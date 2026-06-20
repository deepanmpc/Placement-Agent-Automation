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
    (Projects, Skills) against a given Job Description text.
    """

    @classmethod
    def _safe_join(cls, items) -> str:
        """Safely join any list-like or model into a comma-separated string."""
        if items is None:
            return ""
        if isinstance(items, str):
            return items
        if isinstance(items, list):
            return ", ".join(str(i) for i in items if i)
        # Pydantic model — use all_skills or iterate known list fields
        parts = []
        for attr in ("all_skills", "programming_languages", "frameworks",
                     "databases", "cloud", "tools"):
            val = getattr(items, attr, None)
            if val and isinstance(val, list):
                parts.extend(str(s) for s in val if s)
        return ", ".join(parts)

    @classmethod
    def calculate_fitment(cls, profile: StudentProfile, job_description: str) -> ExplainableScore:
        if not job_description or not job_description.strip():
            return ExplainableScore(0.0, {"error": "No Job Description provided"})

        # 1. Embed Job Description
        try:
            jd_embedding = embedding_service.get_embedding(job_description)
        except Exception as e:
            return ExplainableScore(0.0, {"error": f"Embedding failed: {e}"})

        # 2. Extract and structure chunks from the profile
        chunks: List[Dict[str, Any]] = []

        # Skills Chunk — profile.skills is a Skills pydantic model
        try:
            if profile.skills:
                skills_str = cls._safe_join(profile.skills)
                if skills_str.strip():
                    chunks.append({"type": "skills", "text": f"Skills: {skills_str}", "weight": 0.30})
        except Exception:
            pass

        # Project Chunks — profile.projects is List[ProjectInfo]
        try:
            if profile.projects:
                for i, proj in enumerate(profile.projects):
                    parts = []
                    if getattr(proj, "title", None):
                        parts.append(proj.title)
                    if getattr(proj, "description", None):
                        parts.append(proj.description)
                    techs = getattr(proj, "technologies", None)
                    if techs and isinstance(techs, list):
                        parts.append(f"Technologies: {', '.join(str(t) for t in techs if t)}")
                    if parts:
                        proj_text = f"Project {i+1}: " + ". ".join(parts)
                        chunks.append({"type": f"project_{i+1}", "text": proj_text, "weight": 0.35})
        except Exception:
            pass

        # Education chunk for contextual match
        try:
            if profile.education:
                edu_parts = []
                if getattr(profile.education, "degree", None):
                    edu_parts.append(profile.education.degree)
                if getattr(profile.education, "branch", None):
                    edu_parts.append(profile.education.branch)
                if getattr(profile.education, "college", None):
                    edu_parts.append(profile.education.college)
                if edu_parts:
                    chunks.append({"type": "education", "text": "Education: " + ", ".join(edu_parts), "weight": 0.10})
        except Exception:
            pass

        # GitHub summary chunk
        try:
            if profile.github:
                gh = profile.github
                langs = getattr(gh, "languages", None) or []
                if langs and isinstance(langs, list):
                    gh_text = f"GitHub: {gh.public_repos or 0} repos, languages: {', '.join(str(l) for l in langs if l)}"
                    chunks.append({"type": "github_summary", "text": gh_text, "weight": 0.25})
        except Exception:
            pass

        if not chunks:
            return ExplainableScore(0.0, {"error": "Profile has no extractable chunks (no skills, projects, or education)"})

        # 3. Embed chunks and compute cosine similarity against JD
        breakdown = {}
        total_weighted_score = 0.0
        total_weights = 0.0

        for chunk in chunks:
            try:
                chunk_embedding = embedding_service.get_embedding(chunk["text"])
                similarity = cosine_similarity(jd_embedding, chunk_embedding)
                match_percentage = max(0.0, min(similarity * 100, 100.0))
                weighted_score = match_percentage * chunk["weight"]
                total_weighted_score += weighted_score
                total_weights += chunk["weight"]

                breakdown[chunk["type"]] = {
                    "similarity_score": round(match_percentage, 2),
                    "weight": chunk["weight"],
                    "text_snippet": chunk["text"][:120] + "..." if len(chunk["text"]) > 120 else chunk["text"]
                }
            except Exception as e:
                breakdown[chunk["type"]] = {"error": str(e), "similarity_score": 0.0, "weight": chunk["weight"]}
                total_weights += chunk["weight"]

        if total_weights == 0:
            return ExplainableScore(0.0, {"error": "Invalid weights"})

        final_fitment_score = total_weighted_score / total_weights

        return ExplainableScore(
            total_score=round(final_fitment_score, 2),
            breakdown=breakdown
        )
