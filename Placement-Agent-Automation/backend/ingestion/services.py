import asyncio
from typing import Optional, List
from loguru import logger

from backend.ingestion.resume_parser.resume_extractor import ResumeExtractor, ResumeData
from backend.ingestion.models.student_profile import StudentProfile
from backend.database.repository import StudentRepository
from backend.ingestion.profile_merger import ProfileMerger
from backend.ingestion.qdrant_preparer import QdrantPreparer
from backend.ingestion.github_collector.collector import GitHubCollector
from backend.ingestion.leetcode_collector.collector import LeetCodeCollector
from backend.ingestion.codeforces_collector.collector import CodeforcesCollector
from backend.ingestion.codechef_collector.collector import CodeChefCollector

class IngestionService:
    """Orchestrates the full student profile ingestion pipeline."""
    
    def __init__(self, db_session, settings=None):
        self.repository = StudentRepository(db_session)
        self.merger = ProfileMerger()
        self.qdrant_preparer = QdrantPreparer()
        self.github_collector = GitHubCollector(token=settings.github_token if settings and hasattr(settings, 'github_token') else None)
        self.leetcode_collector = LeetCodeCollector()
        self.codeforces_collector = CodeforcesCollector()
        self.codechef_collector = CodeChefCollector()
    
    async def ingest_resume(self, resume_text: str, filename: str = "") -> StudentProfile:
        """Full ingestion pipeline:
        1. Extract resume data
        2. Create base profile
        3. Collect from all platforms concurrently
        4. Merge all data
        5. Prepare Qdrant documents
        6. Save to database
        7. Return complete profile
        """
        # Step 1: Extract resume
        extractor = ResumeExtractor()
        resume_json = extractor.extract(resume_text)
        resume_data = ResumeData.model_validate_json(resume_json)
        
        # Step 2: Create base profile from resume
        profile = self.merger.merge_resume_data(resume_data)
        profile.metadata.resume_file = filename
        
        # Step 3 & 4 (Skipped): We no longer collect from platforms immediately.
        # It will be done later via the batch-enrich endpoint.
        
        # Step 5: Prepare Qdrant docs (stored in profile for now)
        qdrant_docs = self.qdrant_preparer.prepare(profile)
        logger.info(f"Prepared {len(qdrant_docs)} Qdrant documents for student {profile.student_uuid}")
        
        # Step 6: Save to DB
        try:
            saved_uuid = await self.repository.save_profile(profile)
            logger.info(f"Saved profile {saved_uuid} to database")
        except Exception as e:
            logger.error(f"Failed to save profile to database: {e}")
            profile.metadata.errors.append(f"db_save: {str(e)}")
        
        return profile
    
    async def get_profile(self, student_uuid: str) -> Optional[StudentProfile]:
        return await self.repository.get_profile(student_uuid)
    
    async def get_all_profiles(self, limit: int = 100, offset: int = 0) -> List[StudentProfile]:
        return await self.repository.get_all_profiles(limit=limit, offset=offset)
    
    async def delete_profile(self, student_uuid: str) -> bool:
        return await self.repository.delete_profile(student_uuid)

    async def batch_enrich_profiles(self, batch_size: int = 10) -> dict:
        """Fetch up to `batch_size` profiles, extract coding/github data, and update them."""
        profiles = await self.get_all_profiles(limit=batch_size)
        enriched_count = 0
        errors = []
        
        for profile in profiles:
            try:
                collector_tasks = {}
                if profile.personal_info.github_url:
                    collector_tasks['github'] = self.github_collector.collect(profile.personal_info.github_url)
                if profile.personal_info.leetcode_username:
                    collector_tasks['leetcode'] = self.leetcode_collector.collect(profile.personal_info.leetcode_username)
                if profile.personal_info.codeforces_username:
                    collector_tasks['codeforces'] = self.codeforces_collector.collect(profile.personal_info.codeforces_username)
                if profile.personal_info.codechef_username:
                    collector_tasks['codechef'] = self.codechef_collector.collect(profile.personal_info.codechef_username)
                
                if collector_tasks:
                    results = await asyncio.gather(*collector_tasks.values(), return_exceptions=True)
                    github_data = None
                    leetcode_data = None
                    codeforces_data = None
                    codechef_data = None
                    
                    for key, result in zip(collector_tasks.keys(), results):
                        if isinstance(result, Exception):
                            logger.error(f"Batch collector {key} failed for {profile.student_uuid}: {result}")
                            profile.metadata.errors.append(f"{key}: {str(result)}")
                        else:
                            if key == 'github': github_data = result
                            elif key == 'leetcode': leetcode_data = result
                            elif key == 'codeforces': codeforces_data = result
                            elif key == 'codechef': codechef_data = result
                    
                    # Merge data
                    profile = self.merger.merge_all(
                        profile,
                        github=github_data,
                        leetcode=leetcode_data,
                        codeforces=codeforces_data,
                        codechef=codechef_data
                    )
                    
                    # Save back to DB
                    await self.repository.save_profile(profile)
                    enriched_count += 1
            except Exception as e:
                logger.error(f"Failed to enrich profile {profile.student_uuid}: {e}")
                errors.append(str(e))
                
        return {"enriched": enriched_count, "errors": errors}
