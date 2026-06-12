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
        if id_number:
            profile.personal_info.id_number = id_number
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

def attach_ranking(profile: StudentProfile):
    lc = LeetCodeRanker.calculate(profile.leetcode.model_dump())
    cf = CodeforcesRanker.calculate(profile.codeforces.model_dump())
    cc = CodeChefRanker.calculate(profile.codechef.model_dump())
    coding = CodingAggregator.calculate(lc, cf, cc)
    
    gh_data = profile.github.github_strength.model_dump() if profile.github.github_strength else {}
    gh = GitHubEngineeringRanker.calculate(gh_data)
    
    profile.ranking = {
        "leetcode_score": lc.to_dict(),
        "codeforces_score": cf.to_dict(),
        "codechef_score": cc.to_dict(),
        "coding_score": coding.to_dict(),
        "github_score": gh.to_dict(),
        "total_technical_score": round(coding.total_score * 0.6 + gh.total_score * 0.4, 2)
    }

@app.get("/profiles", response_model=List[StudentProfile])
async def list_profiles(
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    service = IngestionService(db_session=db, settings=settings)
    profiles = await service.get_all_profiles(limit=limit, offset=offset)
    for p in profiles:
        try:
            attach_ranking(p)
        except Exception as e:
            import traceback
            with open("ranking_error.txt", "w") as f:
                f.write(traceback.format_exc())
            logger.error(f"attach_ranking failed for {p.student_uuid}: {e}")
    return profiles

@app.get("/profiles/{student_uuid}", response_model=StudentProfile)
async def get_profile(
    student_uuid: str,
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    service = IngestionService(db_session=db, settings=settings)
    profile = await service.get_profile(student_uuid)
    if not profile:
        raise HTTPException(404, "Profile not found")
    attach_ranking(profile)
    return profile

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

@app.post("/profiles/batch-enrich")
async def batch_enrich(
    req: BatchEnrichRequest,
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    """Enrich specific profiles or up to `batch_size` profiles using PlatformSyncService."""
    from backend.database.models import StudentProfileRecord
    from sqlalchemy.future import select
    from backend.collection.service import PlatformSyncService
    
    if req.student_uuids:
        stmt = select(StudentProfileRecord).where(StudentProfileRecord.student_uuid.in_(req.student_uuids))
    else:
        stmt = select(StudentProfileRecord).limit(req.batch_size)
        
    result = await db.execute(stmt)
    records = result.scalars().all()
    
    success_count = 0
    errors = []
    
    for record in records:
        try:
            res = await PlatformSyncService.sync_platforms(db, record.student_uuid)
            if res:
                success_count += 1
        except Exception as e:
            errors.append(str(e))
            
    return {"enriched": success_count, "errors": errors}

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
    db: AsyncSession = Depends(get_db)
):
    from backend.collection.service import PlatformSyncService
    
    updated_record = await PlatformSyncService.sync_platforms(db, student_uuid)
    if not updated_record:
        raise HTTPException(404, "Student profile not found")
        
    return {
        "status": "success",
        "github_profile": updated_record.github_profile,
        "leetcode_profile": updated_record.leetcode_profile,
        "codeforces_profile": updated_record.codeforces_profile,
        "codechef_profile": updated_record.codechef_profile,
        "platform_sync_metadata": updated_record.platform_sync_metadata
    }
