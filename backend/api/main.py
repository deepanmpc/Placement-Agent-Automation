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

@app.get("/profiles", response_model=List[StudentProfile])
async def list_profiles(
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    service = IngestionService(db_session=db, settings=settings)
    return await service.get_all_profiles(limit=limit, offset=offset)

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

@app.post("/profiles/batch-enrich")
async def batch_enrich(
    batch_size: int = Query(default=10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    """Enrich up to `batch_size` profiles with external coding and github data."""
    service = IngestionService(db_session=db, settings=settings)
    result = await service.batch_enrich_profiles(batch_size=batch_size)
    return result

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
