from typing import Dict, List, Any
import numpy as np
from app.models.fitment_models import RetrievedChunk, Evidence, ParsedJD, MatchJDRequest

class ScoringService:
    def calculate_scores(self, req: MatchJDRequest, parsed_jd: ParsedJD, reranked: Dict[str, List[RetrievedChunk]]) -> Dict[str, Dict[str, Any]]:
        # Group chunks by student
        students_chunks = {}
        for section, chunks in reranked.items():
            for chunk in chunks:
                if chunk.student_id not in students_chunks:
                    students_chunks[chunk.student_id] = {"skills": [], "projects": [], "experience": [], "achievements": []}
                students_chunks[chunk.student_id][section].append(chunk)

        # Determine Weights
        if req.weights:
            w_skills = req.weights.get("skills", 40) / 100.0
            w_projects = req.weights.get("projects", 30) / 100.0
            w_experience = req.weights.get("experience", 20) / 100.0
            w_achievements = req.weights.get("achievements", 10) / 100.0
        else:
            role = parsed_jd.role_type
            if role == "Frontend":
                w_skills, w_projects, w_experience, w_achievements = 0.45, 0.35, 0.15, 0.05
            elif role == "Competitive Programming":
                w_skills, w_projects, w_experience, w_achievements = 0.30, 0.20, 0.10, 0.40
            elif role == "Backend":
                w_skills, w_projects, w_experience, w_achievements = 0.40, 0.35, 0.20, 0.05
            else:
                w_skills, w_projects, w_experience, w_achievements = 0.40, 0.30, 0.20, 0.10

        student_scores = {}
        for student_id, chunks_by_section in students_chunks.items():
            scores = {}
            evidence_list = []
            
            for section in ["skills", "projects", "experience", "achievements"]:
                section_chunks = chunks_by_section[section]
                if section_chunks:
                    scores_list = [c.score for c in section_chunks]
                    best_score = float(max(scores_list))
                    avg_score = float(np.mean(scores_list))
                    
                    # Section score blends best and avg
                    section_score = (best_score * 0.7) + (avg_score * 0.3)
                    scores[f"{section}_score"] = min(max(section_score * 100, 0), 100)
                    
                    # Capture evidence (the best chunk)
                    best_chunk = max(section_chunks, key=lambda c: c.score)
                    evidence_list.append(Evidence(
                        student_id=student_id,
                        matched_text=best_chunk.content,
                        matched_section=section,
                        score=best_chunk.score
                    ))
                else:
                    scores[f"{section}_score"] = 0.0

            semantic_score = (
                w_skills * scores["skills_score"] +
                w_projects * scores["projects_score"] +
                w_experience * scores["experience_score"] +
                w_achievements * scores["achievements_score"]
            )
            
            student_scores[student_id] = {
                "semantic_score": semantic_score,
                "skill_score": scores["skills_score"],
                "project_score": scores["projects_score"],
                "experience_score": scores["experience_score"],
                "achievement_score": scores["achievements_score"],
                "evidence": evidence_list,
                "chunks_by_section": chunks_by_section
            }
            
        return student_scores

scoring_service = ScoringService()
