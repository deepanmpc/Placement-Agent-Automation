"""Codeforces profile data collector using the Codeforces REST API.

Fetches user rating, rank, solved‑problem count, and contest participation.
Does **not** calculate any scores or rankings.
"""

from __future__ import annotations

import asyncio
from typing import Any, Optional

import httpx
from loguru import logger

from backend.ingestion.models.student_profile import CodeforcesProfile


class CodeforcesCollector:
    """Collects Codeforces profile data via the public REST API.

    Attributes:
        BASE_URL: Root endpoint for the Codeforces API.
        MAX_RETRIES: Number of retry attempts for transient failures.
        BACKOFF_BASE: Base delay (seconds) for exponential back‑off.
    """

    BASE_URL: str = "https://codeforces.com/api"
    MAX_RETRIES: int = 3
    BACKOFF_BASE: float = 1.0

    # ── Public API ───────────────────────────────────────────────────────

    async def collect(self, username: str) -> CodeforcesProfile:
        """Collect a complete Codeforces profile for *username*.

        Args:
            username: Codeforces handle.

        Returns:
            A populated :class:`CodeforcesProfile`. On unrecoverable errors
            a profile containing only the username is returned.
        """
        if not username:
            logger.error("Empty Codeforces username supplied")
            return CodeforcesProfile()

        logger.info("Collecting Codeforces data for user: {}", username)

        async with httpx.AsyncClient(
            timeout=httpx.Timeout(30.0),
            follow_redirects=True,
        ) as client:
            user_info = await self._fetch_user_info(client, username)
            contest_count = await self._fetch_contest_count(client, username)
            solved_count = await self._fetch_solved_count(client, username)

        if user_info is None:
            logger.error(f"Could not fetch Codeforces user info for {username}")
            raise ValueError(f"Codeforces API failed for {username}")

        profile = CodeforcesProfile(
            username=user_info.get("handle", username),
            rating=int(user_info.get("rating", 0) or 0),
            max_rating=int(user_info.get("maxRating", 0) or 0),
            rank=str(user_info.get("rank", "") or ""),
            max_rank=str(user_info.get("maxRank", "") or ""),
            solved_count=solved_count,
            contest_count=contest_count,
            contests=contest_count,
        )
        logger.info(
            "Codeforces collection complete for {} – rating {} (max {}), "
            "{} solved, {} contests",
            profile.username,
            profile.rating,
            profile.max_rating,
            profile.solved_count,
            profile.contest_count,
        )
        return profile

    # ── HTTP helper with retry ───────────────────────────────────────────

    async def _request(
        self,
        client: httpx.AsyncClient,
        url: str,
        params: Optional[dict[str, str]] = None,
    ) -> dict[str, Any] | None:
        """GET *url* with retry + exponential back‑off.

        Codeforces returns ``{"status": "OK", "result": ...}`` on success.

        Returns:
            The full JSON dict on success, or ``None`` after exhausting
            retries.
        """
        for attempt in range(1, self.MAX_RETRIES + 1):
            try:
                response = await client.get(url, params=params)
                response.raise_for_status()
                body: dict[str, Any] = response.json()

                if body.get("status") != "OK":
                    comment = body.get("comment", "unknown error")
                    logger.warning(
                        "Codeforces API error (attempt {}/{}): {}",
                        attempt,
                        self.MAX_RETRIES,
                        comment,
                    )
                    # "handle not found" is terminal
                    if "not found" in str(comment).lower():
                        return None
                    await self._backoff(attempt)
                    continue

                return body

            except httpx.HTTPStatusError as exc:
                logger.warning(
                    "HTTP {} from Codeforces (attempt {}/{}): {}",
                    exc.response.status_code,
                    attempt,
                    self.MAX_RETRIES,
                    exc,
                )
            except httpx.RequestError as exc:
                logger.warning(
                    "Request error to Codeforces (attempt {}/{}): {}",
                    attempt,
                    self.MAX_RETRIES,
                    exc,
                )
            except Exception as exc:
                logger.warning(
                    "Unexpected error querying Codeforces (attempt {}/{}): {}",
                    attempt,
                    self.MAX_RETRIES,
                    exc,
                )

            await self._backoff(attempt)

        logger.error(
            "All {} retries exhausted for Codeforces API: {}",
            self.MAX_RETRIES,
            url,
        )
        return None

    async def _backoff(self, attempt: int) -> None:
        """Sleep with exponential back‑off."""
        delay = self.BACKOFF_BASE * (2 ** (attempt - 1))
        logger.debug("Backing off {:.1f}s before retry", delay)
        await asyncio.sleep(delay)

    # ── Data fetchers ────────────────────────────────────────────────────

    async def _fetch_user_info(
        self,
        client: httpx.AsyncClient,
        username: str,
    ) -> dict[str, Any] | None:
        """Fetch ``user.info`` and return the first result dict."""
        url = f"{self.BASE_URL}/user.info"
        body = await self._request(client, url, params={"handles": username})
        if body is None:
            return None

        result: list[dict[str, Any]] = body.get("result", [])
        if not result:
            logger.warning("user.info returned empty result for {}", username)
            return None
        return result[0]

    async def _fetch_contest_count(
        self,
        client: httpx.AsyncClient,
        username: str,
    ) -> int:
        """Return the number of rated contests via ``user.rating``."""
        url = f"{self.BASE_URL}/user.rating"
        body = await self._request(client, url, params={"handle": username})
        if body is None:
            return 0
        result: list[Any] = body.get("result", [])
        return len(result)

    async def _fetch_solved_count(
        self,
        client: httpx.AsyncClient,
        username: str,
    ) -> int:
        """Count unique problems solved (verdict == OK) via ``user.status``.

        Fetches up to 10 000 submissions. Each accepted submission is keyed
        by ``(contestId, index)`` to deduplicate.
        """
        url = f"{self.BASE_URL}/user.status"
        body = await self._request(
            client,
            url,
            params={"handle": username, "from": "1", "count": "10000"},
        )
        if body is None:
            return 0

        submissions: list[dict[str, Any]] = body.get("result", [])
        solved_problems: set[str] = set()

        for sub in submissions:
            if sub.get("verdict") == "OK":
                problem: dict[str, Any] = sub.get("problem", {})
                contest_id = problem.get("contestId", "")
                index = problem.get("index", "")
                if contest_id and index:
                    solved_problems.add(f"{contest_id}-{index}")

        return len(solved_problems)
