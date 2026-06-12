from ..common import ScoreBreakdown, ExplainableScore

class ProjectScoreRanker:
    WEIGHTS = {
        "count": 0.40,
        "technologies_used": 0.30,
        "duration": 0.30
    }
    MAX_EXPECTED = {
        "count": 5,
        "technologies_used": 10,
        "duration": 12 # months
    }

    @classmethod
    def calculate(cls, data: dict) -> ExplainableScore:
        breakdowns = {}
        total = 0.0
        for key, weight in cls.WEIGHTS.items():
            raw = data.get(key, 0)
            b = ScoreBreakdown(key, raw, 0, weight, cls.MAX_EXPECTED[key])
            breakdowns[key] = b.to_dict()
            total += b.contribution
        return ExplainableScore(total, breakdowns)
