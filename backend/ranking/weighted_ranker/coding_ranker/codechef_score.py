"""
CodeChef Score Formula (0-100):
  StarScore: 1★=10, 2★=25, 3★=40, 4★=60, 5★=80, 6★=95, 7★=100
  CC_SCORE = (StarScore × 0.40)
           + MIN(Rating / 3000, 1) × 30
           + MIN(ProblemsSolved / 1000, 1) × 15
           + MIN(Contests / 50, 1) × 10
           + MIN(ActiveDays90 / 90, 1) × 5
"""
from ..common import ExplainableScore
import re


STAR_MAP = {1: 10, 2: 25, 3: 40, 4: 60, 5: 80, 6: 95, 7: 100}


def _safe_int(val) -> int:
    if isinstance(val, (int, float)):
        return int(val)
    if isinstance(val, str):
        m = re.search(r'\d+', val)
        return int(m.group()) if m else 0
    return 0


def _stars_to_int(val) -> int:
    if isinstance(val, int):
        return val
    if isinstance(val, str):
        m = re.search(r'\d+', val)
        return int(m.group()) if m else 0
    return 0


class CodeChefRanker:

    @classmethod
    def calculate(cls, data: dict) -> ExplainableScore:
        stars_raw  = data.get("stars", "0")
        stars_int  = _stars_to_int(stars_raw)
        star_score = STAR_MAP.get(stars_int, 0)

        rating   = _safe_int(data.get("rating", 0))
        solved   = _safe_int(data.get("solved_count", data.get("problems_solved", 0)))
        contests = _safe_int(data.get("contests", data.get("contest_count", 0)))
        active90 = _safe_int(data.get("active_days_90", 0))

        star_component    = star_score * 0.40
        rating_component  = min(rating / 3000, 1) * 30
        solved_component  = min(solved / 1000, 1) * 15
        contest_component = min(contests / 50, 1) * 10
        activity_component= min(active90 / 90, 1) * 5

        total = star_component + rating_component + solved_component + contest_component + activity_component

        breakdown = {
            "star_score": {
                "raw_value": f"{stars_int}★ → {star_score}",
                "formula": f"{star_score} × 0.40",
                "contribution": round(star_component, 2),
                "weight": 0.40
            },
            "rating_score": {
                "raw_value": rating,
                "formula": f"MIN({rating}/3000,1)×30",
                "contribution": round(rating_component, 2),
                "weight": 0.30
            },
            "solved_score": {
                "raw_value": solved,
                "formula": f"MIN({solved}/1000,1)×15",
                "contribution": round(solved_component, 2),
                "weight": 0.15
            },
            "contest_score": {
                "raw_value": contests,
                "formula": f"MIN({contests}/50,1)×10",
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
