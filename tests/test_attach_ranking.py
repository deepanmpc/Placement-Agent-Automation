import sys
import os
import asyncio
from backend.ingestion.models.student_profile import StudentProfile, ProjectInfo, Skills
from backend.api.main import attach_ranking

def test():
    profile = StudentProfile()
    profile.projects = [ProjectInfo(title="Test Project", description="Test Desc", technologies=["Python", "FastAPI"])]
    profile.skills = Skills(all_skills=["Python", "Machine Learning"])

    jd = "Looking for a Python developer with Machine Learning experience."
    
    attach_ranking(profile, job_description=jd)
    print("Ranking Attached Successfully:")
    print(profile.ranking)

test()
