import re
import spacy
from typing import List, Dict, Any

class JDParsingService:
    def __init__(self):
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            # Fallback if not downloaded yet
            import spacy.cli
            spacy.cli.download("en_core_web_sm")
            self.nlp = spacy.load("en_core_web_sm")

    def parse_jd(self, jd_text: str) -> Dict[str, Any]:
        text = jd_text.lower()
        doc = self.nlp(jd_text)

        # Basic keyword extraction using Named Entities and Noun Chunks
        keywords = set()
        for ent in doc.ents:
            if ent.label_ in ["ORG", "PRODUCT", "GPE"]:
                keywords.add(ent.text.lower())
        for chunk in doc.noun_chunks:
            keywords.add(chunk.text.lower())

        # Determine role type based on common keywords
        role_type = "Full Stack"
        if any(w in text for w in ["frontend", "front-end", "react", "angular", "vue", "ui/ux", "css"]):
            role_type = "Frontend"
        if any(w in text for w in ["backend", "back-end", "node", "java", "spring", "django", "api", "database", "sql"]):
            role_type = "Backend"
            if "frontend" in text or "react" in text:
                role_type = "Full Stack"
        if any(w in text for w in ["competitive programming", "algorithms", "data structures", "dsa", "problem solving", "leetcode", "codeforces"]):
            role_type = "Competitive Programming"

        # Regex extractors
        batch_match = re.search(r'(202[0-9])\s*batch', text)
        batch = int(batch_match.group(1)) if batch_match else None

        # Experience keywords
        experience_keywords = []
        if "experience" in text or "internship" in text or "years" in text:
            experience_keywords.append("experience")
            
        # Basic required skills extraction (very naive, assumes comma-separated lists near 'skills')
        required_skills = []
        skills_match = re.search(r'skills(?: required)?[:\s]+((?:[a-z0-9+#.-]+(?:,\s*)?)+)', text)
        if skills_match:
            required_skills = [s.strip() for s in skills_match.group(1).split(",") if s.strip()]

        return {
            "required_skills": required_skills,
            "preferred_skills": [],
            "keywords": list(keywords)[:20], # limit to top 20
            "role_type": role_type,
            "batch_requirement": batch,
            "experience_keywords": experience_keywords
        }

jd_parsing_service = JDParsingService()
