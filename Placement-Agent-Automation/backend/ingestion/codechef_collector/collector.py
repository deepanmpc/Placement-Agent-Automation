"""CodeChef profile data collector.

Uses the community Vercel proxy API for structured JSON. Falls back to
returning a minimal profile (username only) when the API is unavailable.
Does **not** calculate any scores or rankings.
"""

from __future__ import annotations

import asyncio
from typing import Any, Optional

import httpx
from loguru import logger

from backend.ingestion.models.student_profile import CodeChefProfile


class CodeChefCollector:
    """Collects CodeChef profile data via a community JSON API.

    The official CodeChef API requires OAuth and is limited. This collector
    uses the ``codechef-api.vercel.app`` proxy which returns structured JSON
    for public profiles.  Because this third‑party proxy can be unreliable,
    the collector is designed to degrade gracefully — returning a minimal
    profile with just the username on any failure.

    Attributes:
        API_URL: Root endpoint for the Vercel proxy API.
        MAX_RETRIES: Number of retry attempts for transient failures.
        BACKOFF_BASE: Base delay (seconds) for exponential back‑off.
    """

    API_URL: str = "https://codechef-api.vercel.app/handle"
    MAX_RETRIES: int = 3
    BACKOFF_BASE: float = 1.0

    # ── Public API ───────────────────────────────────────────────────────

    async def collect(self, username: str) -> CodeChefProfile:
        """Collect a CodeChef profile for *username*.

        Args:
            username: CodeChef handle.

        Returns:
            A populated :class:`CodeChefProfile` on success, or a minimal
            profile with only the username field set on any failure.
        """
        if not username:
            logger.error("Empty CodeChef username supplied")
            return CodeChefProfile()

        logger.info("Collecting CodeChef data for user: {}", username)

        async with httpx.AsyncClient(
            timeout=httpx.Timeout(30.0),
            follow_redirects=True,
        ) as client:
            data = await self._fetch_profile(client, username)

        if data is None:
            logger.warning(
                "CodeChef API unavailable for {} – returning minimal profile",
                username,
            )
            return CodeChefProfile(username=username)

        return self._parse_response(username, data)

    # ── HTTP helper with retry ───────────────────────────────────────────

    async def _fetch_profile(
        self,
        client: httpx.AsyncClient,
        username: str,
    ) -> dict[str, Any] | None:
        """GET the profile JSON with retry + exponential back‑off.

        Returns:
            The parsed JSON dict on success, or ``None`` after all retries
            are exhausted.
        """
        url = f"{self.API_URL}/{username}"

        for attempt in range(1, self.MAX_RETRIES + 1):
            try:
                response = await client.get(url)
                response.raise_for_status()
                body: dict[str, Any] = response.json()

                if not body.get("success", False):
                    logger.warning(
                        "CodeChef API returned success=false for {} "
                        "(attempt {}/{})",
                        username,
                        attempt,
                        self.MAX_RETRIES,
                    )
                    await self._backoff(attempt)
                    continue

                return body

            except httpx.HTTPStatusError as exc:
                logger.warning(
                    "HTTP {} from CodeChef API (attempt {}/{}): {}",
                    exc.response.status_code,
                    attempt,
                    self.MAX_RETRIES,
                    exc,
                )
            except httpx.RequestError as exc:
                logger.warning(
                    "Request error to CodeChef API (attempt {}/{}): {}",
                    attempt,
                    self.MAX_RETRIES,
                    exc,
                )
            except Exception as exc:
                logger.warning(
                    "Unexpected error querying CodeChef API (attempt {}/{}): {}",
                    attempt,
                    self.MAX_RETRIES,
                    exc,
                )

            await self._backoff(attempt)

        logger.error(
            "All {} retries exhausted for CodeChef API (user: {})",
            self.MAX_RETRIES,
            username,
        )
        return None

    async def _backoff(self, attempt: int) -> None:
        """Sleep with exponential back‑off."""
        delay = self.BACKOFF_BASE * (2 ** (attempt - 1))
        logger.debug("Backing off {:.1f}s before retry", delay)
        await asyncio.sleep(delay)

    # ── Response parser ──────────────────────────────────────────────────

    @staticmethod
    def _parse_response(
        username: str,
        data: dict[str, Any],
    ) -> CodeChefProfile:
        """Map the raw API JSON to a :class:`CodeChefProfile`.

        Args:
            username: The queried handle (used as fallback).
            data: The full JSON response dict from the Vercel proxy.

        Returns:
            A populated :class:`CodeChefProfile`.
        """
        current_rating = CodeChefCollector._safe_int(
            data.get("currentRating", 0)
        )
        highest_rating = CodeChefCollector._safe_int(
            data.get("highestRating", 0)
        )
        stars = str(data.get("stars", "") or "")
        global_rank = CodeChefCollector._safe_int(data.get("globalRank", 0))
        country_rank = CodeChefCollector._safe_int(data.get("countryRank", 0))

        profile = CodeChefProfile(
            username=username,
            current_rating=current_rating,
            highest_rating=highest_rating,
            stars=stars,
            global_rank=global_rank,
            country_rank=country_rank,
        )
        logger.info(
            "CodeChef collection complete for {} – {} (rating {})",
            profile.username,
            profile.stars or "unrated",
            profile.current_rating,
        )
        return profile

    # ── Utilities ────────────────────────────────────────────────────────

    @staticmethod
    def _safe_int(value: Any) -> int:
        """Coerce *value* to ``int``, returning ``0`` on failure.

        The Vercel API sometimes returns stringified numbers or ``None``.
        """
        if value is None:
            return 0
        try:
            return int(value)
        except (ValueError, TypeError):
            return 0
