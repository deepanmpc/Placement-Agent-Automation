import os
import sys
import tempfile
import json
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger
from typing import List, Optional

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


def attach_ranking(profile: StudentProfile, custom_weights: dict | None = None):
    """
    Computes all scoring modes and attaches them to the profile.ranking field.
    
    Modes:
      dsa_mode    = DSA_SCORE × 0.60 + GITHUB_SCORE × 0.40
      github_mode = GITHUB_SCORE × 0.60 + DSA_SCORE × 0.40
      custom      = (LC×lc_w + CC×cc_w + CF×cf_w + GH×gh_w) / 100
    """
    lc = LeetCodeRanker.calculate(profile.leetcode.model_dump())
    cf = CodeforcesRanker.calculate(profile.codeforces.model_dump())
    cc = CodeChefRanker.calculate(profile.codechef.model_dump())

    # DSA aggregate: LC×0.33 + CC×0.34 + CF×0.33
    dsa = CodingAggregator.calculate(lc, cf, cc)

    # GitHub score
    gh_raw = profile.github.model_dump()
    # Also merge github_strength sub-fields if present
    if profile.github.github_strength:
        gh_raw.update(profile.github.github_strength.model_dump())
    gh = GitHubEngineeringRanker.calculate(gh_raw)

    # All three composite modes
    dsa_mode    = RuleScoreAggregator.calculate_dsa_mode(dsa.total_score, gh.total_score)
    github_mode = RuleScoreAggregator.calculate_github_mode(dsa.total_score, gh.total_score)

    cw = custom_weights or {}
    custom = RuleScoreAggregator.calculate_custom(
        lc_score=lc.total_score, cc_score=cc.total_score,
        cf_score=cf.total_score, github_score=gh.total_score,
        lc_weight=cw.get("lc", 25.0), cc_weight=cw.get("cc", 25.0),
        cf_weight=cw.get("cf", 25.0), gh_weight=cw.get("gh", 25.0),
    )

    profile.ranking = {
        # Individual platform scores
        "lc_score":  round(lc.total_score, 2),
        "cc_score":  round(cc.total_score, 2),
        "cf_score":  round(cf.total_score, 2),
        "dsa_score": round(dsa.total_score, 2),
        "github_score_total": round(gh.total_score, 2),

        # Composite modes
        "overall_dsa_mode":    round(dsa_mode.total_score, 2),
        "overall_github_mode": round(github_mode.total_score, 2),
        "custom_score":        round(custom.total_score, 2),

        # Full breakdowns (for detailed UI)
        "leetcode_score":   lc.to_dict(),
        "codechef_score":   cc.to_dict(),
        "codeforces_score": cf.to_dict(),
        "coding_score":     dsa.to_dict(),
        "github_score":     gh.to_dict(),
        "dsa_mode_breakdown":    dsa_mode.to_dict(),
        "github_mode_breakdown": github_mode.to_dict(),
        "custom_breakdown":      custom.to_dict(),

        # Legacy field kept for backward-compat
        "total_technical_score": round(dsa_mode.total_score, 2),
    }

