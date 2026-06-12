import json
import uuid
import re
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class PersonalInfo(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    portfolio: Optional[str] = None
    location: Optional[str] = None

class Education(BaseModel):
    institution: Optional[str] = None
    degree: Optional[str] = None
    specialization: Optional[str] = None
    cgpa: Optional[float] = None
    start_year: Optional[int] = None
    end_year: Optional[int] = None

# Skills schema simplified to List[str] directly in ResumeData

class Project(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    technologies: List[str] = Field(default_factory=list)
    github_url: Optional[str] = None
    live_url: Optional[str] = None
    duration: Optional[str] = None
    role: Optional[str] = None
    achievements: List[str] = Field(default_factory=list)

class Experience(BaseModel):
    company: Optional[str] = None
    role: Optional[str] = None
    duration: Optional[str] = None
    technologies: List[str] = Field(default_factory=list)
    responsibilities: List[str] = Field(default_factory=list)
    achievements: List[str] = Field(default_factory=list)

class Certification(BaseModel):
    title: Optional[str] = None
    provider: Optional[str] = None
    issue_date: Optional[str] = None
    credential_id: Optional[str] = None

class Achievement(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None

class CPPlatform(BaseModel):
    username: Optional[str] = None
    mentioned_rating: Optional[int] = None

class CompetitiveProgramming(BaseModel):
    leetcode: Optional[CPPlatform] = Field(default_factory=CPPlatform)
    codeforces: Optional[CPPlatform] = Field(default_factory=CPPlatform)
    codechef: Optional[CPPlatform] = Field(default_factory=CPPlatform)

class Confidence(BaseModel):
    personal_info: float = 0.0
    education: float = 0.0
    skills: float = 0.0
    projects: float = 0.0
    experience: float = 0.0
    certifications: float = 0.0
    achievements: float = 0.0

class ResumeData(BaseModel):
    student_uuid: str = Field(default_factory=lambda: str(uuid.uuid4()))
    personal_info: Optional[PersonalInfo] = Field(default_factory=PersonalInfo)
    education: List[Education] = Field(default_factory=list)
    skills: List[str] = Field(default_factory=list)
    projects: List[Project] = Field(default_factory=list)
    experience: List[Experience] = Field(default_factory=list)
    certifications: List[Certification] = Field(default_factory=list)
    achievements: List[Achievement] = Field(default_factory=list)
    competitive_programming: Optional[CompetitiveProgramming] = Field(default_factory=CompetitiveProgramming)
    confidence: Optional[Confidence] = Field(default_factory=Confidence)

def normalize_skill(skill_name: str) -> str:
    """Normalizes skill names to standard formats."""
    skill_map = {
        r'(?i)^node\.?js$': 'Node.js',
        r'(?i)^node$': 'Node.js',
        r'(?i)^react\.?js$': 'React',
        r'(?i)^react$': 'React',
        r'(?i)^vue\.?js$': 'Vue.js',
        r'(?i)^angular\.?js$': 'Angular',
        r'(?i)^pytorch framework$': 'PyTorch',
        r'(?i)^pytorch$': 'PyTorch',
        r'(?i)^tensorflow$': 'TensorFlow',
        r'(?i)^c\+\+$': 'C++',
        r'(?i)^python3?$': 'Python',
        r'(?i)^golang$': 'Go',
        r'(?i)^postgres(ql)?$': 'PostgreSQL',
        r'(?i)^mysql$': 'MySQL',
        r'(?i)^mongo(db)?$': 'MongoDB',
    }
    
    for pattern, standard_name in skill_map.items():
        if re.match(pattern, skill_name.strip()):
            return standard_name
    return skill_name.strip()

def normalize_skills_list(skills: List[str]) -> List[str]:
    """Iterates through the skills and normalizes each skill."""
    return list(set([normalize_skill(s) for s in skills if s]))

class ResumeExtractor:
    def __init__(self, llm_client=None):
        self.llm_client = llm_client
        self.system_prompt = """
        You are an expert Resume Intelligence Extraction Agent.
        Your task is to convert raw resume text into a structured JSON document.

        IMPORTANT RULES:
        1. Return ONLY valid JSON.
        2. Do NOT include markdown.
        3. Do NOT include explanations.
        4. If information is missing, return null.
        5. Never invent information.
        6. Normalize all skills into standard names (e.g., Node -> Node.js, ReactJS -> React).
        7. Preserve all project details.
        8. Extract every measurable achievement.
        9. Confidence score must be provided for every major section (0.0 to 1.0).
        10. Output must strictly follow the provided JSON schema.
        """

    def parse_with_local_heuristics(self, text: str) -> ResumeData:
        """
        Local parser to extract basic information using regex and heuristics.
        """
        data = ResumeData()
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # Extract Name (heuristic: first non-empty line without contact info)
        for line in lines[:5]:
            if not re.search(r'[@0-9]|github|linkedin', line, re.IGNORECASE):
                data.personal_info.name = line
                data.confidence.personal_info += 0.2
                break

        # Extract Emails
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
        if emails:
            data.personal_info.email = emails[0]
            data.confidence.personal_info += 0.4
            
        # Extract Phones
        phones = re.findall(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text)
        if phones:
            data.personal_info.phone = phones[0]
            data.confidence.personal_info += 0.2
            
        # Extract GitHub / LinkedIn URLs
        github_urls = re.findall(r'(?:https?://)?(?:www\.)?github\.com/[\w-]+', text)
        if github_urls:
            data.personal_info.github = github_urls[0]
            data.confidence.personal_info += 0.1
            
        linkedin_urls = re.findall(r'(?:https?://)?(?:www\.)?linkedin\.com/in/[\w-]+', text)
        if linkedin_urls:
            data.personal_info.linkedin = linkedin_urls[0]
            data.confidence.personal_info += 0.1

        # Basic Section Splitter
        sections = {"EDUCATION": "", "EXPERIENCE": "", "PROJECT": "", "SKILL": "", "CERTIFICATION": "", "LINKS": "", "PROFILE": "", "ACHIEVEMENT": ""}
        current_section = None
        
        for line in lines:
            upper_line = line.upper()
            matched_section = None
            for sec in sections.keys():
                if sec in upper_line and len(line) < 30:
                    matched_section = sec
                    break
            
            if matched_section:
                current_section = matched_section
            elif current_section:
                sections[current_section] += line + "\n"

        # Parse Education
        if sections["EDUCATION"]:
            edu_text = sections["EDUCATION"]
            cgpa_match = re.search(r'(?:CGPA|GPA)[\s:]*([0-9.]+)', edu_text, re.IGNORECASE)
            year_match = re.findall(r'(20\d{2})', edu_text)
            degree_match = re.search(r'(B\.?Tech|B\.?S\.?|Bachelor|Master|M\.?Tech|B\.?E\.?)', edu_text, re.IGNORECASE)
            
            edu = Education()
            edu_lines = [l for l in edu_text.split('\n') if l.strip()]
            edu.institution = edu_lines[0][:100] if edu_lines else None
            if cgpa_match: edu.cgpa = float(cgpa_match.group(1))
            if len(year_match) >= 1: edu.start_year = int(year_match[0])
            if len(year_match) >= 2: edu.end_year = int(year_match[1])
            if degree_match: edu.degree = degree_match.group(1)
            
            data.education.append(edu)
            data.confidence.education = 0.8

        # Parse Skills
        skills_text = sections["SKILL"] if sections["SKILL"] else text
        common_skills = [
            'python', 'java', 'c++', 'javascript', 'typescript', 'react', 'node', 'sql', 'aws', 'docker',
            'html', 'css', 'django', 'flask', 'spring', 'kubernetes', 'azure', 'gcp', 'mongodb', 'postgresql', 'mysql'
        ]
        # 1. String matching
        found_skills = [s for s in common_skills if re.search(rf'\b{s}\b', skills_text, re.IGNORECASE)]
        
        # 2. Exact extraction from the SKILL section
        extracted_skills = []
        if sections["SKILL"]:
            # Split by commas, newlines, or bullets
            raw_tokens = re.split(r'[,\n•\-\|]', sections["SKILL"])
            for token in raw_tokens:
                token = token.strip()
                # A skill is usually 1-3 words, not a full sentence.
                if 1 < len(token) < 30 and len(token.split()) <= 3:
                    # avoid matching headers again
                    if token.upper() not in {"SKILLS", "TECHNICAL SKILLS", "EXPERTISE"}:
                        extracted_skills.append(token)
                        
        # Combine and remove duplicates (case-insensitive)
        combined_skills = found_skills + extracted_skills
        unique_skills = []
        for s in combined_skills:
            if s.lower() not in [u.lower() for u in unique_skills]:
                unique_skills.append(s)

        if unique_skills:
            data.skills = unique_skills
            data.confidence.skills = 0.8

        # Parse Projects
        if sections["PROJECT"]:
            proj_lines = [l for l in sections["PROJECT"].split('\n') if l.strip()]
            if proj_lines:
                proj = Project()
                proj.title = proj_lines[0][:100]
                # Avoid cramming unrelated links and profiles into the description
                desc = " ".join(proj_lines[1:])
                # Clean up known URLs from the description to keep it clean
                desc = re.sub(r'(https?://[^\s]+)', '', desc).strip()
                proj.description = desc[:500] + ('...' if len(desc) > 500 else '')
                data.projects.append(proj)
                data.confidence.projects = 0.7

        # Parse Experience
        if sections["EXPERIENCE"]:
            exp_lines = [l for l in sections["EXPERIENCE"].split('\n') if l.strip()]
            if exp_lines:
                exp = Experience()
                exp.company = exp_lines[0][:100]
                exp.role = exp_lines[1][:100] if len(exp_lines) > 1 else None
                exp.responsibilities = [exp_lines[2]] if len(exp_lines) > 2 else []
                data.experience.append(exp)
                data.confidence.experience = 0.7
                
        # Parse Leetcode / Codeforces
        lc_match = re.search(r'leetcode\.com/([\w-]+)', text, re.IGNORECASE)
        if lc_match:
            if data.competitive_programming is None:
                data.competitive_programming = CompetitiveProgramming()
            data.competitive_programming.leetcode.username = lc_match.group(1)
            
        cf_match = re.search(r'codeforces\.com/profile/([\w-]+)', text, re.IGNORECASE)
        if cf_match:
            if data.competitive_programming is None:
                data.competitive_programming = CompetitiveProgramming()
            data.competitive_programming.codeforces.username = cf_match.group(1)

        return data

    def extract(self, resume_text: str) -> str:
        """
        Main extraction function. 
        In production, this should preferably use self.llm_client to parse the text 
        into the ResumeData schema. Here, it falls back to local parsing heuristics.
        """
        if self.llm_client:
            # Code to call LLM, e.g., OpenAI with structured output
            # response = self.llm_client.chat.completions.create(
            #     model="gpt-4o",
            #     messages=[
            #         {"role": "system", "content": self.system_prompt},
            #         {"role": "user", "content": resume_text}
            #     ],
            #     response_format={"type": "json_object"} # or use Instructor/Marvin
            # )
            # data = ResumeData.model_validate_json(response.choices[0].message.content)
            pass
        else:
            # Fallback to local regex-based parser
            data = self.parse_with_local_heuristics(resume_text)

        # Enforce skill normalization post-extraction
        data.skills = normalize_skills_list(data.skills)

        # Exclude unset fields using model_dump_json (Pydantic v2)
        # We ensure it returns the exact JSON format string requested
        return data.model_dump_json(indent=2)

if __name__ == "__main__":
    sample_resume = '''
    Jane Doe
    jane.doe@email.com | (555) 123-4567
    LinkedIn: linkedin.com/in/janedoe | GitHub: github.com/jdoe

    Education:
    B.S. in Computer Science, State University (2018-2022)
    CGPA: 3.9

    Skills:
    NodeJS, ReactJS, Python, Postgres, AWS, Docker
    '''
    
    extractor = ResumeExtractor()
    json_output = extractor.extract(sample_resume)
    print(json_output)
