from typing import List, Dict, Any
from app.models.fitment_models import DocumentChunk
from app.services.skill_normalization_service import skill_normalization_service

class ChunkingService:
    def chunk_profile(self, profile_data: Dict[str, Any]) -> List[DocumentChunk]:
        chunks = []
        student_id = profile_data.get("student_uuid", "")
        if not student_id:
            return chunks
            
        education = profile_data.get("education") or {}
        batch = education.get("graduation_year")
        branch = education.get("branch")
        
        # Assume eligible=True unless marked otherwise in personal_info
        personal_info = profile_data.get("personal_info") or {}
        eligible = personal_info.get("eligible", True)

        # Skills chunk
        skills = profile_data.get("skills") or {}
        all_skills = skills.get("all_skills") or []
        if not all_skills:
            all_skills = []
            for k in ["programming_languages", "frameworks", "databases", "cloud", "tools"]:
                all_skills.extend(skills.get(k) or [])
        
        if all_skills:
            # Normalize skills
            normalized_skills = skill_normalization_service.get_canonical_skills(all_skills)
            skills_text = "Technical Skills: " + ", ".join(normalized_skills)
            chunks.append(DocumentChunk(
                student_id=student_id,
                section="skills",
                content=self._truncate(skills_text),
                batch=batch,
                branch=branch,
                eligible=eligible
            ))

        # Project chunks
        projects = profile_data.get("projects") or []
        for p in projects:
            title = p.get("title") or ""
            desc = p.get("description") or ""
            if not title and not desc:
                continue
            techs = p.get("technologies") or []
            tech_str = ", ".join(techs)
            p_text = f"Project: {title}. {desc}. Technologies: {tech_str}"
            chunks.append(DocumentChunk(
                student_id=student_id,
                section="projects",
                content=self._truncate(p_text),
                batch=batch,
                branch=branch,
                eligible=eligible
            ))

        # Experience chunks (GitHub repos)
        github = profile_data.get("github") or {}
        repos = github.get("repositories") or []
        # Sort by stars descending, take top 10
        sorted_repos = sorted(repos, key=lambda x: x.get("stars", 0), reverse=True)[:10]
        for r in sorted_repos:
            name = r.get("name") or ""
            desc = r.get("description") or ""
            if not name and not desc:
                continue
            lang = r.get("language") or ""
            topics = r.get("topics") or []
            r_text = f"Repository: {name}. {desc}. Language: {lang}. Topics: {', '.join(topics)}"
            chunks.append(DocumentChunk(
                student_id=student_id,
                section="experience",
                content=self._truncate(r_text),
                batch=batch,
                branch=branch,
                eligible=eligible
            ))

        # Achievement chunk (Competitive coding)
        ach_parts = []
        
        leetcode = profile_data.get("leetcode") or {}
        lc_rating = leetcode.get("rating", 0)
        lc_solved = leetcode.get("total_solved", 0)
        if lc_rating > 0 or lc_solved > 0:
            ach_parts.append(f"LeetCode: {lc_solved} problems solved (Easy: {leetcode.get('easy_solved',0)}, Medium: {leetcode.get('medium_solved',0)}, Hard: {leetcode.get('hard_solved',0)}), Rating: {lc_rating}, Contests: {leetcode.get('contests_participated',0)}")
            
        codechef = profile_data.get("codechef") or {}
        cc_rating = codechef.get("rating", 0)
        cc_solved = codechef.get("solved_count", 0)
        if cc_rating > 0 or cc_solved > 0:
            ach_parts.append(f"CodeChef: {codechef.get('stars', '')} Star, Rating: {cc_rating}, {cc_solved} problems solved")
            
        codeforces = profile_data.get("codeforces") or {}
        cf_rating = codeforces.get("rating", 0)
        cf_solved = codeforces.get("solved_count", 0)
        if cf_rating > 0 or cf_solved > 0:
            ach_parts.append(f"Codeforces: {codeforces.get('rank', '')}, Rating: {cf_rating}, Max Rating: {codeforces.get('max_rating',0)}, {cf_solved} problems solved")

        if ach_parts:
            ach_text = ". ".join(ach_parts)
            chunks.append(DocumentChunk(
                student_id=student_id,
                section="achievements",
                content=self._truncate(ach_text),
                batch=batch,
                branch=branch,
                eligible=eligible
            ))

        return chunks

    def _truncate(self, text: str, max_chars: int = 2000) -> str:
        return text[:max_chars]

chunking_service = ChunkingService()
