from ..common import ScoreBreakdown, ExplainableScore

class EducationScoreRanker:
    WEIGHTS = {
        "cgpa": 0.80,
        "prestige": 0.20
    }
    MAX_EXPECTED = {
        "cgpa": 10.0,
        "prestige": 100
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
