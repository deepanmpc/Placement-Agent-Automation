
from ..common import ScoreBreakdown, ExplainableScore

class GitHubEngineeringRanker:
    WEIGHTS = {
        "activity_score": 0.20,
        "repository_score": 0.20,
        "collaboration_score": 0.15,
        "documentation_score": 0.15,
        "community_score": 0.10,
        "engineering_score": 0.20
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
