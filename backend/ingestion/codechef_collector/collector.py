"""CodeChef profile data collector.

Uses BeautifulSoup to scrape structured data directly from CodeChef profile page.
Falls back to returning a minimal profile (username only) when the page is unavailable.
Does **not** calculate any scores or rankings.
"""

from __future__ import annotations

import asyncio
from typing import Any, Optional

import httpx
from loguru import logger

from backend.ingestion.models.student_profile import CodeChefProfile


class CodeChefCollector:
    """Collects CodeChef profile data via web scraping.

    Because third-party APIs can be unreliable, this collector directly scrapes
    the public profile. It is designed to degrade gracefully — returning a minimal
    profile with just the username on any failure.

    Attributes:
        MAX_RETRIES: Number of retry attempts for transient failures.
        BACKOFF_BASE: Base delay (seconds) for exponential back‑off.
    """

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

        # Use an async client without strict redirects or custom API constraints
        async with httpx.AsyncClient(
            timeout=httpx.Timeout(30.0),
            follow_redirects=True,
        ) as client:
            html = await self._fetch_profile(client, username)

        if html is None:
            logger.warning(
                "CodeChef profile unavailable for {} – returning minimal profile",
                username,
            )
            return CodeChefProfile(username=username)

        return self._parse_response(username, html)

    # ── HTTP helper with retry ───────────────────────────────────────────

    async def _fetch_profile(
        self,
        client: httpx.AsyncClient,
        username: str,
    ) -> str | None:
        """GET the profile HTML with retry + exponential back‑off."""
        url = f"https://www.codechef.com/users/{username}"

        for attempt in range(1, self.MAX_RETRIES + 1):
            try:
                response = await client.get(url)
                response.raise_for_status()
                return response.text

            except httpx.HTTPStatusError as exc:
                if exc.response.status_code == 404:
                    logger.warning("CodeChef user {} not found", username)
                    return None
                logger.warning(
                    "HTTP {} from CodeChef (attempt {}/{}): {}",
                    exc.response.status_code,
                    attempt,
                    self.MAX_RETRIES,
                    exc,
                )
            except Exception as exc:
                logger.warning(
                    "Unexpected error querying CodeChef (attempt {}/{}): {}",
                    attempt,
                    self.MAX_RETRIES,
                    exc,
                )

            await self._backoff(attempt)

        logger.error(
            "All {} retries exhausted for CodeChef (user: {})",
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
        html: str,
    ) -> CodeChefProfile:
        """Parse the CodeChef profile HTML into a :class:`CodeChefProfile`."""
        from bs4 import BeautifulSoup
        import re

        soup = BeautifulSoup(html, "html.parser")

        # 1. Rating
        rating = 0
        rating_elem = soup.find('div', class_='rating-number')
        if rating_elem:
            m = re.search(r'\d+', rating_elem.text)
            if m: rating = int(m.group())

        # 2. Stars
        stars_str = "1★"
        star_elem = soup.find('div', class_='rating-star')
        if star_elem:
            star_count = star_elem.text.count('★')
            if star_count > 0:
                stars_str = f"{star_count}★"

        # 3. Highest Rating
        highest_rating = rating
        for highest_elem in soup.find_all('small'):
            if 'Highest Rating' in highest_elem.text:
                m = re.search(r'\d+', highest_elem.text)
                if m: 
                    val = int(m.group())
                    if val > highest_rating:
                        highest_rating = val

        # 4. Problems Solved
        solved = 0
        solved_section = soup.find('section', class_='rating-data-section problems-solved')
        if solved_section:
            match = re.search(r'Total Problems Solved:\s*(\d+)', solved_section.text)
            if match: solved = int(match.group(1))

        # 5. Contests Participated
        contests = 0
        contests_section = soup.find('div', class_='contest-participated-count')
        if contests_section:
            m = re.search(r'\d+', contests_section.text)
            if m: contests = int(m.group())

        profile = CodeChefProfile(
            username=username,
            rating=rating,
            highest_rating=highest_rating,
            stars=stars_str,
            contests=contests,
            contest_count=contests,  # legacy mapping
            solved_count=solved,
        )

        logger.info(
            "CodeChef collection complete for {} – rating: {}, stars: {}",
            profile.username,
            profile.rating,
            profile.stars,
        )
        return profile
