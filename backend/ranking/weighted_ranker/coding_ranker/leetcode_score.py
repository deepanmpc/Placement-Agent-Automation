"""
LeetCode Score Formula (0-100):
  DifficultyPoints = (Easy × 1) + (Medium × 3) + (Hard × 8)
  DifficultyScore  = MIN(DifficultyPoints / 3000, 1) × 60
  ContestScore     = MIN(ContestRating / 2500, 1) × 25
  Participation    = MIN(ContestsAttended / 50, 1) × 5
  ActivityScore    = MIN(ActiveDays90 / 90, 1) × 10
  LC_SCORE = DifficultyScore + ContestScore + Participation + ActivityScore
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


class LeetCodeRanker:

    @classmethod
    def calculate(cls, data: dict) -> ExplainableScore:
        easy   = _safe_int(data.get("easy_solved",  data.get("easy", 0)))
        medium = _safe_int(data.get("medium_solved", data.get("medium", 0)))
        hard   = _safe_int(data.get("hard_solved",  data.get("hard", 0)))
        contest_rating  = _safe_int(data.get("rating", data.get("recent_contest_rating", 0)))
        contests        = _safe_int(data.get("contests_participated", data.get("contest_count", 0)))
        active_days_90  = _safe_int(data.get("active_days_90", 0))

        diff_points    = (easy * 1) + (medium * 3) + (hard * 8)
        difficulty_score  = min(diff_points / 3000, 1) * 60
        contest_score     = min(contest_rating / 2500, 1) * 25
        participation     = min(contests / 50, 1) * 5
        activity_score    = min(active_days_90 / 90, 1) * 10

        total = difficulty_score + contest_score + participation + activity_score

        breakdown = {
            "difficulty_score": {
                "raw_value": diff_points,
                "formula": f"({easy}×1)+({medium}×3)+({hard}×8) = {diff_points} → MIN({diff_points}/3000,1)×60",
                "contribution": round(difficulty_score, 2),
                "weight": 0.60
            },
            "contest_score": {
                "raw_value": contest_rating,
                "formula": f"MIN({contest_rating}/2500,1)×25",
                "contribution": round(contest_score, 2),
                "weight": 0.25
            },
            "participation_score": {
                "raw_value": contests,
                "formula": f"MIN({contests}/50,1)×5",
                "contribution": round(participation, 2),
                "weight": 0.05
            },
            "activity_score": {
                "raw_value": active_days_90,
                "formula": f"MIN({active_days_90}/90,1)×10",
                "contribution": round(activity_score, 2),
                "weight": 0.10
            }
        }
        return ExplainableScore(round(min(total, 100), 2), breakdown)
