import sys
import re

with open('backend/api/main.py', 'r') as f:
    content = f.read()

# Add the endpoint after @app.put("/profiles/{student_uuid}")
new_endpoint = """
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
        
        # We only want to override education, skills, projects, and metadata.resume_file
        # We KEEP the personal_info, leetcode, github, codeforces, codechef data intact
        profile.education = merged_profile.education
        profile.skills = merged_profile.skills
        profile.projects = merged_profile.projects
        
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

"""

if "@app.post(\"/profiles/{student_uuid}/resume\")" not in content:
    content = content.replace('@app.delete("/profiles/{student_uuid}")', new_endpoint + '\n@app.delete("/profiles/{student_uuid}")')
    with open('backend/api/main.py', 'w') as f:
        f.write(content)
    print("Endpoint added")
else:
    print("Endpoint already exists")
