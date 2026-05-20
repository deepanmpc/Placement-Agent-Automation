from fastapi import APIRouter, UploadFile, File
from planner_service.services.voice_service import VoiceService
import os
import shutil

router = APIRouter()
voice_service = VoiceService()

@router.post("/transcribe")
async def transcribe_endpoint(file: UploadFile = File(...)):
    temp_path = f"planner_service/outputs/transcripts/{file.filename}"
    
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    result = voice_service.transcribe_audio(temp_path)
    os.remove(temp_path)
    
    return result
