"""
LeetCode Score Formula (0-100):
  DifficultyPoints = (Easy × 1) + (Medium × 3) + (Hard × 8)
  DifficultyScore  = MIN(DifficultyPoints / 1500, 1) × 30
  ContestScore     = MIN(ContestRating / 2500, 1) × 30
  Participation    = MIN(ContestsAttended / 50, 1) × 20
  GlobalRankScore  = MAX(0, (4,000,000 - GlobalRank) / 4,000,000) × 20
  LC_SCORE = DifficultyScore + ContestScore + Participation + GlobalRankScore
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
        easy   = _safe_int(data.get("easy_solved", data.get("easy", 0)))
        medium = _safe_int(data.get("medium_solved", data.get("medium", 0)))
        hard   = _safe_int(data.get("hard_solved", data.get("hard", 0)))
        contest_rating  = _safe_int(data.get("rating", data.get("recent_contest_rating", 0)))
        contests        = _safe_int(data.get("contests_participated", data.get("contest_count", 0)))
        global_rank     = _safe_int(data.get("global_ranking", data.get("ranking", 0)))

        diff_points    = (easy * 1) + (medium * 3) + (hard * 8)
        difficulty_score  = min(diff_points / 1500, 1) * 30
        contest_score     = min(contest_rating / 2500, 1) * 30
        participation     = min(contests / 50, 1) * 20
        
        rank_score = 0
        if global_rank > 0:
            rank_score = max(0, (4000000 - global_rank) / 4000000) * 20

        total = difficulty_score + contest_score + participation + rank_score

        breakdown = {
            "difficulty_score": {
                "raw_value": diff_points,
                "formula": f"({easy}×1)+({medium}×3)+({hard}×8) = {diff_points} → MIN({diff_points}/1500,1)×30",
                "contribution": round(difficulty_score, 2),
                "weight": 0.30
            },
            "contest_score": {
                "raw_value": contest_rating,
                "formula": f"MIN({contest_rating}/2500,1)×30",
                "contribution": round(contest_score, 2),
                "weight": 0.30
            },
            "participation_score": {
                "raw_value": contests,
                "formula": f"MIN({contests}/50,1)×20",
                "contribution": round(participation, 2),
                "weight": 0.20
            },
            "global_rank_score": {
                "raw_value": global_rank or "Unranked",
                "formula": f"MAX(0, (4M - {global_rank})/4M) × 20",
                "contribution": round(rank_score, 2),
                "weight": 0.20
            }
        }
        return ExplainableScore(round(min(total, 100), 2), breakdown)
