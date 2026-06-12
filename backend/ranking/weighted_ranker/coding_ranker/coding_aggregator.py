
from .common import ExplainableScore

class CodingAggregator:
    WEIGHTS = {
        "leetcode": 0.50,
        "codeforces": 0.30,
        "codechef": 0.20
    }

    @classmethod
    def calculate(cls, lc_score: ExplainableScore, cf_score: ExplainableScore, cc_score: ExplainableScore) -> ExplainableScore:
        scores = {}
        if lc_score and lc_score.total_score > 0: scores["leetcode"] = lc_score.total_score
        if cf_score and cf_score.total_score > 0: scores["codeforces"] = cf_score.total_score
        if cc_score and cc_score.total_score > 0: scores["codechef"] = cc_score.total_score
        
        if not scores:
            return ExplainableScore(0.0, {})
            
        # Normalize weights based on available platforms
        total_weight = sum(cls.WEIGHTS[k] for k in scores.keys())
        
        breakdowns = {}
        final_score = 0.0
        for k, val in scores.items():
            adj_weight = cls.WEIGHTS[k] / total_weight
            contrib = val * adj_weight
            final_score += contrib
            breakdowns[k] = {
                "raw_value": val,
                "adjusted_weight": round(adj_weight, 4),
                "contribution": round(contrib, 2)
            }
            
        return ExplainableScore(final_score, breakdowns)
