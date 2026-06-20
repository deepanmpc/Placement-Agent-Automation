from typing import List, Set

class SkillNormalizationService:
    def __init__(self):
        self.canonical_map = {
            "Spring Boot": ["spring mvc", "spring security", "java backend", "springboot", "spring"],
            "React": ["reactjs", "redux", "next.js", "nextjs", "react.js"],
            "Node.js": ["express.js", "backend apis", "rest apis", "nodejs", "node", "express"],
            "Python": ["django", "flask", "fastapi", "python3"],
            "Java": ["j2ee", "core java", "java 8", "java 11"],
            "C++": ["cpp", "c/c++"],
            "JavaScript": ["js", "es6", "vanilla js"],
            "AWS": ["amazon web services", "ec2", "s3", "lambda"],
            "SQL": ["mysql", "postgresql", "postgres", "rdbms"]
        }

    def get_canonical_skills(self, skills: List[str]) -> List[str]:
        canonical = set()
        normalized_input = [s.lower() for s in skills]
        
        for input_skill in normalized_input:
            canonical.add(input_skill) # Keep original
            
            for canonical_skill, variations in self.canonical_map.items():
                if input_skill == canonical_skill.lower() or input_skill in variations:
                    canonical.add(canonical_skill)
                    
        return list(canonical)

    def get_canonical_for_text(self, text: str) -> List[str]:
        canonical = set()
        text_lower = text.lower()
        
        for canonical_skill, variations in self.canonical_map.items():
            if canonical_skill.lower() in text_lower:
                canonical.add(canonical_skill)
            for var in variations:
                if var in text_lower:
                    canonical.add(canonical_skill)
                    
        return list(canonical)

skill_normalization_service = SkillNormalizationService()
