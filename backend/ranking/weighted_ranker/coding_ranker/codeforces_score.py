"""
Codeforces Score Formula (0-100):
  CF_SCORE = MIN(CurrentRating / 3500, 1) × 50
           + MIN(MaxRating / 3500, 1) × 20
           + MIN(ProblemsSolved / 3000, 1) × 15
           + MIN(Contests / 100, 1) × 10
           + MIN(ActiveDays90 / 90, 1) × 5
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
        active90   = _safe_int(data.get("active_days_90", 0))

        rating_component     = min(rating / 3500, 1) * 50
        max_rating_component = min(max_rating / 3500, 1) * 20
        solved_component     = min(solved / 3000, 1) * 15
        contest_component    = min(contests / 100, 1) * 10
        activity_component   = min(active90 / 90, 1) * 5

        total = rating_component + max_rating_component + solved_component + contest_component + activity_component

        breakdown = {
            "rating_score": {
                "raw_value": rating,
                "formula": f"MIN({rating}/3500,1)×50",
                "contribution": round(rating_component, 2),
                "weight": 0.50
            },
            "max_rating_score": {
                "raw_value": max_rating,
                "formula": f"MIN({max_rating}/3500,1)×20",
                "contribution": round(max_rating_component, 2),
                "weight": 0.20
            },
            "solved_score": {
                "raw_value": solved,
                "formula": f"MIN({solved}/3000,1)×15",
                "contribution": round(solved_component, 2),
                "weight": 0.15
            },
            "contest_score": {
                "raw_value": contests,
                "formula": f"MIN({contests}/100,1)×10",
                "contribution": round(contest_component, 2),
                "weight": 0.10
            },
            "activity_score": {
                "raw_value": active90,
                "formula": f"MIN({active90}/90,1)×5",
                "contribution": round(activity_component, 2),
                "weight": 0.05
            }
        }
        return ExplainableScore(round(min(total, 100), 2), breakdown)
