"""LeetCode profile data collector using the public GraphQL API.

Fetches solve counts (easy / medium / hard), global ranking, contest rating,
and contests attended. Does **not** calculate any scores or rankings.
"""

from __future__ import annotations

import asyncio
from typing import Any, Optional

import httpx
from loguru import logger

from backend.ingestion.models.student_profile import LeetCodeProfile

# ── GraphQL query ────────────────────────────────────────────────────────────

_USER_PROFILE_QUERY: str = """
query getUserProfile($username: String!) {
  matchedUser(username: $username) {
    username
    submitStats: submitStatsGlobal {
      acSubmissionNum {
        difficulty
        count
      }
    }
    profile {
      ranking
    }
  }
  userContestRanking(username: $username) {
    rating
    attendedContestsCount
  }
}
"""


class LeetCodeCollector:
    """Collects LeetCode profile data via the public GraphQL endpoint.

    Attributes:
        GRAPHQL_URL: The LeetCode GraphQL API endpoint.
        MAX_RETRIES: Number of retry attempts for transient failures.
        BACKOFF_BASE: Base delay (seconds) for exponential back‑off.
    """

    GRAPHQL_URL: str = "https://leetcode.com/graphql"
    MAX_RETRIES: int = 3
    BACKOFF_BASE: float = 1.0

    # ── Public API ───────────────────────────────────────────────────────

    async def collect(self, username: str) -> LeetCodeProfile:
        """Collect a complete LeetCode profile for *username*.

        Args:
            username: LeetCode handle (case‑insensitive on the platform).

        Returns:
            A populated :class:`LeetCodeProfile`. On unrecoverable errors
            a profile containing only the username is returned.
        """
        if not username:
            logger.error("Empty LeetCode username supplied")
            return LeetCodeProfile()

        logger.info("Collecting LeetCode data for user: {}", username)

        payload: dict[str, Any] = {
            "query": _USER_PROFILE_QUERY,
            "variables": {"username": username},
        }

        headers: dict[str, str] = {
            "Content-Type": "application/json",
            "Referer": "https://leetcode.com",
        }

        async with httpx.AsyncClient(
            timeout=httpx.Timeout(30.0),
            follow_redirects=True,
        ) as client:
            data = await self._execute_query(client, payload, headers)

        if data is None:
            logger.warning(
                "LeetCode query returned no data for {}, returning default profile",
                username,
            )
            return LeetCodeProfile(username=username)

        return self._parse_response(username, data)

    # ── HTTP helper with retry ───────────────────────────────────────────

    async def _execute_query(
        self,
        client: httpx.AsyncClient,
        payload: dict[str, Any],
        headers: dict[str, str],
    ) -> dict[str, Any] | None:
        """Send the GraphQL query with retry + exponential back‑off.

        Returns:
            The ``"data"`` dict from the response, or ``None`` on failure.
        """
        for attempt in range(1, self.MAX_RETRIES + 1):
            try:
                response = await client.post(
                    self.GRAPHQL_URL,
                    json=payload,
                    headers=headers,
                )
                response.raise_for_status()
                body: dict[str, Any] = response.json()

                if "errors" in body:
                    logger.warning(
                        "GraphQL errors (attempt {}/{}): {}",
                        attempt,
                        self.MAX_RETRIES,
                        body["errors"],
                    )
                    # Some errors are terminal (e.g. user not found)
                    if any(
                        "not exist" in str(e.get("message", "")).lower()
                        for e in body["errors"]
                    ):
                        return None
                    await self._backoff(attempt)
                    continue

                return body.get("data")

            except httpx.HTTPStatusError as exc:
                logger.warning(
                    "HTTP {} from LeetCode (attempt {}/{}): {}",
                    exc.response.status_code,
                    attempt,
                    self.MAX_RETRIES,
                    exc,
                )
            except httpx.RequestError as exc:
                logger.warning(
                    "Request error to LeetCode (attempt {}/{}): {}",
                    attempt,
                    self.MAX_RETRIES,
                    exc,
                )
            except Exception as exc:
                logger.warning(
                    "Unexpected error querying LeetCode (attempt {}/{}): {}",
                    attempt,
                    self.MAX_RETRIES,
                    exc,
                )

            await self._backoff(attempt)

        logger.error(
            "All {} retries exhausted for LeetCode GraphQL query",
            self.MAX_RETRIES,
        )
        return None

    async def _backoff(self, attempt: int) -> None:
        """Sleep with exponential back‑off."""
        delay = self.BACKOFF_BASE * (2 ** (attempt - 1))
        logger.debug("Backing off {:.1f}s before retry", delay)
        await asyncio.sleep(delay)

    # ── Response parser ──────────────────────────────────────────────────

    @staticmethod
    def _parse_response(username: str, data: dict[str, Any]) -> LeetCodeProfile:
        """Map the raw GraphQL ``data`` dict to a :class:`LeetCodeProfile`.

        Args:
            username: The queried username (used as fallback).
            data: The ``"data"`` object from the GraphQL response.

        Returns:
            A populated :class:`LeetCodeProfile`.
        """
        matched_user: dict[str, Any] | None = data.get("matchedUser")
        contest_ranking: dict[str, Any] | None = data.get("userContestRanking")

        if matched_user is None:
            logger.warning("matchedUser is null for {} – user may not exist", username)
            return LeetCodeProfile(username=username)

        # ── Solve counts ─────────────────────────────────────────────────
        total_solved = 0
        easy_solved = 0
        medium_solved = 0
        hard_solved = 0

        submit_stats: dict[str, Any] | None = matched_user.get("submitStats")
        if submit_stats:
            ac_list: list[dict[str, Any]] = submit_stats.get(
                "acSubmissionNum", []
            )
            for entry in ac_list:
                difficulty: str = entry.get("difficulty", "")
                count: int = entry.get("count", 0)
                if difficulty == "All":
                    total_solved = count
                elif difficulty == "Easy":
                    easy_solved = count
                elif difficulty == "Medium":
                    medium_solved = count
                elif difficulty == "Hard":
                    hard_solved = count

        # ── Ranking ──────────────────────────────────────────────────────
        ranking: int = 0
        profile_obj: dict[str, Any] | None = matched_user.get("profile")
        if profile_obj:
            ranking = int(profile_obj.get("ranking", 0) or 0)

        # ── Contest rating ───────────────────────────────────────────────
        contest_rating: float = 0.0
        contests_attended: int = 0
        if contest_ranking:
            contest_rating = float(contest_ranking.get("rating", 0) or 0)
            contests_attended = int(
                contest_ranking.get("attendedContestsCount", 0) or 0
            )

        profile = LeetCodeProfile(
            username=matched_user.get("username", username),
            total_solved=total_solved,
            easy_solved=easy_solved,
            medium_solved=medium_solved,
            hard_solved=hard_solved,
            ranking=ranking,
            rating=round(contest_rating, 2),
            contests_participated=contests_attended,
        )
        logger.info(
            "LeetCode collection complete for {} – {} solved (E:{} M:{} H:{})",
            profile.username,
            total_solved,
            easy_solved,
            medium_solved,
            hard_solved,
        )
        return profile
