from typing import Dict, List, Any
from app.models.fitment_models import RetrievedChunk, Evidence
import re

class ExplanationService:
    def generate_explanations(self, student_scores: Dict[str, Any]) -> List[str]:
        explanations = []
        evidence_list: List[Evidence] = student_scores.get("evidence", [])
        
        skill_score = student_scores.get("skill_score", 0)
        project_score = student_scores.get("project_score", 0)
        exp_score = student_scores.get("experience_score", 0)
        ach_score = student_scores.get("achievement_score", 0)
        
        evidence_by_section = {e.matched_section: e for e in evidence_list}
        
        if skill_score > 60 and "skills" in evidence_by_section:
            text = evidence_by_section["skills"].matched_text
            skills_str = text.replace("Technical Skills: ", "").split(".")[0][:100]
            explanations.append(f"Strong skill alignment detected, including: {skills_str}.")
        elif skill_score > 30 and "skills" in evidence_by_section:
            explanations.append("Partial skill alignment found in profile.")
            
        if project_score > 60 and "projects" in evidence_by_section:
            text = evidence_by_section["projects"].matched_text
            title_match = re.search(r"Project: (.*?)\.", text)
            if title_match:
                title = title_match.group(1)[:50]
                explanations.append(f"Project '{title}' strongly matches the required JD context.")
            else:
                explanations.append("A project closely aligns with the role requirements.")
                
        if exp_score > 50 and "experience" in evidence_by_section:
            text = evidence_by_section["experience"].matched_text
            repo_match = re.search(r"Repository: (.*?)\.", text)
            if repo_match:
                repo_name = repo_match.group(1)[:50]
                explanations.append(f"GitHub repository '{repo_name}' indicates relevant practical experience.")
                
        if ach_score > 40 and "achievements" in evidence_by_section:
            text = evidence_by_section["achievements"].matched_text
            platform = text.split(":")[0][:20]
            explanations.append(f"Strong problem-solving indicators found on {platform}.")
            
        if not explanations:
            explanations.append("Limited semantic match for this job description.")
            
        return explanations

explanation_service = ExplanationService()
