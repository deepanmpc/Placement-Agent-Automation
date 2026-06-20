import re
from typing import Dict, List, Any

class ResumeParser:
    """
    Service to parse and chunk raw resume text into structured formats.
    """
    
    @classmethod
    def parse(cls, raw_text: str) -> Dict[str, Any]:
        """
        Chunks and organizes the raw text into highly structured formats.
        Categorizes data into Projects, Skills, and Other Details.
        
        Args:
            raw_text (str): The raw text of the resume.
            
        Returns:
            Dict[str, Any]: A dictionary containing structured sections.
        """
        # A simple rule-based fallback implementation.
        # In a real implementation, this could use an LLM or more robust NLP.
        structured_data = {
            "projects": [],
            "skills": [],
            "other_details": ""
        }
        
        # Split text by common section headers
        sections = re.split(r'\n(?=(?:PROJECTS|SKILLS|EXPERIENCE|EDUCATION|OTHER):?)', raw_text, flags=re.IGNORECASE)
        
        other_details_chunks = []
        
        for section in sections:
            section_upper = section.strip().upper()
            if section_upper.startswith("PROJECT"):
                # Extract individual projects (heuristically splitting by newlines or bullets)
                content = re.sub(r'^PROJECTS?:?', '', section, flags=re.IGNORECASE).strip()
                projects = [p.strip() for p in re.split(r'\n-|\n•|\n\*', content) if p.strip()]
                if not projects:
                    projects = [content]
                structured_data["projects"].extend(projects)
            elif section_upper.startswith("SKILL"):
                content = re.sub(r'^SKILLS?:?', '', section, flags=re.IGNORECASE).strip()
                # Split skills by commas or bullets
                skills = [s.strip() for s in re.split(r',|\n-|\n•|\n\*', content) if s.strip()]
                structured_data["skills"].extend(skills)
            else:
                other_details_chunks.append(section.strip())
                
        structured_data["other_details"] = "\n\n".join(other_details_chunks).strip()
        
        return structured_data
