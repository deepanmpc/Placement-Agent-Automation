from ..common import ScoreBreakdown, ExplainableScore

class SkillScoreRanker:
    WEIGHTS = {
        "programming": 0.50,
        "frameworks": 0.30,
        "tools": 0.20
    }
    MAX_EXPECTED = {
        "programming": 10,
        "frameworks": 5,
        "tools": 5
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
