from ..common import ScoreBreakdown, ExplainableScore

class CodeforcesRanker:
    WEIGHTS = {
        "rating": 0.35, "max_rating": 0.15, "contest_count": 0.15,
        "solved": 0.15, "consistency": 0.10, "growth": 0.10
    }
    MAX_EXPECTED = {
        "rating": 2400, "max_rating": 2600, "contest_count": 100,
        "solved": 3000, "consistency": 100, "growth": 500
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
