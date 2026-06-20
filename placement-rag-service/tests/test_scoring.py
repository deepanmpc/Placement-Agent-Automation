from app.services.scoring_service import scoring_service
from app.models.fitment_models import RetrievedChunk, MatchJDRequest, ParsedJD

def test_scoring_calculation():
    reranked = {
        "skills": [
            RetrievedChunk(student_id="1", section="skills", content="skills", score=0.8),
            RetrievedChunk(student_id="1", section="skills", content="skills2", score=0.6)
        ],
        "projects": [
            RetrievedChunk(student_id="1", section="projects", content="proj", score=0.9)
        ],
        "experience": [], # Empty should be 0
        "achievements": [
            RetrievedChunk(student_id="1", section="achievements", content="ach", score=0.5)
        ]
    }
    
    req = MatchJDRequest(job_description="test")
    parsed_jd = ParsedJD(
        required_skills=[], preferred_skills=[], keywords=[], role_type="Full Stack", batch_requirement=None, experience_keywords=[]
    )
    
    scores = scoring_service.calculate_scores(req, parsed_jd, reranked)
    assert "1" in scores
    
    s = scores["1"]
    
    # Skills: 0.8 best, 0.7 avg. Score = (0.8*0.7 + 0.7*0.3)*100 = (0.56 + 0.21)*100 = 77.0
    # Projects: 0.9 best, 0.9 avg. Score = 90.0
    # Experience: 0
    # Achievements: 0.5 best, 0.5 avg. Score = 50.0
    
    assert abs(s["skill_score"] - 77.0) < 0.1
    assert s["project_score"] == 90.0
    assert s["experience_score"] == 0.0
    assert s["achievement_score"] == 50.0
    
    # 0.40*77 + 0.30*90 + 0.20*0 + 0.10*50 = 30.8 + 27 + 0 + 5 = 62.8
    assert abs(s["semantic_score"] - 62.8) < 0.1
    assert len(s["evidence"]) == 3
