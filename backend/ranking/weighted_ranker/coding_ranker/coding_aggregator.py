"""
DSA Score Aggregator:
  DSA_SCORE = LC_SCORE×0.33 + CC_SCORE×0.34 + CF_SCORE×0.33
"""
from ..common import ExplainableScore


class CodingAggregator:
    # Fixed weights as per specification
    WEIGHTS = {
        "leetcode":   0.33,
        "codechef":   0.34,
        "codeforces": 0.33,
    }

    @classmethod
    def calculate(
        cls,
        lc_score: ExplainableScore,
        cf_score: ExplainableScore,
        cc_score: ExplainableScore
    ) -> ExplainableScore:
        
        scores = {
            "leetcode":   lc_score.total_score if lc_score else 0.0,
            "codechef":   cc_score.total_score if cc_score else 0.0,
            "codeforces": cf_score.total_score if cf_score else 0.0,
        }

        breakdowns = {}
        final_score = 0.0

        for k, val in scores.items():
            fixed_weight = cls.WEIGHTS[k]
            contrib = val * fixed_weight
            final_score += contrib
            breakdowns[k] = {
                "raw_value": round(val, 2),
                "fixed_weight": fixed_weight,
                "adjusted_weight": fixed_weight,
                "formula": f"{round(val,2)} × {fixed_weight}",
                "contribution": round(contrib, 2)
            }

        return ExplainableScore(round(min(final_score, 100), 2), breakdowns)
