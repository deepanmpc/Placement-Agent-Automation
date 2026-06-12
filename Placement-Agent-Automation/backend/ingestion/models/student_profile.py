"""Master StudentProfile schema for the Placement Agent ingestion pipeline.

Every data collector (résumé parser, GitHub scraper, LeetCode scraper, etc.)
writes its output into a single :class:`StudentProfile` instance.  This
guarantees a **uniform shape** regardless of which sources were collected and
makes downstream ranking / RAG trivially consistent.

All sub-models default to ``None`` or empty collections so a
partially-populated profile is always valid.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# ──────────────────────────────────────────────────────────────────────
# Sub-models
# ──────────────────────────────────────────────────────────────────────


class PersonalInfo(BaseModel):
    """Contact and social-platform handles extracted from a résumé."""

    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    leetcode_username: Optional[str] = None
    codeforces_username: Optional[str] = None
    codechef_username: Optional[str] = None


class Education(BaseModel):
    """Highest / most-relevant education entry."""

    college: Optional[str] = None
    degree: Optional[str] = None
    branch: Optional[str] = None
    cgpa: Optional[float] = None
    graduation_year: Optional[int] = None


class Skills(BaseModel):
    """Categorised technical skills.

    ``all_skills`` is a **flattened, deduplicated** list automatically
    maintained by consumers for fast look-ups and embedding.
    """

    programming_languages: List[str] = Field(default_factory=list)
    frameworks: List[str] = Field(default_factory=list)
    databases: List[str] = Field(default_factory=list)
    cloud: List[str] = Field(default_factory=list)
    tools: List[str] = Field(default_factory=list)
    all_skills: List[str] = Field(
        default_factory=list,
        description="Flattened unique list of every skill across all categories.",
    )


class ProjectInfo(BaseModel):
    """A single academic / personal project."""

    title: Optional[str] = None
    description: Optional[str] = None
    technologies: List[str] = Field(default_factory=list)
    github_link: Optional[str] = None


# ── Competitive / coding-platform profiles ────────────────────────────


class GitHubRepository(BaseModel):
    """Lightweight representation of a single GitHub repository."""

    name: Optional[str] = None
    stars: int = 0
    forks: int = 0
    language: Optional[str] = None
    topics: List[str] = Field(default_factory=list)
    description: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class GitHubProfile(BaseModel):
    """Aggregated GitHub activity metrics and repository listing."""

    username: Optional[str] = None
    public_repos: int = 0
    followers: int = 0
    following: int = 0
    total_stars: int = 0
    languages: List[str] = Field(default_factory=list)
    repositories: List[GitHubRepository] = Field(default_factory=list)
    commit_frequency: float = Field(
        default=0.0,
        description="Average commits per week over the last year.",
    )
    activity_score: float = Field(
        default=0.0,
        description="Composite score derived from stars, forks, and commit frequency.",
    )
    contribution_consistency: float = Field(
        default=0.0,
        description="Fraction of weeks in the past year with ≥1 commit.",
    )
    collected_at: Optional[datetime] = None


class LeetCodeProfile(BaseModel):
    """LeetCode competitive-programming statistics."""

    username: Optional[str] = None
    rating: float = 0.0
    ranking: int = 0
    easy_solved: int = 0
    medium_solved: int = 0
    hard_solved: int = 0
    total_solved: int = 0
    contests_participated: int = 0
    recent_contest_rating: float = 0.0
    collected_at: Optional[datetime] = None


class CodeforcesProfile(BaseModel):
    """Codeforces competitive-programming statistics."""

    username: Optional[str] = None
    rating: int = 0
    max_rating: int = 0
    rank: Optional[str] = None
    contests: int = 0
    solved_count: int = 0
    collected_at: Optional[datetime] = None


class CodeChefProfile(BaseModel):
    """CodeChef competitive-programming statistics."""

    username: Optional[str] = None
    rating: int = 0
    stars: Optional[str] = None
    contests: int = 0
    solved_count: int = 0
    collected_at: Optional[datetime] = None


# ── Metadata ──────────────────────────────────────────────────────────


class IngestionMetadata(BaseModel):
    """Book-keeping data attached to every ingested profile.

    Tracks *which* sources were collected, any errors encountered, and
    the schema version so future migrations are deterministic.
    """

    resume_file: Optional[str] = None
    ingested_at: datetime = Field(
        default_factory=lambda: datetime.now(tz=timezone.utc),
    )
    sources_collected: List[str] = Field(
        default_factory=list,
        description="Source identifiers, e.g. ['resume', 'github', 'leetcode'].",
    )
    errors: List[str] = Field(
        default_factory=list,
        description="Human-readable error messages from failed collectors.",
    )
    version: str = "1.0.0"


# ──────────────────────────────────────────────────────────────────────
# Root model
# ──────────────────────────────────────────────────────────────────────


class StudentProfile(BaseModel):
    """Canonical student profile aggregated from all ingestion sources.

    This is the **single source of truth** that every collector writes
    into and every downstream consumer (ranking engine, RAG pipeline,
    API layer) reads from.  The full model is persisted as JSON inside
    the ``student_profiles`` table so the relational schema never needs
    to change when new fields are added.
    """

    student_uuid: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Globally-unique student identifier (UUID v4).",
    )
    personal_info: PersonalInfo = Field(default_factory=PersonalInfo)
    education: Education = Field(default_factory=Education)
    skills: Skills = Field(default_factory=Skills)
    projects: List[ProjectInfo] = Field(default_factory=list)
    github: GitHubProfile = Field(default_factory=GitHubProfile)
    leetcode: LeetCodeProfile = Field(default_factory=LeetCodeProfile)
    codeforces: CodeforcesProfile = Field(default_factory=CodeforcesProfile)
    codechef: CodeChefProfile = Field(default_factory=CodeChefProfile)
    metadata: IngestionMetadata = Field(default_factory=IngestionMetadata)
