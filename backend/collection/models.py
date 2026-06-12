from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class Repository(BaseModel):
    repo_name: str
    description: Optional[str] = None
    stars: int = 0
    forks: int = 0
    language: Optional[str] = None
    topics: List[str] = []
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class GitHubStrength(BaseModel):
    activity_score: int = 0
    repository_score: int = 0
    collaboration_score: int = 0
    documentation_score: int = 0
    community_score: int = 0
    engineering_score: int = 0

class GitHubProfile(BaseModel):
    username: str
    name: Optional[str] = None
    bio: Optional[str] = None
    followers: int = 0
    following: int = 0
    public_repos: int = 0
    account_age_days: int = 0
    total_stars: int = 0
    total_forks: int = 0
    language_distribution: Dict[str, int] = {}
    commit_frequency: float = 0.0
    contribution_consistency: float = 0.0
    repository_growth: float = 0.0
    repositories: List[Repository] = []
    github_strength: Optional[GitHubStrength] = None
    snapshots: List[Dict[str, Any]] = Field(default_factory=list)

class LeetCodeProfile(BaseModel):
    total_solved: int = 0
    easy_solved: int = 0
    medium_solved: int = 0
    hard_solved: int = 0
    rating: float = 0.0
    global_ranking: int = 0
    attended_contests: int = 0
    submissions_last_30_days: int = 0
    active_days_last_30_days: int = 0
    rating_growth: float = 0.0
    solving_consistency: float = 0.0
    snapshots: List[Dict[str, Any]] = Field(default_factory=list)

class CodeforcesProfile(BaseModel):
    rating: int = 0
    max_rating: int = 0
    rank: Optional[str] = None
    max_rank: Optional[str] = None
    contest_count: int = 0
    recent_contests: int = 0
    solved_count: int = 0
    rating_growth: float = 0.0
    participation_consistency: float = 0.0
    snapshots: List[Dict[str, Any]] = Field(default_factory=list)

class CodeChefProfile(BaseModel):
    rating: int = 0
    stars: Optional[str] = None
    highest_rating: int = 0
    contest_count: int = 0
    solved_count: int = 0
    contest_activity: float = 0.0
    rating_growth: float = 0.0
    snapshots: List[Dict[str, Any]] = Field(default_factory=list)

class PlatformSyncMetadata(BaseModel):
    last_synced_at: str
    sync_status: str
    failed_platforms: List[str] = []
