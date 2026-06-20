from app.services.chunking_service import chunking_service

def test_chunking_with_full_profile():
    profile = {
        "student_uuid": "123",
        "education": {"graduation_year": 2026},
        "skills": {
            "all_skills": ["Python", "React", "Docker"]
        },
        "projects": [
            {"title": "Proj1", "description": "Desc1", "technologies": ["Python"]}
        ],
        "github": {
            "repositories": [
                {"name": "Repo1", "description": "RepoDesc1", "language": "Python", "topics": ["web"], "stars": 10}
            ]
        },
        "leetcode": {"rating": 1500, "total_solved": 100},
        "codeforces": {"rating": 1200, "solved_count": 50}
    }
    
    chunks = chunking_service.chunk_profile(profile)
    assert len(chunks) == 4
    
    sections = [c.section for c in chunks]
    assert "skills" in sections
    assert "projects" in sections
    assert "experience" in sections
    assert "achievements" in sections
    
    for c in chunks:
        assert c.student_id == "123"
        assert c.batch == 2026
        assert c.eligible is True

def test_empty_profile():
    profile = {"student_uuid": "123"}
    chunks = chunking_service.chunk_profile(profile)
    assert len(chunks) == 0
