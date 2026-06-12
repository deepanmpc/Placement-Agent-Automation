
from .common import ExplainableScore

class RuleScoreAggregator:
    CAPABILITY_WEIGHTS = {
        "coding": 0.35,
        "github": 0.25,
        "resume": 0.25,
        "academic": 0.15
    }
    
    BEHAVIOR_WEIGHTS = {
        "github_behavior": 0.40,
        "contest_consistency": 0.30,
        "rating_growth": 0.15,
        "activity_trend": 0.15
    }

    FINAL_WEIGHTS = {
        "capability": 0.75,
        "behavior": 0.25
    }

    @classmethod
    def calculate_capability(cls, coding: float, github: float, resume: float, academic: float) -> ExplainableScore:
        scores = {"coding": coding, "github": github, "resume": resume, "academic": academic}
        breakdowns = {}
        total = 0.0
        for k, val in scores.items():
            contrib = val * cls.CAPABILITY_WEIGHTS[k]
            total += contrib
            breakdowns[k] = {"raw_value": val, "weight": cls.CAPABILITY_WEIGHTS[k], "contribution": round(contrib, 2)}
        return ExplainableScore(total, breakdowns)

    @classmethod
    def calculate_behavior(cls, data: dict) -> ExplainableScore:
        breakdowns = {}
        total = 0.0
        for k, w in cls.BEHAVIOR_WEIGHTS.items():
            val = data.get(k, 0)
            # Assuming max 100 for behavioral raw values
            norm = min(val / 100.0, 1.0)
            contrib = norm * w * 100
            total += contrib
            breakdowns[k] = {"raw_value": val, "weight": w, "contribution": round(contrib, 2)}
        return ExplainableScore(total, breakdowns)

    @classmethod
    def calculate_final(cls, capability: ExplainableScore, behavior: ExplainableScore) -> ExplainableScore:
        cap_contrib = capability.total_score * cls.FINAL_WEIGHTS["capability"]
        beh_contrib = behavior.total_score * cls.FINAL_WEIGHTS["behavior"]
        total = cap_contrib + beh_contrib
        
        breakdowns = {
            "capability_score": {
                "raw_value": capability.total_score,
                "weight": cls.FINAL_WEIGHTS["capability"],
                "contribution": round(cap_contrib, 2),
                "details": capability.breakdown
            },
            "behavior_score": {
                "raw_value": behavior.total_score,
                "weight": cls.FINAL_WEIGHTS["behavior"],
                "contribution": round(beh_contrib, 2),
                "details": behavior.breakdown
            }
        }
        return ExplainableScore(total, breakdowns)
