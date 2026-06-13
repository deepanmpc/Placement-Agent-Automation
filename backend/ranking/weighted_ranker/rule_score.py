"""
Score Aggregation Modes:
  OVERALL_GITHUB_MODE = (GITHUB_SCORE × 0.60) + (DSA_SCORE × 0.40)
  OVERALL_DSA_MODE    = (DSA_SCORE × 0.60) + (GITHUB_SCORE × 0.40)
  CUSTOM_SCORE        = (LC×LC_W + CC×CC_W + CF×CF_W + GH×GH_W) / 100
"""
from .common import ExplainableScore


class RuleScoreAggregator:

    @classmethod
    def calculate_dsa_mode(cls, dsa_score: float, github_score: float) -> ExplainableScore:
        """
        OVERALL_DSA_MODE = (DSA_SCORE × 0.60) + (GITHUB_SCORE × 0.40)
        """
        dsa_contrib = dsa_score * 0.60
        gh_contrib  = github_score * 0.40
        total = dsa_contrib + gh_contrib
        breakdown = {
            "dsa_score":    {"raw_value": round(dsa_score, 2), "weight": 0.60, "contribution": round(dsa_contrib, 2),
                             "formula": f"{round(dsa_score,2)} × 0.60"},
            "github_score": {"raw_value": round(github_score, 2), "weight": 0.40, "contribution": round(gh_contrib, 2),
                             "formula": f"{round(github_score,2)} × 0.40"},
        }
        return ExplainableScore(round(min(total, 100), 2), breakdown)

    @classmethod
    def calculate_github_mode(cls, dsa_score: float, github_score: float) -> ExplainableScore:
        """
        OVERALL_GITHUB_MODE = (GITHUB_SCORE × 0.60) + (DSA_SCORE × 0.40)
        """
        gh_contrib  = github_score * 0.60
        dsa_contrib = dsa_score * 0.40
        total = gh_contrib + dsa_contrib
        breakdown = {
            "github_score": {"raw_value": round(github_score, 2), "weight": 0.60, "contribution": round(gh_contrib, 2),
                             "formula": f"{round(github_score,2)} × 0.60"},
            "dsa_score":    {"raw_value": round(dsa_score, 2), "weight": 0.40, "contribution": round(dsa_contrib, 2),
                             "formula": f"{round(dsa_score,2)} × 0.40"},
        }
        return ExplainableScore(round(min(total, 100), 2), breakdown)

    @classmethod
    def calculate_custom(
        cls,
        lc_score: float, cc_score: float, cf_score: float, github_score: float,
        lc_weight: float = 25.0, cc_weight: float = 25.0,
        cf_weight: float = 25.0, gh_weight: float = 25.0
    ) -> ExplainableScore:
        """
        CUSTOM_SCORE = (LC×LC_W + CC×CC_W + CF×CF_W + GH×GH_W) / 100
        Weights are in percentage (sum to 100).
        """
        numerator = (lc_score * lc_weight) + (cc_score * cc_weight) + \
                    (cf_score * cf_weight) + (github_score * gh_weight)
        total = numerator / 100.0
        breakdown = {
            "leetcode":   {"raw_value": round(lc_score, 2), "weight_pct": lc_weight,
                           "formula": f"{round(lc_score,2)} × {lc_weight}",
                           "contribution": round(lc_score * lc_weight / 100, 2)},
            "codechef":   {"raw_value": round(cc_score, 2), "weight_pct": cc_weight,
                           "formula": f"{round(cc_score,2)} × {cc_weight}",
                           "contribution": round(cc_score * cc_weight / 100, 2)},
            "codeforces": {"raw_value": round(cf_score, 2), "weight_pct": cf_weight,
                           "formula": f"{round(cf_score,2)} × {cf_weight}",
                           "contribution": round(cf_score * cf_weight / 100, 2)},
            "github":     {"raw_value": round(github_score, 2), "weight_pct": gh_weight,
                           "formula": f"{round(github_score,2)} × {gh_weight}",
                           "contribution": round(github_score * gh_weight / 100, 2)},
        }
        return ExplainableScore(round(min(total, 100), 2), breakdown)
