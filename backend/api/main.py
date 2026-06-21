import os
import sys
import tempfile
import json
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger
logger.add("backend.log", rotation="10 MB", retention="10 days", level="INFO")
from typing import List, Optional
from pydantic import BaseModel

# Fix imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.config import get_settings, Settings
from backend.database.connection import get_db, init_db
from backend.ingestion.services import IngestionService
from backend.ingestion.models.student_profile import StudentProfile
from backend.ingestion.qdrant_preparer import QdrantPreparer, QdrantDocument

app = FastAPI(
    title="Placement Agent API",
    description="Student Intelligence Ingestion Layer",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    await init_db()
    logger.info("Database initialized")

# Helper to extract text from file
def extract_text_from_file(file_path: str, ext: str) -> str:
    if ext in (".txt", ".md"):
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    elif ext == ".pdf":
        try:
            import pdfplumber
            text = ""
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    extracted = page.extract_text()
                    if extracted:
                        text += extracted + "\n"
                    if hasattr(page, 'hyperlinks'):
                        for link in page.hyperlinks:
                            if 'uri' in link:
                                text += "\n" + link['uri'] + "\n"
            return text
        except ImportError:
            import pypdf
            reader = pypdf.PdfReader(file_path)
            text = ""
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
                if '/Annots' in page:
                    for annot in page['/Annots']:
                        obj = annot.get_object()
                        if '/A' in obj and '/URI' in obj['/A']:
                            text += "\n" + obj['/A']['/URI'] + "\n"
            return text
    elif ext == ".docx":
        import docx
        doc = docx.Document(file_path)
        return "\n".join([para.text for para in doc.paragraphs])
    return ""

@app.get("/health")
async def health():
    return {"status": "ok", "service": "placement-agent-ingestion"}

@app.post("/ingest", response_model=StudentProfile)
async def ingest_resume(
    file: UploadFile = File(...),
    id_number: Optional[str] = Form(None),
    github_url: Optional[str] = Form(None),
    linkedin_url: Optional[str] = Form(None),
    leetcode_username: Optional[str] = Form(None),
    codeforces_username: Optional[str] = Form(None),
    codechef_username: Optional[str] = Form(None),
    graduation_year: Optional[int] = Form(None),
    name: Optional[str] = Form(None),
    department: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    """Upload a resume and run the full ingestion pipeline."""
    if not file.filename:
        raise HTTPException(400, "No file provided")
    
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in (".pdf", ".docx", ".txt", ".md"):
        raise HTTPException(400, f"Unsupported format: {ext}")
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name
    
    from backend.database.repository import StudentRepository
    repo = StudentRepository(db)
    
    # Duplicate check logic: Primary by ID Number, fallback to filename
    if id_number:
        is_duplicate = await repo.check_duplicate_id_number(id_number)
        if is_duplicate:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
            raise HTTPException(409, f"Duplicate Profile: A candidate with ID '{id_number}' already exists.")
    else:
        is_duplicate = await repo.check_duplicate_filename(file.filename)
        if is_duplicate:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
            raise HTTPException(409, f"Duplicate Profile: A resume named '{file.filename}' has already been uploaded.")
    
    try:
        text = extract_text_from_file(tmp_path, ext)
        if not text.strip():
            raise HTTPException(400, "Could not extract text from file")
        
        service = IngestionService(db_session=db, settings=settings)
        profile = await service.ingest_resume(text, filename=file.filename)
        
        # Override with manual inputs if provided
        if name:
            profile.personal_info.name = name
        if id_number:
            profile.personal_info.id_number = id_number
        if department:
            if profile.education is None:
                from backend.ingestion.models.student_profile import Education
                profile.education = Education()
            profile.education.branch = department
        if github_url:
            profile.personal_info.github_url = github_url
        if linkedin_url:
            profile.personal_info.linkedin_url = linkedin_url
        if leetcode_username:
            profile.personal_info.leetcode_username = leetcode_username
        if codeforces_username:
            profile.personal_info.codeforces_username = codeforces_username
        if codechef_username:
            profile.personal_info.codechef_username = codechef_username
        if graduation_year:
            if profile.education is None:
                from backend.ingestion.models.student_profile import Education
                profile.education = Education()
            profile.education.graduation_year = graduation_year
            
        # Secondary duplicate check in case the LLM extracted an ID that was not provided manually
        if profile.personal_info.id_number:
            is_dup = await repo.check_duplicate_id_number(profile.personal_info.id_number)
            if is_dup:
                raise HTTPException(409, f"Duplicate Profile: A candidate with extracted ID '{profile.personal_info.id_number}' already exists.")
                
        await repo.save_profile(profile)
        
        return profile
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Ingestion failed")
        raise HTTPException(500, f"Ingestion failed: {str(e)}")
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

from backend.ranking.weighted_ranker.coding_ranker.leetcode_score import LeetCodeRanker
from backend.ranking.weighted_ranker.coding_ranker.codeforces_score import CodeforcesRanker
from backend.ranking.weighted_ranker.coding_ranker.codechef_score import CodeChefRanker
from backend.ranking.weighted_ranker.coding_ranker.coding_aggregator import CodingAggregator
from backend.ranking.weighted_ranker.github_ranker.github_engineering import GitHubEngineeringRanker
from backend.ranking.weighted_ranker.rule_score import RuleScoreAggregator


def attach_ranking(profile: StudentProfile, custom_weights: dict = None, job_description: str = None):
    """
    Computes all scoring modes and attaches them to the profile.ranking field.
    
    Modes:
      dsa_mode    = DSA_SCORE × 0.60 + GITHUB_SCORE × 0.40
      github_mode = GITHUB_SCORE × 0.60 + DSA_SCORE × 0.40
      custom      = (LC×lc_w + CC×cc_w + CF×cf_w + GH×gh_w) / 100
      fitment     = Rule-based (DSA) × 0.4 + Behavioral (GH) × 0.2 + Semantic × 0.4
    """
    from backend.ranking.weighted_ranker.semantic_ranker import SemanticRanker
    from backend.ranking.weighted_ranker.common import ExplainableScore
    
    try:
        lc_data = profile.leetcode.model_dump() if profile.leetcode else {}
        cf_data = profile.codeforces.model_dump() if profile.codeforces else {}
        cc_data = profile.codechef.model_dump() if profile.codechef else {}
    
        lc = LeetCodeRanker.calculate(lc_data)
        cf = CodeforcesRanker.calculate(cf_data)
        cc = CodeChefRanker.calculate(cc_data)
    
        # DSA aggregate: LC×0.33 + CC×0.34 + CF×0.33
        dsa = CodingAggregator.calculate(lc, cf, cc)
    
        # GitHub score
        gh_raw = profile.github.model_dump() if profile.github else {}
        # Also merge github_strength sub-fields if present
        if getattr(profile, 'github', None) and getattr(profile.github, 'github_strength', None):
            gh_raw.update(profile.github.github_strength.model_dump())
        gh = GitHubEngineeringRanker.calculate(gh_raw)
    
        # All three composite modes
        dsa_mode    = RuleScoreAggregator.calculate_dsa_mode(dsa.total_score, gh.total_score)
        github_mode = RuleScoreAggregator.calculate_github_mode(dsa.total_score, gh.total_score)
    
        # Semantic Fitment (3-Pillar Score)
        semantic_score_obj = None
        if job_description:
            semantic_score_obj = SemanticRanker.calculate_fitment(profile, job_description)
            # Semantic Mode: DSA 35% + GitHub 40% + Semantic 25%
            fitment_blend = RuleScoreAggregator.calculate_fitment_blend(
                platform_score=dsa.total_score,
                behavioral_score=gh.total_score,
                semantic_score=semantic_score_obj.total_score,
                w_platform=0.35,
                w_behavioral=0.40,
                w_semantic=0.25
            )
        else:
            fitment_blend = ExplainableScore(0.0, {"error": "No JD provided"})

        cw = custom_weights or {}
        custom = RuleScoreAggregator.calculate_custom(
            lc_score=lc.total_score, cc_score=cc.total_score,
            cf_score=cf.total_score, github_score=gh.total_score,
            semantic_score=semantic_score_obj.total_score if semantic_score_obj else 0.0,
            lc_weight=cw.get("lc", 20.0), cc_weight=cw.get("cc", 20.0),
            cf_weight=cw.get("cf", 20.0), gh_weight=cw.get("gh", 20.0), sm_weight=cw.get("sm", 20.0)
        )
            
        missing_platforms = profile.metadata.missing_platforms if profile.metadata and getattr(profile.metadata, 'missing_platforms', None) else []
    
        profile.ranking = {
            # Individual platform scores
            "lc_score":  round(lc.total_score, 2),
            "cc_score":  round(cc.total_score, 2),
            "cf_score":  round(cf.total_score, 2),
            "dsa_score": round(dsa.total_score, 2),
            "github_score_total": round(gh.total_score, 2),
            "semantic_score": round(semantic_score_obj.total_score, 2) if semantic_score_obj else 0.0,
    
            # Composite modes
            "overall_dsa_mode":    round(dsa_mode.total_score, 2),
            "overall_github_mode": round(github_mode.total_score, 2),
            "custom_score":        round(custom.total_score, 2),
            "fitment_score":       round(fitment_blend.total_score, 2),
    
            # Full breakdowns (for detailed UI)
            "leetcode_score":   lc.to_dict(),
            "codechef_score":   cc.to_dict(),
            "codeforces_score": cf.to_dict(),
            "coding_score":     dsa.to_dict(),
            "github_score":     gh.to_dict(),
            "dsa_mode_breakdown":    dsa_mode.to_dict(),
            "github_mode_breakdown": github_mode.to_dict(),
            "custom_breakdown":      custom.to_dict(),
            "semantic_breakdown":    semantic_score_obj.to_dict() if semantic_score_obj else {},
            "fitment_breakdown":     fitment_blend.to_dict(),
    
            # Legacy field kept for backward-compat
            "total_technical_score": round(dsa_mode.total_score, 2),
            "missing_platforms": missing_platforms
        }
    except Exception as e:
        import logging
        logging.error(f"Error in attach_ranking: {e}")
        profile.ranking = {"error": str(e), "missing_platforms": getattr(profile.metadata, 'missing_platforms', []) if getattr(profile, 'metadata', None) else []}


@app.get("/profiles", response_model=List[StudentProfile])
async def list_profiles(
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    lc_w: Optional[float] = None,
    cc_w: Optional[float] = None,
    cf_w: Optional[float] = None,
    gh_w: Optional[float] = None,
    sm_w: Optional[float] = None,
    job_description: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    service = IngestionService(db_session=db, settings=settings)
    profiles = await service.get_all_profiles(limit=limit, offset=offset)
    
    custom_weights = None
    if lc_w is not None and cc_w is not None and cf_w is not None and gh_w is not None and sm_w is not None:
        custom_weights = {"lc": lc_w, "cc": cc_w, "cf": cf_w, "gh": gh_w, "sm": sm_w}
    else:
        from backend.database.models import ScoringRule
        from sqlalchemy.future import select
        result = await db.execute(select(ScoringRule).where(ScoringRule.is_active == True))
        active_rule = result.scalars().first()
        if active_rule and "platform_weights" in active_rule.config:
            custom_weights = active_rule.config["platform_weights"]
        
    for p in profiles:
        try:
            attach_ranking(p, custom_weights=custom_weights, job_description=job_description)
        except Exception as e:
            import traceback
            logger.error(f"attach_ranking failed for {p.student_uuid}:\n{traceback.format_exc()}")
            p.ranking = {"error": f"Ranking calculation failed: {str(e)}"}
    return profiles

@app.get("/profiles/{student_uuid}", response_model=StudentProfile)
async def get_profile(
    student_uuid: str,
    lc_w: Optional[float] = None,
    cc_w: Optional[float] = None,
    cf_w: Optional[float] = None,
    gh_w: Optional[float] = None,
    sm_w: Optional[float] = None,
    job_description: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    service = IngestionService(db_session=db, settings=settings)
    profile = await service.get_profile(student_uuid)
    if not profile:
        raise HTTPException(404, "Profile not found")
        
    custom_weights = None
    if lc_w is not None and cc_w is not None and cf_w is not None and gh_w is not None and sm_w is not None:
        custom_weights = {"lc": lc_w, "cc": cc_w, "cf": cf_w, "gh": gh_w, "sm": sm_w}
    else:
        from backend.database.models import ScoringRule
        from sqlalchemy.future import select
        result = await db.execute(select(ScoringRule).where(ScoringRule.is_active == True))
        active_rule = result.scalars().first()
        if active_rule and "platform_weights" in active_rule.config:
            custom_weights = active_rule.config["platform_weights"]
        
    try:
        attach_ranking(profile, custom_weights=custom_weights, job_description=job_description)
    except Exception as e:
        import traceback
        logger.error(f"attach_ranking failed for {student_uuid}:\n{traceback.format_exc()}")
        profile.ranking = {"error": f"Ranking calculation failed: {str(e)}"}
    return profile

class ProfileUpdateRequest(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    id_number: Optional[str] = None
    github_url: Optional[str] = None
    leetcode_username: Optional[str] = None
    codeforces_username: Optional[str] = None
    codechef_username: Optional[str] = None
    graduation_year: Optional[int] = None

@app.put("/profiles/{student_uuid}")
async def update_profile(
    student_uuid: str,
    req: ProfileUpdateRequest,
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    service = IngestionService(db_session=db, settings=settings)
    profile = await service.get_profile(student_uuid)
    if not profile:
        raise HTTPException(404, "Profile not found")
        
    # Update fields
    if req.name is not None: profile.personal_info.name = req.name
    if req.email is not None: profile.personal_info.email = req.email
    if req.phone is not None: profile.personal_info.phone = req.phone
    if req.id_number is not None: profile.personal_info.id_number = req.id_number
    if req.github_url is not None: profile.personal_info.github_url = req.github_url
    if req.leetcode_username is not None: profile.personal_info.leetcode_username = req.leetcode_username
    if req.codeforces_username is not None: profile.personal_info.codeforces_username = req.codeforces_username
    if req.codechef_username is not None: profile.personal_info.codechef_username = req.codechef_username
    if req.graduation_year is not None:
        if not profile.education:
            from backend.ingestion.models.student_profile import Education
            profile.education = Education()
        profile.education.graduation_year = req.graduation_year

    from backend.database.repository import StudentRepository
    repo = StudentRepository(db)
    await repo.save_profile(profile)
    
    return {"status": "success", "message": "Profile updated successfully"}


@app.get("/analytics")
async def get_analytics(
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    service = IngestionService(db_session=db, settings=settings)
    profiles = await service.get_all_profiles(limit=10000, offset=0)
    
    total_students = len(profiles)
    
    platform_counts = {"github": 0, "leetcode": 0, "codeforces": 0, "codechef": 0}
    skills_counter = {}
    branch_counts = {}
    batch_counts = {}
    
    total_cgpa = 0
    cgpa_count = 0
    
    total_lc_rating = 0
    lc_count = 0
    total_cf_rating = 0
    cf_count = 0
    total_cc_rating = 0
    cc_count = 0
    
    # We will compute base coding scores (DSA mode) without JD to get a distribution
    from backend.ranking.weighted_ranker.coding_ranker.leetcode_score import LeetCodeRanker
    from backend.ranking.weighted_ranker.coding_ranker.codeforces_score import CodeforcesRanker
    from backend.ranking.weighted_ranker.coding_ranker.codechef_score import CodeChefRanker
    from backend.ranking.weighted_ranker.coding_ranker.aggregator import CodingAggregator
    from backend.ranking.weighted_ranker.behavioral_ranker.github_score import GitHubEngineeringRanker
    from backend.ranking.weighted_ranker.rule_aggregator import RuleScoreAggregator
    
    top_candidates = []
    
    for p in profiles:
        # Platform counts
        if p.github and p.github.github_url: platform_counts["github"] += 1
        if p.leetcode and p.leetcode.leetcode_username: platform_counts["leetcode"] += 1
        if p.codeforces and p.codeforces.codeforces_username: platform_counts["codeforces"] += 1
        if p.codechef and p.codechef.codechef_username: platform_counts["codechef"] += 1
        
        # CGPA
        if p.education and p.education.cgpa is not None:
            total_cgpa += p.education.cgpa
            cgpa_count += 1
            
        # Ratings
        if p.leetcode and getattr(p.leetcode, 'contest_rating', None):
            total_lc_rating += p.leetcode.contest_rating
            lc_count += 1
        if p.codeforces and getattr(p.codeforces, 'rating', None):
            total_cf_rating += p.codeforces.rating
            cf_count += 1
        if p.codechef and getattr(p.codechef, 'rating', None):
            total_cc_rating += p.codechef.rating
            cc_count += 1
            
        # Skills
        if p.skills and p.skills.languages:
            for s in p.skills.languages:
                skills_counter[s] = skills_counter.get(s, 0) + 1
        if p.skills and p.skills.frameworks:
            for s in p.skills.frameworks:
                skills_counter[s] = skills_counter.get(s, 0) + 1
                
        # Branch
        if p.education and p.education.degree:
            b = p.education.degree.upper()
            branch_counts[b] = branch_counts.get(b, 0) + 1
            
        # Batch
        if p.education and p.education.graduation_year:
            y = str(p.education.graduation_year)
            batch_counts[y] = batch_counts.get(y, 0) + 1
            
        # Base Score Calculation
        lc_data = p.leetcode.model_dump() if p.leetcode else {}
        cf_data = p.codeforces.model_dump() if p.codeforces else {}
        cc_data = p.codechef.model_dump() if p.codechef else {}
        lc = LeetCodeRanker.calculate(lc_data)
        cf = CodeforcesRanker.calculate(cf_data)
        cc = CodeChefRanker.calculate(cc_data)
        dsa = CodingAggregator.calculate(lc, cf, cc)
        
        gh_raw = p.github.model_dump() if p.github else {}
        if getattr(p, 'github', None) and getattr(p.github, 'github_strength', None):
            gh_raw.update(p.github.github_strength.model_dump())
        gh = GitHubEngineeringRanker.calculate(gh_raw)
        
        dsa_mode = RuleScoreAggregator.calculate_dsa_mode(dsa.total_score, gh.total_score)
        score = dsa_mode.total_score
        
        top_candidates.append({
            "uuid": p.student_uuid,
            "name": p.personal_info.name if p.personal_info else "Unknown",
            "score": round(score, 2),
            "cgpa": p.education.cgpa if p.education else None
        })
        
    top_candidates = sorted(top_candidates, key=lambda x: x["score"], reverse=True)[:10]
    
    top_skills = [{"name": k, "value": v} for k, v in sorted(skills_counter.items(), key=lambda item: item[1], reverse=True)[:15]]
    branch_distribution = [{"name": k, "value": v} for k, v in branch_counts.items()]
    batch_distribution = [{"name": k, "value": v} for k, v in batch_counts.items()]
    
    platform_engagement = [
        {"name": "GitHub", "value": platform_counts["github"]},
        {"name": "LeetCode", "value": platform_counts["leetcode"]},
        {"name": "Codeforces", "value": platform_counts["codeforces"]},
        {"name": "CodeChef", "value": platform_counts["codechef"]},
    ]
    
    avg_cgpa = round(total_cgpa / cgpa_count, 2) if cgpa_count > 0 else 0
    avg_lc = round(total_lc_rating / lc_count, 0) if lc_count > 0 else 0
    avg_cf = round(total_cf_rating / cf_count, 0) if cf_count > 0 else 0
    avg_cc = round(total_cc_rating / cc_count, 0) if cc_count > 0 else 0
    
    return {
        "overview": {
            "total_students": total_students,
            "average_cgpa": avg_cgpa,
            "avg_lc_rating": avg_lc,
            "avg_cf_rating": avg_cf,
            "avg_cc_rating": avg_cc
        },
        "platform_engagement": platform_engagement,
        "top_skills": top_skills,
        "branch_distribution": branch_distribution,
        "batch_distribution": batch_distribution,
        "top_candidates": top_candidates
    }

@app.post("/profiles/{student_uuid}/resume")
async def update_profile_resume(
    student_uuid: str,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    if not file.filename:
        raise HTTPException(400, "No file provided")
    
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in (".pdf", ".docx", ".txt", ".md"):
        raise HTTPException(400, f"Unsupported format: {ext}")
        
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        file_content = await file.read()
        tmp.write(file_content)
        tmp_path = tmp.name
        
    try:
        text = extract_text_from_file(tmp_path, ext)
        if not text.strip():
            raise HTTPException(400, "Could not extract text from file")
            
        service = IngestionService(db_session=db, settings=settings)
        profile = await service.get_profile(student_uuid)
        if not profile:
            raise HTTPException(404, "Profile not found")
            
        from backend.ingestion.resume_parser.resume_extractor import ResumeExtractor, ResumeData
        extractor = ResumeExtractor()
        resume_json = extractor.extract(text)
        resume_data = ResumeData.model_validate_json(resume_json)
        
        # Merge the new resume data into the existing profile
        merged_profile = service.merger.merge_resume_data(resume_data)
        
        # Preserve old graduation year if not found in new resume
        old_grad_year = profile.education.graduation_year if profile.education else None
        
        # We only want to override education, skills, projects, and metadata.resume_file
        # We KEEP the personal_info, leetcode, github, codeforces, codechef data intact
        profile.education = merged_profile.education
        profile.skills = merged_profile.skills
        profile.projects = merged_profile.projects
        
        # Restore old graduation year unconditionally if it existed
        if old_grad_year:
            if not profile.education:
                from backend.ingestion.models.student_profile import Education
                profile.education = Education()
            profile.education.graduation_year = old_grad_year
        
        # Also if the user hasn't set their personal info fields manually, we might want to update them
        if not profile.personal_info.phone and merged_profile.personal_info.phone:
            profile.personal_info.phone = merged_profile.personal_info.phone
        if not profile.personal_info.email and merged_profile.personal_info.email:
            profile.personal_info.email = merged_profile.personal_info.email
        if not profile.personal_info.portfolio_url and merged_profile.personal_info.portfolio_url:
            profile.personal_info.portfolio_url = merged_profile.personal_info.portfolio_url
            
        profile.metadata.resume_file = file.filename
        
        from backend.database.repository import StudentRepository
        repo = StudentRepository(db)
        await repo.save_profile(profile)
        
        return {"status": "success", "message": "Resume updated successfully"}
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


@app.delete("/profiles/{student_uuid}")
async def delete_profile(
    student_uuid: str,
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    service = IngestionService(db_session=db, settings=settings)
    deleted = await service.delete_profile(student_uuid)
    if not deleted:
        raise HTTPException(404, "Profile not found")
    return {"status": "deleted", "student_uuid": student_uuid}

from pydantic import BaseModel
class BatchEnrichRequest(BaseModel):
    student_uuids: Optional[List[str]] = None
    batch_size: int = 10
    reset: bool = False

from fastapi import BackgroundTasks
from backend.database.connection import async_session_factory
from backend.database.models import ExtractionJob
import asyncio

async def process_extraction_job(job_id: int):
    async with async_session_factory() as db:
        from sqlalchemy.future import select
        from backend.collection.service import PlatformSyncService
        from backend.database.models import StudentProfileRecord
        
        result = await db.execute(select(ExtractionJob).where(ExtractionJob.id == job_id))
        job = result.scalars().first()
        if not job or job.status != "IN_PROGRESS":
            return
            
        target_uuids = job.target_uuids.get("uuids", [])
        completed_uuids = job.completed_uuids.get("uuids", [])
        
        remaining_uuids = [u for u in target_uuids if u not in completed_uuids]
        
        from sqlalchemy.orm.attributes import flag_modified
        
        for uuid in remaining_uuids:
            # check if still IN_PROGRESS (could be canceled)
            job_refresh = await db.execute(select(ExtractionJob).where(ExtractionJob.id == job_id))
            job_current = job_refresh.scalars().first()
            if not job_current or job_current.status != "IN_PROGRESS":
                break
                
            try:
                await PlatformSyncService.sync_platforms(db, uuid)
                rec_res = await db.execute(select(StudentProfileRecord).where(StudentProfileRecord.student_uuid == uuid))
                rec = rec_res.scalars().first()
                if rec and rec.platform_sync_metadata and rec.platform_sync_metadata.get("sync_status") == "completed":
                    if uuid not in completed_uuids:
                        completed_uuids.append(uuid)
            except Exception as e:
                logger.error(f"Error syncing {uuid}: {e}")
            
            job_current.completed_uuids = {"uuids": list(completed_uuids)}
            flag_modified(job_current, "completed_uuids")
            
            job_current.completed_count += 1
            await db.commit()
            
        # After processing all targeted uuids, if job wasn't paused/canceled, mark it completed
        job_refresh = await db.execute(select(ExtractionJob).where(ExtractionJob.id == job_id))
        job_final = job_refresh.scalars().first()
        if job_final and job_final.status == "IN_PROGRESS":
            job_final.status = "COMPLETED"
            await db.commit()

@app.post("/profiles/batch-enrich")
async def batch_enrich(
    req: BatchEnrichRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    """Creates an ExtractionJob and starts background processing."""
    from backend.database.models import StudentProfileRecord
    from sqlalchemy.future import select
    
    # Check if there's an active or paused job
    result = await db.execute(select(ExtractionJob).where(ExtractionJob.status.in_(["IN_PROGRESS", "PAUSED"])))
    existing_job = result.scalars().first()
    
    if existing_job:
        if req.reset:
            # Delete all old jobs to prevent flooding the database
            from sqlalchemy import delete
            await db.execute(delete(ExtractionJob))
            await db.commit()
            # fall through to create a new job
        else:
            if existing_job.status == "PAUSED":
                existing_job.status = "IN_PROGRESS"
                await db.commit()
                background_tasks.add_task(process_extraction_job, existing_job.id)
            return {
                "job_id": existing_job.id, 
                "status": existing_job.status, 
                "message": "Resumed existing job",
                "total": existing_job.total_count,
                "completed": existing_job.completed_count
            }
    else:
        # If there's no active job and we are starting fresh, clean up any old COMPLETED jobs
        from sqlalchemy import delete
        await db.execute(delete(ExtractionJob))
        await db.commit()

    if req.student_uuids:
        uuids = req.student_uuids
    else:
        stmt = select(StudentProfileRecord.student_uuid)
        res = await db.execute(stmt)
        uuids = res.scalars().all()
        
    if not uuids:
        return {"message": "No students selected."}

    # Smart Resume logic: pre-calculate which students have already been synced
    completed_uuids_list = []
    if not req.reset:
        stmt = select(StudentProfileRecord).where(
            StudentProfileRecord.student_uuid.in_(uuids)
        )
        res = await db.execute(stmt)
        for r in res.scalars().all():
            meta = r.platform_sync_metadata
            if meta and meta.get("sync_status") == "completed":
                completed_uuids_list.append(r.student_uuid)
    job = ExtractionJob(
        status="IN_PROGRESS",
        total_count=len(uuids),
        completed_count=len(completed_uuids_list),
        target_uuids={"uuids": list(uuids)},
        completed_uuids={"uuids": list(completed_uuids_list)}
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)
    
    background_tasks.add_task(process_extraction_job, job.id)
    return {
        "job_id": job.id, 
        "status": job.status, 
        "message": "Extraction started",
        "total": job.total_count,
        "completed": job.completed_count
    }

@app.get("/profiles/extraction-job/status")
async def get_extraction_status(db: AsyncSession = Depends(get_db)):
    from sqlalchemy.future import select
    result = await db.execute(select(ExtractionJob).order_by(ExtractionJob.id.desc()).limit(1))
    job = result.scalars().first()
    if not job:
        return {"active": False}
        
    estimated_seconds = (job.total_count - job.completed_count) * 2.5
        
    return {
        "active": job.status == "IN_PROGRESS",
        "job_id": job.id,
        "status": job.status,
        "total": job.total_count,
        "completed": job.completed_count,
        "estimated_seconds": estimated_seconds
    }

@app.post("/profiles/extraction-job/cancel")
async def cancel_extraction_job(db: AsyncSession = Depends(get_db)):
    from sqlalchemy.future import select
    result = await db.execute(select(ExtractionJob).where(ExtractionJob.status == "IN_PROGRESS"))
    jobs = result.scalars().all()
    for job in jobs:
        job.status = "PAUSED"
    await db.commit()
    return {"status": "PAUSED", "message": "All active jobs paused"}

@app.post("/profiles/{student_uuid}/enrich", response_model=StudentProfile)
async def enrich_profile(
    student_uuid: str,
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    """Enrich a single profile with external coding and github data."""
    service = IngestionService(db_session=db, settings=settings)
    profile = await service.enrich_single_profile(student_uuid)
    if not profile:
        raise HTTPException(404, "Profile not found")
    return profile

@app.get("/profiles/{student_uuid}/qdrant-docs", response_model=List[QdrantDocument])
async def get_qdrant_docs(
    student_uuid: str,
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    """Get the prepared Qdrant documents for a student."""
    service = IngestionService(db_session=db, settings=settings)
    profile = await service.get_profile(student_uuid)
    if not profile:
        raise HTTPException(404, "Profile not found")
    preparer = QdrantPreparer()
    return preparer.prepare(profile)

@app.post("/candidates/{student_uuid}/sync-platforms")
async def sync_platforms(
    student_uuid: str,
    lc_w: Optional[float] = None,
    cc_w: Optional[float] = None,
    cf_w: Optional[float] = None,
    gh_w: Optional[float] = None,
    sm_w: Optional[float] = None,
    job_description: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    from backend.collection.service import PlatformSyncService
    from backend.ingestion.models.student_profile import StudentProfile
    
    updated_record = await PlatformSyncService.sync_platforms(db, student_uuid)
    if not updated_record:
        raise HTTPException(404, "Student profile not found")
        
    profile = StudentProfile.model_validate(updated_record.profile_data)
    
    custom_weights = None
    if lc_w is not None and cc_w is not None and cf_w is not None and gh_w is not None and sm_w is not None:
        custom_weights = {"lc": lc_w, "cc": cc_w, "cf": cf_w, "gh": gh_w, "sm": sm_w}
    else:
        from backend.database.models import ScoringRule
        from sqlalchemy.future import select
        result = await db.execute(select(ScoringRule).where(ScoringRule.is_active == True))
        active_rule = result.scalars().first()
        if active_rule and "platform_weights" in active_rule.config:
            custom_weights = active_rule.config["platform_weights"]
        
    attach_ranking(profile, custom_weights=custom_weights, job_description=job_description)
        
    return {
        "status": "success",
        "github_profile": updated_record.github_profile,
        "leetcode_profile": updated_record.leetcode_profile,
        "codeforces_profile": updated_record.codeforces_profile,
        "codechef_profile": updated_record.codechef_profile,
        "platform_sync_metadata": updated_record.platform_sync_metadata,
        "ranking": profile.ranking
    }

from pydantic import BaseModel
from sqlalchemy.future import select

class ScoringRuleCreate(BaseModel):
    name: str
    is_active: bool = False
    config: dict

@app.get("/scoring-rules")
async def get_scoring_rules(db: AsyncSession = Depends(get_db)):
    from backend.database.models import ScoringRule
    result = await db.execute(select(ScoringRule).order_by(ScoringRule.id.desc()))
    rules = result.scalars().all()
    if not rules:
        # Default config if db is empty
        default_config = {
            "platform_weights": {"lc": 20.0, "cc": 20.0, "cf": 20.0, "gh": 20.0, "sm": 20.0},
            "leetcode": {"rating_divisor": 3000, "rating_weight": 60, "contest_divisor": 2500, "contest_weight": 25, "active_days_divisor": 90, "active_days_weight": 10},
            "codechef": {"rating_divisor": 3000, "rating_weight": 30, "highest_rating_divisor": 3000, "highest_rating_weight": 0, "solved_divisor": 1000, "solved_weight": 15, "contest_divisor": 50, "contest_weight": 10},
            "codeforces": {"rating_divisor": 3500, "rating_weight": 50, "max_rating_divisor": 3500, "max_rating_weight": 20, "solved_divisor": 3000, "solved_weight": 15, "contest_divisor": 100, "contest_weight": 10},
            "github": {
                "orig_repos_divisor": 30, "orig_repos_weight": 10,
                "project_depth_divisor": 50, "project_depth_weight": 10,
                "momentum_divisor": 30, "momentum_weight": 15,
                "stars_divisor": 30, "stars_weight": 3,
                "commits_divisor": 1500, "commits_weight": 15,
                "contrib_days_divisor": 365, "contrib_days_weight": 21,
                "merged_pr_divisor": 15, "merged_pr_weight": 10,
                "issues_divisor": 20, "issues_weight": 5,
                "active90_divisor": 90, "active90_weight": 11
            }
        }
        return {"id": 0, "name": "Default Configuration", "is_active": True, "config": default_config}
    active_rule = next((r for r in rules if r.is_active), rules[0])
    return {
        "id": active_rule.id,
        "name": active_rule.name,
        "is_active": active_rule.is_active,
        "config": active_rule.config
    }

@app.post("/scoring-rules")
async def save_scoring_rule(rule: ScoringRuleCreate, db: AsyncSession = Depends(get_db)):
    from backend.database.models import ScoringRule
    from sqlalchemy import update
    
    if rule.is_active:
        await db.execute(update(ScoringRule).values(is_active=False))
        
    new_rule = ScoringRule(
        name=rule.name,
        is_active=rule.is_active,
        config=rule.config
    )
    db.add(new_rule)
    await db.commit()
    await db.refresh(new_rule)
    
    return {"status": "success", "id": new_rule.id}
