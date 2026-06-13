"""GitHub profile data collector using the GitHub REST API v3.

Fetches user profile metadata, repository information, and computes
behavioural activity metrics (commit frequency, activity score,
contribution consistency). Does **not** calculate any scores or rankings.
"""

from __future__ import annotations

import asyncio
import re
from datetime import datetime, timezone
from typing import Any, Optional
from urllib.parse import urlparse

import httpx
from loguru import logger

from backend.ingestion.models.student_profile import GitHubProfile, GitHubRepository


class GitHubCollector:
    """Collects GitHub profile data using the GitHub REST API.

    Attributes:
        BASE_URL: Root endpoint for the GitHub REST API v3.
        MAX_RETRIES: Number of retry attempts for transient failures.
        BACKOFF_BASE: Base delay (seconds) for exponential back‑off.
    """

    BASE_URL: str = "https://api.github.com"
    MAX_RETRIES: int = 3
    BACKOFF_BASE: float = 1.0

    def __init__(self, token: Optional[str] = None) -> None:
        """Initialise the collector.

        Args:
            token: Optional GitHub personal‑access token. When supplied the
                   collector uses authenticated requests (higher rate limits).
        """
        self.token: Optional[str] = token
        self.headers: dict[str, str] = {
            "Accept": "application/vnd.github.v3+json",
        }
        if token:
            self.headers["Authorization"] = f"token {token}"

    # ── Public API ───────────────────────────────────────────────────────

    async def collect(self, github_url: str) -> GitHubProfile:
        """Collect a complete GitHub profile for the user at *github_url*.

        Args:
            github_url: A GitHub profile URL such as
                ``https://github.com/username`` (with or without scheme /
                trailing slash).

        Returns:
            A fully‑populated :class:`GitHubProfile`. On unrecoverable errors
            an empty profile with only the URL field set is returned.
        """
        username = self._extract_username(github_url)
        if not username:
            logger.error("Failed to extract GitHub username from URL: {}", github_url)
            return GitHubProfile(profile_url=github_url)

        logger.info("Collecting GitHub data for user: {}", username)

        async with httpx.AsyncClient(
            headers=self.headers,
            timeout=httpx.Timeout(30.0),
            follow_redirects=True,
        ) as client:
            user_data = await self._fetch_user(client, username)
            if user_data is None:
                logger.warning("Could not fetch user profile for {}", username)
                return GitHubProfile(
                    username=username,
                    profile_url=f"https://github.com/{username}",
                )

            repositories = await self._fetch_repositories(client, username)

        # Build model objects
        repo_models = self._build_repo_models(repositories)
        languages = self._aggregate_languages(repositories)
        total_stars = sum(r.get("stargazers_count", 0) for r in repositories)

        # Behaviour metrics
        now = datetime.now(tz=timezone.utc)
        commit_frequency = self._calc_commit_frequency(repositories, now)
        activity_score = self._calc_activity_score(repositories, now)
        contribution_consistency = self._calc_contribution_consistency(
            repositories, now
        )

        commits_last_365 = 0
        contribution_days_365 = 0
        active_days_90 = 0
        merged_prs = 0
        issues_closed = 0
        
        # Scrape Contributions graph
        try:
            async with httpx.AsyncClient() as unauth_client:
                contrib_resp = await unauth_client.get(f"https://github.com/users/{username}/contributions", timeout=10.0)
                if contrib_resp.status_code == 200:
                    text = contrib_resp.text
                    m = re.search(r'(\d{1,3}(?:,\d{3})*)\s+contributions\s+in\s+the\s+last\s+year', text, re.IGNORECASE)
                    if m:
                        commits_last_365 = int(m.group(1).replace(',', ''))
                    
                    days = re.findall(r'data-date="([^"]+)"[^>]*data-level="([0-4])"', text)
                    if not days:
                        days = re.findall(r'data-level="([0-4])"[^>]*data-date="([^"]+)"', text)
                        days = [(d, l) for l, d in days]
                    
                    if days:
                        contribution_days_365 = sum(1 for d, l in days if l != '0')
                        last_90 = days[-90:]
                        active_days_90 = sum(1 for d, l in last_90 if l != '0')
        except Exception as e:
            logger.warning(f"Failed to scrape contributions for {username}: {e}")

        async with httpx.AsyncClient(headers=self.headers, timeout=httpx.Timeout(15.0)) as client:
            try:
                pr_url = f"{self.BASE_URL}/search/issues?q=author:{username}+type:pr+is:merged"
                pr_resp = await self._request(client, "GET", pr_url)
                if pr_resp:
                    merged_prs = pr_resp.json().get("total_count", 0)
            except Exception as e:
                logger.warning(f"Failed to fetch PRs for {username}: {e}")

            try:
                iss_url = f"{self.BASE_URL}/search/issues?q=author:{username}+type:issue+is:closed"
                iss_resp = await self._request(client, "GET", iss_url)
                if iss_resp:
                    issues_closed = iss_resp.json().get("total_count", 0)
            except Exception as e:
                logger.warning(f"Failed to fetch issues for {username}: {e}")

        profile = GitHubProfile(
            username=user_data.get("login", username),
            name=user_data.get("name"),
            bio=user_data.get("bio"),
            public_repos=user_data.get("public_repos", 0),
            followers=user_data.get("followers", 0),
            following=user_data.get("following", 0),
            total_stars=total_stars,
            repositories=repo_models,
            language_distribution=languages,
            languages=list(languages.keys()),
            commit_frequency=round(commit_frequency, 2),
            activity_score=round(activity_score, 2),
            contribution_consistency=round(contribution_consistency, 2),
            commits_last_365=commits_last_365,
            contribution_days_365=contribution_days_365,
            active_days_90=active_days_90,
            merged_prs=merged_prs,
            issues_closed=issues_closed,
            profile_url=user_data.get("html_url", f"https://github.com/{username}"),
            avatar_url=user_data.get("avatar_url"),
            created_at=self._parse_dt(user_data.get("created_at")),
        )
        logger.info(
            "GitHub collection complete for {} – {} repos, {} stars",
            username,
            len(repo_models),
            total_stars,
        )
        return profile

    # ── HTTP helpers with retry ──────────────────────────────────────────

    async def _request(
        self,
        client: httpx.AsyncClient,
        method: str,
        url: str,
        **kwargs: Any,
    ) -> httpx.Response | None:
        """Execute an HTTP request with retry + exponential back‑off.

        Args:
            client: The ``httpx.AsyncClient`` instance.
            method: HTTP verb (``GET``, ``POST``, …).
            url: Fully‑qualified URL.
            **kwargs: Forwarded to ``client.request``.

        Returns:
            The :class:`httpx.Response` on success, or ``None`` after all
            retries are exhausted.
        """
        for attempt in range(1, self.MAX_RETRIES + 1):
            try:
                response = await client.request(method, url, **kwargs)

                # Respect GitHub rate limits
                if response.status_code == 403:
                    remaining = response.headers.get("X-RateLimit-Remaining", "")
                    if remaining == "0":
                        logger.warning(
                            "GitHub rate limit hit on attempt {}/{}",
                            attempt,
                            self.MAX_RETRIES,
                        )
                        await self._backoff(attempt)
                        continue

                if response.status_code == 404:
                    logger.warning("Resource not found: {}", url)
                    return None

                response.raise_for_status()
                return response

            except httpx.HTTPStatusError as exc:
                logger.warning(
                    "HTTP {} on {} (attempt {}/{}): {}",
                    exc.response.status_code,
                    url,
                    attempt,
                    self.MAX_RETRIES,
                    exc,
                )
            except httpx.RequestError as exc:
                logger.warning(
                    "Request error on {} (attempt {}/{}): {}",
                    url,
                    attempt,
                    self.MAX_RETRIES,
                    exc,
                )

            await self._backoff(attempt)

        logger.error("All {} retries exhausted for {}", self.MAX_RETRIES, url)
        return None

    async def _backoff(self, attempt: int) -> None:
        """Sleep with exponential back‑off."""
        delay = self.BACKOFF_BASE * (2 ** (attempt - 1))
        logger.debug("Backing off {:.1f}s before retry", delay)
        await asyncio.sleep(delay)

    # ── Data fetchers ────────────────────────────────────────────────────

    async def _fetch_user(
        self,
        client: httpx.AsyncClient,
        username: str,
    ) -> dict[str, Any] | None:
        """Fetch ``/users/{username}`` and return the JSON dict, or ``None``."""
        url = f"{self.BASE_URL}/users/{username}"
        resp = await self._request(client, "GET", url)
        if resp is None:
            return None
        try:
            return resp.json()  # type: ignore[no-any-return]
        except Exception:
            logger.exception("Failed to decode user JSON for {}", username)
            return None

    async def _fetch_repositories(
        self,
        client: httpx.AsyncClient,
        username: str,
    ) -> list[dict[str, Any]]:
        """Fetch all public repos for *username* (paginated, up to 300)."""
        all_repos: list[dict[str, Any]] = []
        page = 1
        max_pages = 3  # 100 per page → 300 repos maximum

        while page <= max_pages:
            url = (
                f"{self.BASE_URL}/users/{username}/repos"
                f"?per_page=100&sort=updated&page={page}"
            )
            resp = await self._request(client, "GET", url)
            if resp is None:
                break
            try:
                repos: list[dict[str, Any]] = resp.json()
            except Exception:
                logger.exception("Failed to decode repos JSON page {}", page)
                break

            if not repos:
                break
            all_repos.extend(repos)
            page += 1

        logger.debug("Fetched {} repositories for {}", len(all_repos), username)
        return all_repos

    # ── Model builders ───────────────────────────────────────────────────

    @staticmethod
    def _build_repo_models(
        repos: list[dict[str, Any]],
    ) -> list[GitHubRepository]:
        """Convert raw API dicts into :class:`GitHubRepository` models."""
        models: list[GitHubRepository] = []
        for r in repos:
            models.append(
                GitHubRepository(
                    name=r.get("name", ""),
                    description=r.get("description"),
                    language=r.get("language"),
                    stars=r.get("stargazers_count", 0),
                    forks=r.get("forks_count", 0),
                    topics=r.get("topics", []),
                    created_at=r.get("created_at"),
                    updated_at=r.get("updated_at"),
                )
            )
        return models

    @staticmethod
    def _aggregate_languages(
        repos: list[dict[str, Any]],
    ) -> dict[str, int]:
        """Count the number of repos using each language."""
        lang_counts: dict[str, int] = {}
        for r in repos:
            lang = r.get("language")
            if lang:
                lang_counts[lang] = lang_counts.get(lang, 0) + 1
        return lang_counts

    # ── Behaviour metrics ────────────────────────────────────────────────

    @staticmethod
    def _calc_commit_frequency(
        repos: list[dict[str, Any]],
        now: datetime,
    ) -> float:
        """Estimate weekly commit frequency.

        Heuristic: repos updated in the last 90 days divided by 13 weeks.
        """
        cutoff = now.timestamp() - 90 * 86_400
        recent = sum(
            1
            for r in repos
            if (
                dt := GitHubCollector._parse_dt(r.get("updated_at"))
            )
            is not None
            and dt.timestamp() >= cutoff
        )
        return recent / 13.0

    @staticmethod
    def _calc_activity_score(
        repos: list[dict[str, Any]],
        now: datetime,
    ) -> float:
        """Percentage of repos updated in the last 6 months, capped at 100."""
        if not repos:
            return 0.0
        cutoff = now.timestamp() - 180 * 86_400
        recent = sum(
            1
            for r in repos
            if (
                dt := GitHubCollector._parse_dt(r.get("updated_at"))
            )
            is not None
            and dt.timestamp() >= cutoff
        )
        return min((recent / len(repos)) * 100.0, 100.0)

    @staticmethod
    def _calc_contribution_consistency(
        repos: list[dict[str, Any]],
        now: datetime,
    ) -> float:
        """Fraction of the last 12 months with at least one repo update.

        Returns a value between 0 and 100.
        """
        cutoff = now.timestamp() - 365 * 86_400
        active_months: set[str] = set()

        for r in repos:
            dt = GitHubCollector._parse_dt(r.get("updated_at"))
            if dt is not None and dt.timestamp() >= cutoff:
                active_months.add(dt.strftime("%Y-%m"))

        return (len(active_months) / 12.0) * 100.0

    # ── Utilities ────────────────────────────────────────────────────────

    @staticmethod
    def _extract_username(url: str) -> str | None:
        """Extract a GitHub username from a profile URL.

        Handles:
            - ``https://github.com/username``
            - ``github.com/username``
            - ``http://github.com/username/``

        Returns:
            The username string, or ``None`` if extraction fails.
        """
        url = url.strip()

        # If it's just a raw username without slashes or domain
        if "/" not in url and "github.com" not in url:
            return url

        # Ensure a scheme so urlparse works correctly
        if not url.startswith(("http://", "https://")):
            url = f"https://{url}"

        parsed = urlparse(url)

        # Validate host
        if parsed.hostname not in ("github.com", "www.github.com"):
            logger.warning("URL host is not github.com: {}", parsed.hostname)
            return None

        # Extract first non‑empty path segment
        path_parts = [p for p in parsed.path.split("/") if p]
        if not path_parts:
            logger.warning("No username found in URL path: {}", parsed.path)
            return None

        return path_parts[0]

    @staticmethod
    def _parse_dt(value: str | None) -> datetime | None:
        """Parse an ISO‑8601 datetime string (as returned by GitHub)."""
        if not value:
            return None
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            return None
