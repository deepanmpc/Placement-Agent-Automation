
from .common import ScoreBreakdown, ExplainableScore

class LeetCodeRanker:
    WEIGHTS = {
        "easy": 0.10, "medium": 0.20, "hard": 0.30,
        "rating": 0.20, "contest_count": 0.05,
        "acceptance": 0.05, "consistency": 0.05, "growth": 0.05
    }
    MAX_EXPECTED = {
        "easy": 1000, "medium": 1000, "hard": 300,
        "rating": 2500, "contest_count": 100,
        "acceptance": 100, "consistency": 100, "growth": 500
    }

    @classmethod
    def calculate(cls, data: dict) -> ExplainableScore:
        breakdowns = {}
        total = 0.0
        for key in cls.WEIGHTS.keys():
            raw = data.get(key, 0)
            b = ScoreBreakdown(key, raw, 0, cls.WEIGHTS[key], cls.MAX_EXPECTED[key])
            breakdowns[key] = b.to_dict()
            total += b.contribution
        
        return ExplainableScore(total, breakdowns)
