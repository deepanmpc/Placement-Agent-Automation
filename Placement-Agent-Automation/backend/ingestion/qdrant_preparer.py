from pydantic import BaseModel, Field
from typing import List, Dict, Any
from backend.ingestion.models.student_profile import StudentProfile

class QdrantDocument(BaseModel):
    """Document prepared for future Qdrant indexing."""
    student_uuid: str
    document_type: str  # 'resume_text', 'project_text', 'github_project_text'
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

class QdrantPreparer:
    """Prepares searchable documents from StudentProfile for future Qdrant indexing.
    Does NOT generate embeddings. Only prepares text content."""
    
    def prepare(self, profile: StudentProfile) -> List[QdrantDocument]:
        documents = []
        
        # 1. resume_text: Combine name + education + skills + summary
        resume_parts = []
        if profile.personal_info.name:
            resume_parts.append(f"Name: {profile.personal_info.name}")
        if profile.education.degree:
            resume_parts.append(f"Education: {profile.education.degree} in {profile.education.branch or 'N/A'} from {profile.education.college or 'N/A'}, CGPA: {profile.education.cgpa or 'N/A'}")
        if profile.skills.all_skills:
            resume_parts.append(f"Skills: {', '.join(profile.skills.all_skills)}")
        
        if resume_parts:
            documents.append(QdrantDocument(
                student_uuid=profile.student_uuid,
                document_type='resume_text',
                content='\n'.join(resume_parts),
                metadata={'source': 'resume'}
            ))
        
        # 2. project_text: One document per project
        for proj in profile.projects:
            parts = []
            if proj.title: parts.append(f"Project: {proj.title}")
            if proj.description: parts.append(proj.description)
            if proj.technologies: parts.append(f"Technologies: {', '.join(proj.technologies)}")
            if parts:
                documents.append(QdrantDocument(
                    student_uuid=profile.student_uuid,
                    document_type='project_text',
                    content='\n'.join(parts),
                    metadata={'source': 'resume', 'project_title': proj.title}
                ))
        
        # 3. github_project_text: One document per GitHub repo
        for repo in profile.github.repositories:
            parts = []
            if repo.name: parts.append(f"Repository: {repo.name}")
            if repo.description: parts.append(repo.description)
            if repo.language: parts.append(f"Language: {repo.language}")
            if repo.topics: parts.append(f"Topics: {', '.join(repo.topics)}")
            if parts:
                documents.append(QdrantDocument(
                    student_uuid=profile.student_uuid,
                    document_type='github_project_text',
                    content='\n'.join(parts),
                    metadata={'source': 'github', 'repo_name': repo.name}
                ))
        
        return documents

    def prepare_combined_document(self, profile: StudentProfile) -> str:
        """Create a single combined searchable text for the student."""
        # Combine all documents into one text block
        docs = self.prepare(profile)
        return '\n\n---\n\n'.join(doc.content for doc in docs)
