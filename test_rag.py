import sys
import os
sys.path.append(os.path.abspath('.'))

from backend.services.resume_parser import ResumeParser
from backend.services.embedding_service import embedding_service
from backend.ranking.weighted_ranker.semantic_ranker import SemanticRanker
from backend.services.llm_service import llm_service

def test_rag():
    print("Testing ResumeParser...")
    raw_resume = """
    JOHN DOE
    
    PROJECTS
    - Placement Agent RAG Microservice
    - Personal Portfolio Website
    
    SKILLS
    Python, React, Machine Learning, FastAPI
    
    OTHER
    B.Tech in Computer Science
    """
    
    parsed = ResumeParser.parse(raw_resume)
    print("Parsed Resume:")
    print(parsed)
    
    print("\nTesting SemanticRanker...")
    jd = "We are looking for a Python backend engineer with experience in FastAPI and Machine Learning."
    score = SemanticRanker.generate_score(parsed, jd)
    print(f"Semantic Score: {score}")

    print("\nTesting LLM Service...")
    explainability = llm_service.generate_explainability(parsed, jd)
    print(f"Explainability: {explainability}")

if __name__ == "__main__":
    test_rag()
