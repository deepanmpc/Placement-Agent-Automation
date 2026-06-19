"""
Codeforces Score Formula (0-100):
  CF_SCORE = MIN(CurrentRating / 3500, 1) × 45
           + MIN(MaxRating / 3500, 1) × 15
           + TitlePoints (0 to 10)
           + MIN(ProblemsSolved / 3000, 1) × 20
           + MIN(Contests / 100, 1) × 10
"""
from ..common import ExplainableScore
import re


def _safe_int(val) -> int:
    if isinstance(val, (int, float)):
        return int(val)
    if isinstance(val, str):
        m = re.search(r'\d+', val)
        return int(m.group()) if m else 0
    return 0


class CodeforcesRanker:

    @classmethod
    def calculate(cls, data: dict) -> ExplainableScore:
        rating     = _safe_int(data.get("rating", 0))
        max_rating = _safe_int(data.get("max_rating", 0))
        solved     = _safe_int(data.get("solved_count", data.get("solved", 0)))
        contests   = _safe_int(data.get("contests", data.get("contest_count", 0)))

        title = str(data.get("max_rank") or data.get("rank") or "").lower().strip()
        TITLE_MAP = {"newbie": 2, "pupil": 4, "specialist": 6, "expert": 8, "candidate master": 10, "master": 10, "international master": 10, "grandmaster": 10, "international grandmaster": 10, "legendary grandmaster": 10}
        
        title_points = TITLE_MAP.get(title, 0)
        if not title_points:
            if max_rating >= 2100: title_points = 10
            elif max_rating >= 1900: title_points = 8
            elif max_rating >= 1600: title_points = 6
            elif max_rating >= 1400: title_points = 4
            elif max_rating >= 1200: title_points = 2
            else: title_points = 0

        rating_component     = min(rating / 3500, 1) * 45
        max_rating_component = min(max_rating / 3500, 1) * 15
        title_component      = title_points
        solved_component     = min(solved / 3000, 1) * 20
        contest_component    = min(contests / 100, 1) * 10

        total = rating_component + max_rating_component + title_component + solved_component + contest_component

        breakdown = {
            "rating_score": {
                "raw_value": rating,
                "formula": f"MIN({rating}/3500,1)×45",
                "contribution": round(rating_component, 2),
                "weight": 0.45
            },
            "max_rating_score": {
                "raw_value": max_rating,
                "formula": f"MIN({max_rating}/3500,1)×15",
                "contribution": round(max_rating_component, 2),
                "weight": 0.15
            },
            "title_score": {
                "raw_value": title.title() or f"Inferred from rating ({max_rating})",
                "formula": f"MapTitleToPoints({title})",
                "contribution": round(title_component, 2),
                "weight": 0.10
            },
            "solved_score": {
                "raw_value": solved,
                "formula": f"MIN({solved}/3000,1)×20",
                "contribution": round(solved_component, 2),
                "weight": 0.20
            },
            "contest_score": {
                "raw_value": contests,
                "formula": f"MIN({contests}/100,1)×10",
                "contribution": round(contest_component, 2),
                "weight": 0.10
            }
        }
        return ExplainableScore(round(min(total, 100), 2), breakdown)
