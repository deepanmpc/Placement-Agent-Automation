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
        CUSTOM_SCORE = Normalized weighted sum of all platforms
        """
        total_weight = lc_weight + cc_weight + cf_weight + gh_weight
        if total_weight <= 0:
            total_weight = 100.0
            lc_weight = cc_weight = cf_weight = gh_weight = 25.0

        lc_pct = lc_weight / total_weight
        cc_pct = cc_weight / total_weight
        cf_pct = cf_weight / total_weight
        gh_pct = gh_weight / total_weight

        total = (lc_score * lc_pct) + (cc_score * cc_pct) + \
                (cf_score * cf_pct) + (github_score * gh_pct)

        breakdown = {
            "leetcode":   {"raw_value": round(lc_score, 2), "weight_pct": round(lc_pct * 100, 2),
                           "formula": f"{round(lc_score,2)} × {lc_weight}",
                           "contribution": round(lc_score * lc_weight / 100, 2)},
            "codechef":   {"raw_value": round(cc_score, 2), "weight_pct": round(cc_pct * 100, 2),
                           "formula": f"{round(cc_score,2)} × {round(cc_pct, 2)}",
                           "contribution": round(cc_score * cc_pct, 2)},
            "codeforces": {"raw_value": round(cf_score, 2), "weight_pct": round(cf_pct * 100, 2),
                           "formula": f"{round(cf_score,2)} × {round(cf_pct, 2)}",
                           "contribution": round(cf_score * cf_pct, 2)},
            "github":     {"raw_value": round(github_score, 2), "weight_pct": round(gh_pct * 100, 2),
                           "formula": f"{round(github_score,2)} × {round(gh_pct, 2)}",
                           "contribution": round(github_score * gh_pct, 2)},
        }
        return ExplainableScore(round(max(0, min(total, 100)), 2), breakdown)
