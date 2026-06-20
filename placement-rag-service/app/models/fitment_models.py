from pydantic import BaseModel
from typing import List, Optional, Literal, Dict, Any

class DocumentChunk(BaseModel):
    student_id: str
    section: Literal["skills", "projects", "experience", "achievements"]
    content: str
    batch: Optional[int] = None
    branch: Optional[str] = None
    eligible: Optional[bool] = None

class RetrievedChunk(BaseModel):
    student_id: str
    section: str
    content: str
    score: float
    batch: Optional[int] = None
    branch: Optional[str] = None
    eligible: Optional[bool] = None

class IndexStudentRequest(BaseModel):
    student_id: str

class IndexResponse(BaseModel):
    student_id: str
    chunks_indexed: int
    status: str

class IndexAllResponse(BaseModel):
    total_students: int
    total_chunks: int
    status: str
    errors: List[str]

class MatchJDRequest(BaseModel):
    job_description: str
    batch_filter: Optional[int] = None
    branch_filter: Optional[str] = None
    eligible_filter: Optional[bool] = None
    weights: Optional[Dict[str, int]] = None

class ParsedJD(BaseModel):
    required_skills: List[str]
    preferred_skills: List[str]
    keywords: List[str]
    role_type: str
    batch_requirement: Optional[int]
    experience_keywords: List[str]

class Evidence(BaseModel):
    student_id: str
    matched_text: str
    matched_section: str
    score: float

class StudentFitmentResult(BaseModel):
    student_id: str
    semantic_score: float
    skill_score: float
    project_score: float
    experience_score: float
    achievement_score: float
    explanation: List[str]
    evidence: List[Evidence]

class MatchJDResponse(BaseModel):
    results: List[StudentFitmentResult]
    total_students_evaluated: int
    processing_time_ms: float
