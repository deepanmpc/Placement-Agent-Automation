import math
from typing import List, Dict, Any
from backend.ingestion.models.student_profile import StudentProfile
from backend.rag.embeddings.model import embedding_service
from .common import ExplainableScore

def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    dot_product = sum(a * b for a, b in zip(v1, v2))
    norm_v1 = math.sqrt(sum(a * a for a in v1))
    norm_v2 = math.sqrt(sum(b * b for b in v2))
    if norm_v1 == 0 or norm_v2 == 0:
        return 0.0
    return dot_product / (norm_v1 * norm_v2)

class SemanticRanker:
    """
    Computes a Semantic/Fitment Score by matching the structured chunks of a StudentProfile 
    (Projects, Experience, Skills) against a given Job Description text.
    """
    
    @classmethod
    def calculate_fitment(cls, profile: StudentProfile, job_description: str) -> ExplainableScore:
        if not job_description or not job_description.strip():
            return ExplainableScore(0.0, {"error": "No Job Description provided"})
        
        # 1. Embed Job Description
        jd_embedding = embedding_service.get_embedding(job_description)
        
        # 2. Extract and structure chunks from the profile
        chunks: List[Dict[str, Any]] = []
        
        # Skills Chunk
        if profile.skills:
            skills_text = "Skills: " + ", ".join(profile.skills)
            chunks.append({"type": "skills", "text": skills_text, "weight": 0.3})
        
        # Experience Chunks
        if profile.experience:
            for i, exp in enumerate(profile.experience):
                exp_text = f"Experience {i+1}: Role {exp.role} at {exp.company}."
                if exp.technologies:
                    exp_text += f" Technologies used: {', '.join(exp.technologies)}."
                if exp.responsibilities:
                    exp_text += f" Responsibilities: {', '.join(exp.responsibilities)}."
                chunks.append({"type": f"experience_{i+1}", "text": exp_text, "weight": 0.4})
                
        # Project Chunks
        if profile.projects:
            for i, proj in enumerate(profile.projects):
                proj_text = f"Project {i+1}: {proj.title}. {proj.description or ''}"
                if proj.technologies:
                    proj_text += f" Technologies: {', '.join(proj.technologies)}."
                chunks.append({"type": f"project_{i+1}", "text": proj_text, "weight": 0.3})
                
        if not chunks:
            return ExplainableScore(0.0, {"error": "Profile has no extractable chunks (no skills, projects, or experience)"})
            
        # 3. Embed chunks and compute similarity
        breakdown = {}
        total_weighted_score = 0.0
        total_weights = 0.0
        
        for chunk in chunks:
            chunk_embedding = embedding_service.get_embedding(chunk["text"])
            similarity = cosine_similarity(jd_embedding, chunk_embedding)
            
            # Map cosine similarity [-1, 1] to a percentage [0, 100]
            # (Usually similarity for these embeddings is bounded closer to [0, 1] in practice,
            # but we clamp it just in case).
            match_percentage = max(0.0, min(similarity * 100, 100.0))
            
            weighted_score = match_percentage * chunk["weight"]
            total_weighted_score += weighted_score
            total_weights += chunk["weight"]
            
            breakdown[chunk["type"]] = {
                "similarity_score": round(match_percentage, 2),
                "weight": chunk["weight"],
                "text_snippet": chunk["text"][:100] + "..." if len(chunk["text"]) > 100 else chunk["text"]
            }
            
        if total_weights == 0:
            return ExplainableScore(0.0, {"error": "Invalid weights"})
            
        final_fitment_score = total_weighted_score / total_weights
        
        return ExplainableScore(
            score=round(final_fitment_score, 2),
            breakdown=breakdown
        )
