
from .common import ScoreBreakdown, ExplainableScore

class AcademicRanker:
    WEIGHTS = {
        "cgpa": 0.50, "aptitude": 0.30, "communication": 0.20
    }
    MAX_EXPECTED = {
        "cgpa": 10.0, "aptitude": 100, "communication": 100
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
