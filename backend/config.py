"""Application configuration module.

Centralises all environment-driven settings for the Placement Agent
backend using *pydantic-settings*.  Every setting can be overridden
via an environment variable prefixed with ``PA_`` (e.g.
``PA_DATABASE_URL``, ``PA_QDRANT_HOST``).
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Root settings for the Placement Agent backend.

    Attributes:
        database_url: Async MySQL connection string (aiomysql driver).
        qdrant_host: Hostname for the Qdrant vector-database instance.
        qdrant_port: Port for the Qdrant gRPC / HTTP API.
        github_api_token: Personal-access token for GitHub API calls.
                          Optional – unauthenticated calls are rate-limited.
        log_level: Minimum log severity (DEBUG / INFO / WARNING / ERROR).
        upload_dir: Filesystem directory where uploaded résumé files are
                    temporarily stored before parsing.
    """

    model_config = SettingsConfigDict(
        env_prefix="PA_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Database ──────────────────────────────────────────────────────
    database_url: str = "mysql+aiomysql://root:15713007@127.0.0.1:3306/placement_agent"

    # ── Qdrant ────────────────────────────────────────────────────────
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333

    # ── External APIs ─────────────────────────────────────────────────
    github_api_token: Optional[str] = None

    # ── Logging ───────────────────────────────────────────────────────
    log_level: str = "INFO"

    # ── File Storage ──────────────────────────────────────────────────
    upload_dir: str = "/tmp/resumes"

    # ── Derived helpers ───────────────────────────────────────────────
    @property
    def upload_path(self) -> Path:
        """Return *upload_dir* as a :class:`pathlib.Path`, creating it if needed."""
        p = Path(self.upload_dir)
        p.mkdir(parents=True, exist_ok=True)
        return p


# Module-level singleton so the rest of the app can do:
#   from backend.config import settings
settings: Settings = Settings()

def get_settings() -> Settings:
    return settings
