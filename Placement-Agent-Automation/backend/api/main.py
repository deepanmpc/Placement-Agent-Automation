import os
import sys
import tempfile
import json
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from ingestion.resume_parser.resume_extractor import ResumeExtractor

app = FastAPI(title="Placement Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def extract_text_from_file(file_path: str, ext: str) -> str:
    if ext == ".txt" or ext == ".md":
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
            return text
        except ImportError:
            import pypdf
            reader = pypdf.PdfReader(file_path)
            text = ""
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
            return text
    elif ext == ".docx":
        import docx
        doc = docx.Document(file_path)
        return "\n".join([para.text for para in doc.paragraphs])
    return ""

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/upload")
async def upload_resume(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(400, "No file provided")

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in (".pdf", ".docx", ".txt", ".md"):
        raise HTTPException(400, f"Unsupported format: {ext}. Use PDF, DOCX, TXT, or MD.")

    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        text = extract_text_from_file(tmp_path, ext)
        if not text.strip():
            raise HTTPException(400, "Could not extract text from file")
            
        extractor = ResumeExtractor()
        result_json = extractor.extract(text)
        
        return json.loads(result_json)
    except Exception as e:
        raise HTTPException(500, f"Failed to parse resume: {str(e)}")
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
