from backend.ingestion.resume_parser.resume_extractor import ResumeData
from backend.ingestion.models.student_profile import (
    StudentProfile, PersonalInfo, Education, Skills, ProjectInfo,
    GitHubProfile, LeetCodeProfile, CodeforcesProfile, CodeChefProfile,
    IngestionMetadata
)
from typing import Optional
from loguru import logger

class ProfileMerger:
    """Merges data from all sources into a unified StudentProfile."""
    
    def merge_resume_data(self, resume_data: ResumeData) -> StudentProfile:
        """Convert ResumeData into StudentProfile base."""
        profile = StudentProfile(student_uuid=resume_data.student_uuid)
        
        # Map personal_info
        profile.personal_info = PersonalInfo(
            name=resume_data.personal_info.name,
            email=resume_data.personal_info.email,
            phone=resume_data.personal_info.phone,
            linkedin_url=resume_data.personal_info.linkedin,
            github_url=resume_data.personal_info.github,
            portfolio_url=resume_data.personal_info.portfolio,
        )
        
        # Extract platform usernames from competitive_programming
        if resume_data.competitive_programming:
            if resume_data.competitive_programming.leetcode and resume_data.competitive_programming.leetcode.username:
                profile.personal_info.leetcode_username = resume_data.competitive_programming.leetcode.username
            if resume_data.competitive_programming.codeforces and resume_data.competitive_programming.codeforces.username:
                profile.personal_info.codeforces_username = resume_data.competitive_programming.codeforces.username
            if resume_data.competitive_programming.codechef and resume_data.competitive_programming.codechef.username:
                profile.personal_info.codechef_username = resume_data.competitive_programming.codechef.username
        
        # Map education (use first entry)
        if resume_data.education:
            edu = resume_data.education[0]
            profile.education = Education(
                college=edu.institution,
                degree=edu.degree,
                branch=edu.specialization,
                cgpa=edu.cgpa,
                graduation_year=edu.end_year,
            )
        
        # Map skills
        profile.skills = Skills(
            all_skills=resume_data.skills,
            # We can try to categorize, but all_skills is the flat list
        )
        
        # Map projects
        for proj in resume_data.projects:
            profile.projects.append(ProjectInfo(
                title=proj.title,
                description=proj.description,
                technologies=proj.technologies,
                github_link=proj.github_url,
            ))
        
        profile.metadata.sources_collected.append('resume')
        return profile
    
    def merge_github(self, profile: StudentProfile, github_data: GitHubProfile) -> StudentProfile:
        """Merge GitHub data into profile."""
        profile.github = github_data
        if 'github' not in profile.metadata.sources_collected:
            profile.metadata.sources_collected.append('github')
        return profile
    
    def merge_leetcode(self, profile: StudentProfile, leetcode_data: LeetCodeProfile) -> StudentProfile:
        profile.leetcode = leetcode_data
        if 'leetcode' not in profile.metadata.sources_collected:
            profile.metadata.sources_collected.append('leetcode')
        return profile
    
    def merge_codeforces(self, profile: StudentProfile, codeforces_data: CodeforcesProfile) -> StudentProfile:
        profile.codeforces = codeforces_data
        if 'codeforces' not in profile.metadata.sources_collected:
            profile.metadata.sources_collected.append('codeforces')
        return profile
    
    def merge_codechef(self, profile: StudentProfile, codechef_data: CodeChefProfile) -> StudentProfile:
        profile.codechef = codechef_data
        if 'codechef' not in profile.metadata.sources_collected:
            profile.metadata.sources_collected.append('codechef')
        return profile
    
    def merge_all(self, profile: StudentProfile, github: Optional[GitHubProfile] = None, leetcode: Optional[LeetCodeProfile] = None, codeforces: Optional[CodeforcesProfile] = None, codechef: Optional[CodeChefProfile] = None) -> StudentProfile:
        try:
            if github: self.merge_github(profile, github)
            if leetcode: self.merge_leetcode(profile, leetcode)
            if codeforces: self.merge_codeforces(profile, codeforces)
            if codechef: self.merge_codechef(profile, codechef)
        except Exception as e:
            logger.error(f"Error merging profiles: {e}")
            profile.metadata.errors.append(f"merger: {str(e)}")
        return profile
