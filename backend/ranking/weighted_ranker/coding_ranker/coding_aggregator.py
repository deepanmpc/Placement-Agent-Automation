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
        available = {}
        if lc_score and lc_score.total_score > 0:
            available["leetcode"] = lc_score.total_score
        if cc_score and cc_score.total_score > 0:
            available["codechef"] = cc_score.total_score
        if cf_score and cf_score.total_score > 0:
            available["codeforces"] = cf_score.total_score

        if not available:
            return ExplainableScore(0.0, {})

        # Normalize weights to available platforms
        total_weight = sum(cls.WEIGHTS[k] for k in available)
        breakdowns = {}
        final_score = 0.0

        for k, val in available.items():
            adj_weight = cls.WEIGHTS[k] / total_weight
            contrib = val * adj_weight
            final_score += contrib
            breakdowns[k] = {
                "raw_value": round(val, 2),
                "fixed_weight": cls.WEIGHTS[k],
                "adjusted_weight": round(adj_weight, 4),
                "formula": f"{round(val,2)} × {round(adj_weight,4)}",
                "contribution": round(contrib, 2)
            }

        return ExplainableScore(round(min(final_score, 100), 2), breakdowns)
