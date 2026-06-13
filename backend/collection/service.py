import asyncio
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import logging

from backend.database.models import StudentProfileRecord
from backend.ingestion.github_collector.collector import GitHubCollector
from backend.ingestion.leetcode_collector.collector import LeetCodeCollector
from backend.ingestion.codeforces_collector.collector import CodeforcesCollector
from backend.ingestion.codechef_collector.collector import CodeChefCollector
from backend.config import get_settings
from .models import PlatformSyncMetadata

logger = logging.getLogger(__name__)

class PlatformSyncService:
    @staticmethod
    async def sync_platforms(db: AsyncSession, student_uuid: str) -> Optional[StudentProfileRecord]:
        # 1. Fetch the user record from the database
        stmt = select(StudentProfileRecord).where(StudentProfileRecord.student_uuid == student_uuid)
        result = await db.execute(stmt)
        record = result.scalars().first()
        
        if not record:
            logger.error(f"Student with UUID {student_uuid} not found.")
            return None
            
        # 2. Extract usernames
        github_url = record.github_url
        leetcode_username = record.leetcode_username
        codeforces_username = record.codeforces_username
        codechef_username = record.codechef_username
        
        # Initialize collectors
        settings = get_settings()
        github_collector = GitHubCollector(token=settings.github_token if settings and hasattr(settings, 'github_token') else None)
        leetcode_collector = LeetCodeCollector()
        codeforces_collector = CodeforcesCollector()
        codechef_collector = CodeChefCollector()
        
        async def safe_collect(collector, value):
            if not value:
                return None
            return await collector.collect(value)
            
        # 3. Run collectors concurrently
        results = await asyncio.gather(
            safe_collect(github_collector, github_url),
            safe_collect(leetcode_collector, leetcode_username),
            safe_collect(codeforces_collector, codeforces_username),
            safe_collect(codechef_collector, codechef_username),
            return_exceptions=True
        )
        
        github_result, leetcode_result, codeforces_result, codechef_result = results
        
        failed_platforms = []
        today = datetime.utcnow().strftime("%Y-%m-%d")
        
        # Process GitHub
        if isinstance(github_result, Exception):
            logger.error(f"GitHub collection exception: {github_result}")
            failed_platforms.append("github")
        elif github_result is not None:
            old_snapshots = record.github_profile.get("snapshots", []) if record.github_profile else []
            # Prevent duplicate snapshots for the same day
            if not any(s.get("date") == today for s in old_snapshots):
                old_snapshots.append({"date": today, "public_repos": github_result.public_repos, "total_stars": github_result.total_stars})
            github_result.snapshots = old_snapshots
            record.github_profile = github_result.model_dump(mode="json")
            
        # Process LeetCode
        if isinstance(leetcode_result, Exception):
            logger.error(f"LeetCode collection exception: {leetcode_result}")
            failed_platforms.append("leetcode")
        elif leetcode_result is not None:
            old_snapshots = record.leetcode_profile.get("snapshots", []) if record.leetcode_profile else []
            if not any(s.get("date") == today for s in old_snapshots):
                old_snapshots.append({"date": today, "rating": leetcode_result.rating, "total_solved": leetcode_result.total_solved})
            leetcode_result.snapshots = old_snapshots
            record.leetcode_profile = leetcode_result.model_dump(mode="json")
            
        # Process Codeforces
        if isinstance(codeforces_result, Exception):
            logger.error(f"Codeforces collection exception: {codeforces_result}")
            failed_platforms.append("codeforces")
        elif codeforces_result is not None:
            old_snapshots = record.codeforces_profile.get("snapshots", []) if record.codeforces_profile else []
            if not any(s.get("date") == today for s in old_snapshots):
                old_snapshots.append({"date": today, "rating": codeforces_result.rating, "solved_count": codeforces_result.solved_count})
            codeforces_result.snapshots = old_snapshots
            record.codeforces_profile = codeforces_result.model_dump(mode="json")
            
        # Process CodeChef
        if isinstance(codechef_result, Exception):
            logger.error(f"CodeChef collection exception: {codechef_result}")
            failed_platforms.append("codechef")
        elif codechef_result is not None:
            old_snapshots = record.codechef_profile.get("snapshots", []) if record.codechef_profile else []
            if not any(s.get("date") == today for s in old_snapshots):
                old_snapshots.append({"date": today, "rating": codechef_result.rating, "solved_count": codechef_result.solved_count})
            codechef_result.snapshots = old_snapshots
            record.codechef_profile = codechef_result.model_dump(mode="json")
            
        # 4. Update sync metadata
        sync_status = "success" if not failed_platforms else ("partial" if len(failed_platforms) < 4 else "failed")
        
        metadata = PlatformSyncMetadata(
            last_synced_at=datetime.utcnow().isoformat() + "Z",
            sync_status=sync_status,
            failed_platforms=failed_platforms
        )
        record.platform_sync_metadata = metadata.model_dump()
        
        # Update the main profile_data json payload so it reflects in standard GET calls
        profile_data = dict(record.profile_data) if record.profile_data else {}
        if record.github_profile:
            profile_data["github"] = record.github_profile
        if record.leetcode_profile:
            profile_data["leetcode"] = record.leetcode_profile
        if record.codeforces_profile:
            profile_data["codeforces"] = record.codeforces_profile
        if record.codechef_profile:
            profile_data["codechef"] = record.codechef_profile
            
        # Update metadata.sources_collected in profile_data
        meta = profile_data.get("metadata", {})
        sources = set(meta.get("sources_collected", []))
        if record.github_profile: sources.add("github")
        if record.leetcode_profile: sources.add("leetcode")
        if record.codeforces_profile: sources.add("codeforces")
        if record.codechef_profile: sources.add("codechef")
        meta["sources_collected"] = list(sources)
        profile_data["metadata"] = meta
        
        record.profile_data = profile_data
        
        # 5. Commit to database
        await db.commit()
        await db.refresh(record)
        
        return record
