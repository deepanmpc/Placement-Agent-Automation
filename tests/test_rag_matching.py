import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from backend.ranking.weighted_ranker.semantic_ranker import SemanticRanker

class MockProject:
    def __init__(self, title, description, technologies):
        self.title = title
        self.description = description
        self.technologies = technologies

class MockSkills:
    def __init__(self, all_skills):
        self.all_skills = all_skills

class MockProfile:
    def __init__(self, name, skills, projects):
        self.name = name
        self.skills = MockSkills(skills)
        self.projects = [MockProject(**p) for p in projects]

# 5 Test Resumes/Profiles
profiles = [
    MockProfile(
        name="Frontend Developer",
        skills=["React", "TypeScript", "Redux", "TailwindCSS", "Next.js", "HTML", "CSS"],
        projects=[
            {"title": "E-commerce Dashboard", "description": "Built a responsive admin dashboard with React and Redux.", "technologies": ["React", "Redux"]},
            {"title": "Portfolio Site", "description": "Server side rendered marketing site.", "technologies": ["Next.js", "TailwindCSS"]}
        ]
    ),
    MockProfile(
        name="Backend Java Developer",
        skills=["Java", "Spring Boot", "Hibernate", "PostgreSQL", "Kafka", "Microservices"],
        projects=[
            {"title": "Payment Service", "description": "Scalable payment processing service using Spring Boot.", "technologies": ["Java", "Spring Boot", "PostgreSQL"]},
            {"title": "Notification Engine", "description": "Event-driven architecture for notifications.", "technologies": ["Kafka", "Java"]}
        ]
    ),
    MockProfile(
        name="Machine Learning Engineer",
        skills=["Python", "TensorFlow", "PyTorch", "Scikit-Learn", "Pandas", "NLP", "LLMs"],
        projects=[
            {"title": "Sentiment Analyzer", "description": "Trained an NLP model to classify tweets.", "technologies": ["Python", "PyTorch"]},
            {"title": "Sales Forecaster", "description": "Time-series prediction using Scikit-learn.", "technologies": ["Python", "Pandas", "Scikit-Learn"]}
        ]
    ),
    MockProfile(
        name="DevOps Engineer",
        skills=["AWS", "Docker", "Kubernetes", "Terraform", "CI/CD", "Linux", "Jenkins"],
        projects=[
            {"title": "Cluster Migration", "description": "Migrated legacy apps to Kubernetes.", "technologies": ["Kubernetes", "Docker", "AWS"]},
            {"title": "Infra as Code", "description": "Automated provisioning with Terraform.", "technologies": ["Terraform", "CI/CD"]}
        ]
    ),
    MockProfile(
        name="Game Developer",
        skills=["C++", "Unreal Engine", "Unity", "C#", "3D Math", "Physics", "HLSL"],
        projects=[
            {"title": "FPS Prototype", "description": "Multiplayer first person shooter.", "technologies": ["C++", "Unreal Engine"]},
            {"title": "Mobile Puzzle Game", "description": "2D physics based puzzle game for Android.", "technologies": ["C#", "Unity"]}
        ]
    )
]

# 5 Test Job Descriptions
jds = [
    {
        "target": "Frontend Developer",
        "description": "Looking for a skilled UI developer experienced in React, state management like Redux, and modern CSS frameworks like Tailwind. Must know Next.js for SSR."
    },
    {
        "target": "Backend Java Developer",
        "description": "Seeking a backend engineer to build enterprise microservices. Strong experience with Java, Spring Boot, SQL databases, and event streaming (Kafka) required."
    },
    {
        "target": "Machine Learning Engineer",
        "description": "We need an AI specialist to develop deep learning models. Expertise in Python, PyTorch, and NLP is a must. Experience with LLMs is a plus."
    },
    {
        "target": "DevOps Engineer",
        "description": "Hiring a cloud infrastructure engineer. You will manage our AWS environments, orchestrate containers with Kubernetes, and maintain CI/CD pipelines using Terraform."
    },
    {
        "target": "Game Developer",
        "description": "Game studio looking for a programmer to work on a 3D AAA title. Must have strong C++ skills and extensive experience with Unreal Engine."
    }
]

def run_tests():
    print("Running Semantic Ranker Tests...\n")
    all_passed = True
    
    for jd_data in jds:
        target = jd_data["target"]
        jd_text = jd_data["description"]
        print(f"Testing JD targetting: {target}")
        
        scores = []
        for profile in profiles:
            score_obj = SemanticRanker.calculate_fitment(profile, jd_text)
            scores.append({
                "name": profile.name,
                "score": score_obj.total_score
            })
        
        # Sort scores highest to lowest
        scores.sort(key=lambda x: x["score"], reverse=True)
        
        top_match = scores[0]["name"]
        top_score = scores[0]["score"]
        
        print(f"  Top Match: {top_match} (Score: {top_score})")
        
        if top_match == target:
            print("  ✅ PASS\n")
        else:
            print(f"  ❌ FAIL: Expected {target} but got {top_match}")
            all_passed = False
            for s in scores:
                print(f"     - {s['name']}: {s['score']}")
            print("\n")

    if all_passed:
        print("ALL 5 TESTS PASSED! Semantic extraction and RAG scoring work correctly.")
        sys.exit(0)
    else:
        print("SOME TESTS FAILED! The RAG scoring engine needs fixing.")
        sys.exit(1)

if __name__ == "__main__":
    run_tests()
