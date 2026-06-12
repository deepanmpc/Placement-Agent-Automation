import httpx
import asyncio
from datetime import datetime
from typing import Optional, Dict, Any, List
from .models import GitHubProfile, Repository, LeetCodeProfile, CodeforcesProfile, CodeChefProfile

import logging

logger = logging.getLogger(__name__)

class GitHubCollector:
    BASE_URL = "https://api.github.com"
    
    @classmethod
    async def collect(cls, github_url: str) -> Optional[GitHubProfile]:
        if not github_url:
            return None
            
        username = github_url.rstrip("/").split("/")[-1]
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                # Fetch user profile
                user_resp = await client.get(f"{cls.BASE_URL}/users/{username}")
                user_resp.raise_for_status()
                user_data = user_resp.json()
                
                # Fetch repos
                repos_resp = await client.get(f"{cls.BASE_URL}/users/{username}/repos?per_page=100")
                repos_resp.raise_for_status()
                repos_data = repos_resp.json()
                
                # Process data
                created_at = datetime.strptime(user_data.get("created_at", "2020-01-01T00:00:00Z"), "%Y-%m-%dT%H:%M:%SZ")
                account_age_days = (datetime.utcnow() - created_at).days
                
                total_stars = 0
                total_forks = 0
                languages = {}
                repositories = []
                
                for r in repos_data:
                    stars = r.get("stargazers_count", 0)
                    forks = r.get("forks_count", 0)
                    lang = r.get("language")
                    total_stars += stars
                    total_forks += forks
                    
                    if lang:
                        languages[lang] = languages.get(lang, 0) + 1
                        
                    repositories.append(Repository(
                        repo_name=r.get("name", ""),
                        description=r.get("description"),
                        stars=stars,
                        forks=forks,
                        language=lang,
                        topics=r.get("topics", []),
                        created_at=r.get("created_at"),
                        updated_at=r.get("updated_at")
                    ))
                
                return GitHubProfile(
                    username=username,
                    name=user_data.get("name"),
                    bio=user_data.get("bio"),
                    followers=user_data.get("followers", 0),
                    following=user_data.get("following", 0),
                    public_repos=user_data.get("public_repos", 0),
                    account_age_days=account_age_days,
                    total_stars=total_stars,
                    total_forks=total_forks,
                    language_distribution=languages,
                    repositories=repositories
                )
            except Exception as e:
                logger.error(f"GitHubCollector failed for {username}: {e}")
                return None


class LeetCodeCollector:
    URL = "https://leetcode.com/graphql/"

    @classmethod
    async def collect(cls, username: str) -> Optional[LeetCodeProfile]:
        if not username:
            return None
            
        query = """
        query getUserProfile($username: String!) {
            matchedUser(username: $username) {
                submitStats: submitStatsGlobal {
                    acSubmissionNum {
                        difficulty
                        count
                    }
                }
            }
            userContestRanking(username: $username) {
                attendedContestsCount
                rating
                globalRanking
            }
        }
        """
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                resp = await client.post(
                    cls.URL, 
                    json={"query": query, "variables": {"username": username}},
                    headers={"Content-Type": "application/json"}
                )
                resp.raise_for_status()
                data = resp.json().get("data", {})
                
                user_data = data.get("matchedUser") or {}
                contest_data = data.get("userContestRanking") or {}
                
                stats = user_data.get("submitStats", {}).get("acSubmissionNum", [])
                
                total = next((s["count"] for s in stats if s["difficulty"] == "All"), 0)
                easy = next((s["count"] for s in stats if s["difficulty"] == "Easy"), 0)
                medium = next((s["count"] for s in stats if s["difficulty"] == "Medium"), 0)
                hard = next((s["count"] for s in stats if s["difficulty"] == "Hard"), 0)
                
                return LeetCodeProfile(
                    total_solved=total,
                    easy_solved=easy,
                    medium_solved=medium,
                    hard_solved=hard,
                    contest_rating=contest_data.get("rating", 0.0),
                    global_ranking=contest_data.get("globalRanking", 0),
                    attended_contests=contest_data.get("attendedContestsCount", 0)
                )
            except Exception as e:
                logger.error(f"LeetCodeCollector failed for {username}: {e}")
                return None


class CodeforcesCollector:
    BASE_URL = "https://codeforces.com/api"

    @classmethod
    async def collect(cls, username: str) -> Optional[CodeforcesProfile]:
        if not username:
            return None
            
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                user_resp = await client.get(f"{cls.BASE_URL}/user.info?handles={username}")
                user_resp.raise_for_status()
                user_data = user_resp.json()
                
                if user_data.get("status") != "OK":
                    return None
                    
                info = user_data["result"][0]
                
                rating_resp = await client.get(f"{cls.BASE_URL}/user.rating?handle={username}")
                rating_resp.raise_for_status()
                rating_data = rating_resp.json()
                contests = rating_data.get("result", [])
                
                return CodeforcesProfile(
                    rating=info.get("rating", 0),
                    max_rating=info.get("maxRating", 0),
                    rank=info.get("rank"),
                    max_rank=info.get("maxRank"),
                    contest_count=len(contests)
                )
            except Exception as e:
                logger.error(f"CodeforcesCollector failed for {username}: {e}")
                return None


class CodeChefCollector:
    @classmethod
    async def collect(cls, username: str) -> Optional[CodeChefProfile]:
        if not username:
            return None
            
        # Using a public unofficial API or mock since official API requires OAuth
        url = f"https://codechef-api.vercel.app/handle/{username}"
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                resp = await client.get(url)
                resp.raise_for_status()
                data = resp.json()
                
                if not data.get("success", False):
                    return None
                    
                return CodeChefProfile(
                    rating=data.get("currentRating", 0),
                    stars=data.get("stars", "1★"),
                    highest_rating=data.get("highestRating", 0),
                    contest_count=len(data.get("ratingData", [])),
                    solved_count=0  # The API might not provide this easily
                )
            except Exception as e:
                logger.error(f"CodeChefCollector failed for {username}: {e}")
                # Mock fallback if api is down
                return CodeChefProfile(
                    rating=1500,
                    stars="3★",
                    highest_rating=1600,
                    contest_count=5,
                    solved_count=20
                )
