"""SQLAlchemy ORM models for the Placement Agent database.

Uses the SQLAlchemy 2.0 :class:`DeclarativeBase` style with
:class:`Mapped` / :func:`mapped_column` type annotations.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional

from sqlalchemy import JSON, DateTime, Integer, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Shared declarative base for all ORM models."""


class StudentProfileRecord(Base):
    """Relational record for a single student profile.

    The full :class:`~backend.ingestion.models.student_profile.StudentProfile`
    payload is stored in :attr:`profile_data` as a JSON blob.  Top-level
    columns (``github_url``, ``leetcode_username``, …) are **denormalised
    copies** kept for fast filtering and indexing without JSON path queries.

    Attributes:
        id: Auto-incrementing surrogate primary key.
        student_uuid: Globally-unique student identifier (UUID v4).
        profile_data: Complete ``StudentProfile.model_dump()`` payload.
        resume_source: Original résumé filename, if any.
        github_url: GitHub profile URL (denormalised for indexing).
        leetcode_username: LeetCode handle (denormalised for indexing).
        codeforces_username: Codeforces handle (denormalised for indexing).
        codechef_username: CodeChef handle (denormalised for indexing).
        ingested_at: Timestamp of initial ingestion (UTC).
        updated_at: Timestamp of last update (UTC, auto-managed).
    """

    __tablename__ = "student_profiles"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    student_uuid: Mapped[str] = mapped_column(
        String(36),
        unique=True,
        index=True,
        nullable=False,
    )
    profile_data: Mapped[Dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
    )
    resume_source: Mapped[Optional[str]] = mapped_column(
        String(512),
        nullable=True,
    )
    github_url: Mapped[Optional[str]] = mapped_column(
        String(512),
        nullable=True,
    )
    leetcode_username: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )
    codeforces_username: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )
    codechef_username: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )
    github_profile: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
    )
    leetcode_profile: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
    )
    codeforces_profile: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
    )
    codechef_profile: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
    )
    platform_sync_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
    )
    ingested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        onupdate=lambda: datetime.now(tz=timezone.utc),
    )

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<StudentProfileRecord(id={self.id}, "
            f"uuid={self.student_uuid!r})>"
        )
