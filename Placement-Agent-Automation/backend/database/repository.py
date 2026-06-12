"""Async repository for :class:`StudentProfileRecord` CRUD operations.

Every public method accepts (or uses) an :class:`AsyncSession` injected
at construction time and returns typed results.  All database errors are
caught, logged with *loguru*, and re-raised so callers can decide how to
handle them (e.g. return 500 in an API handler).
"""

from __future__ import annotations

from typing import List, Optional

from loguru import logger
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.models import StudentProfileRecord
from backend.ingestion.models.student_profile import StudentProfile


class StudentRepository:
    """Encapsulates persistence logic for student profiles.

    Parameters:
        session: An active :class:`AsyncSession` – typically provided
                 via FastAPI's ``Depends(get_db)`` or created manually
                 in background workers.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # ── CREATE / UPSERT ───────────────────────────────────────────────

    async def save_profile(self, profile: StudentProfile) -> str:
        """Persist a student profile, upserting if the UUID already exists.

        Args:
            profile: Fully or partially populated :class:`StudentProfile`.

        Returns:
            The ``student_uuid`` of the saved record.

        Raises:
            SQLAlchemyError: On unrecoverable database errors.
        """
        try:
            stmt = select(StudentProfileRecord).where(
                StudentProfileRecord.student_uuid == profile.student_uuid,
            )
            result = await self._session.execute(stmt)
            existing: Optional[StudentProfileRecord] = result.scalar_one_or_none()

            if existing is not None:
                logger.info(
                    "Updating existing profile for student_uuid={}",
                    profile.student_uuid,
                )
                existing.profile_data = profile.model_dump(mode="json")
                existing.resume_source = profile.metadata.resume_file
                existing.github_url = profile.personal_info.github_url
                existing.leetcode_username = profile.personal_info.leetcode_username
                existing.codeforces_username = profile.personal_info.codeforces_username
                existing.codechef_username = profile.personal_info.codechef_username
            else:
                logger.info(
                    "Creating new profile for student_uuid={}",
                    profile.student_uuid,
                )
                record = StudentProfileRecord(
                    student_uuid=profile.student_uuid,
                    profile_data=profile.model_dump(mode="json"),
                    resume_source=profile.metadata.resume_file,
                    github_url=profile.personal_info.github_url,
                    leetcode_username=profile.personal_info.leetcode_username,
                    codeforces_username=profile.personal_info.codeforces_username,
                    codechef_username=profile.personal_info.codechef_username,
                )
                self._session.add(record)

            await self._session.flush()
            logger.debug("Flushed profile {} to database", profile.student_uuid)
            return profile.student_uuid

        except IntegrityError as exc:
            logger.error(
                "Integrity error while saving profile {}: {}",
                profile.student_uuid,
                exc,
            )
            raise
        except SQLAlchemyError as exc:
            logger.error(
                "Database error while saving profile {}: {}",
                profile.student_uuid,
                exc,
            )
            raise

    # ── READ ──────────────────────────────────────────────────────────

    async def get_profile(self, student_uuid: str) -> Optional[StudentProfile]:
        """Retrieve a single student profile by its UUID.

        Args:
            student_uuid: The UUID v4 string identifying the student.

        Returns:
            A :class:`StudentProfile` if found, otherwise ``None``.

        Raises:
            SQLAlchemyError: On unrecoverable database errors.
        """
        try:
            stmt = select(StudentProfileRecord).where(
                StudentProfileRecord.student_uuid == student_uuid,
            )
            result = await self._session.execute(stmt)
            record: Optional[StudentProfileRecord] = result.scalar_one_or_none()

            if record is None:
                logger.debug("No profile found for student_uuid={}", student_uuid)
                return None

            logger.debug("Retrieved profile for student_uuid={}", student_uuid)
            return StudentProfile.model_validate(record.profile_data)

        except SQLAlchemyError as exc:
            logger.error(
                "Database error while fetching profile {}: {}",
                student_uuid,
                exc,
            )
            raise

    async def get_all_profiles(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> List[StudentProfile]:
        """Return a paginated list of student profiles.

        Args:
            limit: Maximum number of profiles to return.
            offset: Number of profiles to skip (for pagination).

        Returns:
            A list of :class:`StudentProfile` instances (may be empty).

        Raises:
            SQLAlchemyError: On unrecoverable database errors.
        """
        try:
            stmt = (
                select(StudentProfileRecord)
                .order_by(StudentProfileRecord.ingested_at.desc())
                .limit(limit)
                .offset(offset)
            )
            result = await self._session.execute(stmt)
            records = result.scalars().all()

            profiles = [
                StudentProfile.model_validate(rec.profile_data) for rec in records
            ]
            logger.debug(
                "Retrieved {} profiles (limit={}, offset={})",
                len(profiles),
                limit,
                offset,
            )
            return profiles

        except SQLAlchemyError as exc:
            logger.error(
                "Database error while listing profiles: {}",
                exc,
            )
            raise

    async def check_duplicate_filename(self, filename: str) -> bool:
        """Check if a profile with the same resume filename already exists."""
        if not filename:
            return False
        try:
            stmt = select(StudentProfileRecord.id).where(
                StudentProfileRecord.resume_source == filename
            ).limit(1)
            result = await self._session.execute(stmt)
            return result.scalar_one_or_none() is not None
        except SQLAlchemyError as exc:
            logger.error("Database error while checking duplicate filename: {}", exc)
            return False

    # ── UPDATE ────────────────────────────────────────────────────────

    async def update_profile(
        self,
        student_uuid: str,
        profile: StudentProfile,
    ) -> bool:
        """Replace an existing profile's data wholesale.

        Args:
            student_uuid: The UUID of the profile to update.
            profile: The new :class:`StudentProfile` payload.

        Returns:
            ``True`` if the record was found and updated, ``False``
            otherwise.

        Raises:
            SQLAlchemyError: On unrecoverable database errors.
        """
        try:
            stmt = select(StudentProfileRecord).where(
                StudentProfileRecord.student_uuid == student_uuid,
            )
            result = await self._session.execute(stmt)
            record: Optional[StudentProfileRecord] = result.scalar_one_or_none()

            if record is None:
                logger.warning(
                    "Cannot update – no profile found for student_uuid={}",
                    student_uuid,
                )
                return False

            record.profile_data = profile.model_dump(mode="json")
            record.resume_source = profile.metadata.resume_file
            record.github_url = profile.personal_info.github_url
            record.leetcode_username = profile.personal_info.leetcode_username
            record.codeforces_username = profile.personal_info.codeforces_username
            record.codechef_username = profile.personal_info.codechef_username

            await self._session.flush()
            logger.info("Updated profile for student_uuid={}", student_uuid)
            return True

        except SQLAlchemyError as exc:
            logger.error(
                "Database error while updating profile {}: {}",
                student_uuid,
                exc,
            )
            raise

    # ── DELETE ────────────────────────────────────────────────────────

    async def delete_profile(self, student_uuid: str) -> bool:
        """Delete a student profile by its UUID.

        Args:
            student_uuid: The UUID of the profile to remove.

        Returns:
            ``True`` if a record was deleted, ``False`` if none matched.

        Raises:
            SQLAlchemyError: On unrecoverable database errors.
        """
        try:
            stmt = delete(StudentProfileRecord).where(
                StudentProfileRecord.student_uuid == student_uuid,
            )
            result = await self._session.execute(stmt)

            if result.rowcount == 0:
                logger.warning(
                    "Cannot delete – no profile found for student_uuid={}",
                    student_uuid,
                )
                return False

            await self._session.flush()
            logger.info("Deleted profile for student_uuid={}", student_uuid)
            return True

        except SQLAlchemyError as exc:
            logger.error(
                "Database error while deleting profile {}: {}",
                student_uuid,
                exc,
            )
            raise
