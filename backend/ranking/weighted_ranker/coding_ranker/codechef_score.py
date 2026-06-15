"""
CodeChef Score Formula (0-100):
  StarScore: 1★=10, 2★=25, 3★=40, 4★=60, 5★=80, 6★=95, 7★=100
  CC_SCORE = (StarScore × 0.40)
           + MIN(CurrentRating / 3000, 1) × 20
           + MIN(HighestRating / 3000, 1) × 10
           + MIN(ProblemsSolved / 1000, 1) × 20
           + MIN(Contests / 50, 1) × 10
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

        rating         = _safe_int(data.get("rating") or 0)
        highest_rating = _safe_int(data.get("highest_rating") or rating)
        solved         = _safe_int(data.get("solved_count") or data.get("problems_solved", 0))
        contests       = _safe_int(data.get("contests") or data.get("contest_count", 0))

        star_component    = star_score * 0.40
        rating_component  = min(rating / 3000, 1) * 20
        highest_component = min(highest_rating / 3000, 1) * 10
        solved_component  = min(solved / 1000, 1) * 20
        contest_component = min(contests / 50, 1) * 10

        total = star_component + rating_component + highest_component + solved_component + contest_component

        breakdown = {
            "star_score": {
                "raw_value": f"{stars_int}★ → {star_score}",
                "formula": f"{star_score} × 0.40",
                "contribution": round(star_component, 2),
                "weight": 0.40
            },
            "rating_score": {
                "raw_value": rating,
                "formula": f"MIN({rating}/3000,1)×20",
                "contribution": round(rating_component, 2),
                "weight": 0.20
            },
            "highest_rating_score": {
                "raw_value": highest_rating,
                "formula": f"MIN({highest_rating}/3000,1)×10",
                "contribution": round(highest_component, 2),
                "weight": 0.10
            },
            "solved_score": {
                "raw_value": solved,
                "formula": f"MIN({solved}/1000,1)×20",
                "contribution": round(solved_component, 2),
                "weight": 0.20
            },
            "contest_score": {
                "raw_value": contests,
                "formula": f"MIN({contests}/50,1)×10",
                "contribution": round(contest_component, 2),
                "weight": 0.10
            }
        }
        return ExplainableScore(round(min(total, 100), 2), breakdown)