@app.get("/profiles", response_model=List[StudentProfile])
async def list_profiles(
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    lc_w: Optional[float] = None,
    cc_w: Optional[float] = None,
    cf_w: Optional[float] = None,
    gh_w: Optional[float] = None,
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    service = IngestionService(db_session=db, settings=settings)
    profiles = await service.get_all_profiles(limit=limit, offset=offset)
    
    custom_weights = None
    if lc_w is not None and cc_w is not None and cf_w is not None and gh_w is not None:
        custom_weights = {"lc": lc_w, "cc": cc_w, "cf": cf_w, "gh": gh_w}
    else:
        from backend.database.models import ScoringRule
        from sqlalchemy.future import select
        result = await db.execute(select(ScoringRule).where(ScoringRule.is_active == True))
        active_rule = result.scalars().first()
        if active_rule and "platform_weights" in active_rule.config:
            custom_weights = active_rule.config["platform_weights"]
        
    for p in profiles:
        try:
            attach_ranking(p, custom_weights=custom_weights)
        except Exception as e:
            import traceback
            logger.error(f"attach_ranking failed for {p.student_uuid}: {e}")
    return profiles

@app.get("/profiles/{student_uuid}", response_model=StudentProfile)
async def get_profile(
    student_uuid: str,
    lc_w: Optional[float] = None,
    cc_w: Optional[float] = None,
    cf_w: Optional[float] = None,
    gh_w: Optional[float] = None,
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    service = IngestionService(db_session=db, settings=settings)
    profile = await service.get_profile(student_uuid)
    if not profile:
        raise HTTPException(404, "Profile not found")
        
    custom_weights = None
    if lc_w is not None and cc_w is not None and cf_w is not None and gh_w is not None:
        custom_weights = {"lc": lc_w, "cc": cc_w, "cf": cf_w, "gh": gh_w}
    else:
        from backend.database.models import ScoringRule
        from sqlalchemy.future import select
        result = await db.execute(select(ScoringRule).where(ScoringRule.is_active == True))
        active_rule = result.scalars().first()
        if active_rule and "platform_weights" in active_rule.config:
            custom_weights = active_rule.config["platform_weights"]
        
    try:
        attach_ranking(profile, custom_weights=custom_weights)
    except Exception as e:
        import traceback
        logger.error(f"attach_ranking failed for {student_uuid}: {e}")
        logger.error(traceback.format_exc())
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

    from backend.database.repository import StudentRepository
    repo = StudentRepository(db)
    await repo.save_profile(profile)
    
    return {"status": "success", "message": "Profile updated successfully"}

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
        
        result = await db.execute(select(ExtractionJob).where(ExtractionJob.id == job_id))
        job = result.scalars().first()
        if not job or job.status != "IN_PROGRESS":
            return
            
        target_uuids = job.target_uuids.get("uuids", [])
        completed_uuids = job.completed_uuids.get("uuids", [])
        
        remaining_uuids = [u for u in target_uuids if u not in completed_uuids]
        
        for uuid in remaining_uuids:
            # check if still IN_PROGRESS (could be canceled)
            job_refresh = await db.execute(select(ExtractionJob).where(ExtractionJob.id == job_id))
            job_current = job_refresh.scalars().first()
            if not job_current or job_current.status != "IN_PROGRESS":
                break
                
            try:
                await PlatformSyncService.sync_platforms(db, uuid)
            except Exception as e:
                logger.error(f"Error syncing {uuid}: {e}")
                
            # Update job progress
            completed_uuids.append(uuid)
            job_current.completed_uuids = {"uuids": completed_uuids}
            job_current.completed_count = len(completed_uuids)
            if job_current.completed_count >= job_current.total_count:
                job_current.status = "COMPLETED"
            
            # Commit after each student to save state
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
            existing_job.status = "CANCELED"
            await db.commit()
            # fall through to create a new job
        else:
            if existing_job.status == "PAUSED":
                existing_job.status = "IN_PROGRESS"
                await db.commit()
                background_tasks.add_task(process_extraction_job, existing_job.id)
            return {"job_id": existing_job.id, "status": existing_job.status, "message": "Resumed existing job"}

    if req.student_uuids:
        uuids = req.student_uuids
    else:
        stmt = select(StudentProfileRecord.student_uuid)
        res = await db.execute(stmt)
        uuids = res.scalars().all()
        
    if not uuids:
        return {"message": "No students selected."}
        
    job = ExtractionJob(
        status="IN_PROGRESS",
        total_count=len(uuids),
        completed_count=0,
        target_uuids={"uuids": list(uuids)},
        completed_uuids={"uuids": []}
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)
    
    background_tasks.add_task(process_extraction_job, job.id)
    return {"job_id": job.id, "status": job.status, "message": "Extraction started"}

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
    db: AsyncSession = Depends(get_db)
):
    from backend.collection.service import PlatformSyncService
    from backend.ingestion.models.student_profile import StudentProfile
    
    updated_record = await PlatformSyncService.sync_platforms(db, student_uuid)
    if not updated_record:
        raise HTTPException(404, "Student profile not found")
        
    profile = StudentProfile.model_validate(updated_record.profile_data)
    
    custom_weights = None
    if lc_w is not None and cc_w is not None and cf_w is not None and gh_w is not None:
        custom_weights = {"lc": lc_w, "cc": cc_w, "cf": cf_w, "gh": gh_w}
    else:
        from backend.database.models import ScoringRule
        from sqlalchemy.future import select
        result = await db.execute(select(ScoringRule).where(ScoringRule.is_active == True))
        active_rule = result.scalars().first()
        if active_rule and "platform_weights" in active_rule.config:
            custom_weights = active_rule.config["platform_weights"]
        
    attach_ranking(profile, custom_weights=custom_weights)
        
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
            "platform_weights": {"lc": 25.0, "cc": 25.0, "cf": 25.0, "gh": 25.0},
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
