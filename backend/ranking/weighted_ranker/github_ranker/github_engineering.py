
from ..common import ScoreBreakdown, ExplainableScore

class GitHubEngineeringRanker:
    WEIGHTS = {
        "activity": 0.20, "repository": 0.20, "collaboration": 0.10,
        "commit_quality": 0.10, "documentation": 0.10, "portfolio": 0.15,
        "community": 0.05, "behavior": 0.10
    }
    MAX_EXPECTED = {k: 100 for k in WEIGHTS.keys()}

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
