import sys
import os
import traceback
import math

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from backend.ranking.weighted_ranker.coding_ranker.leetcode_score import LeetCodeRanker
from backend.ranking.weighted_ranker.coding_ranker.codeforces_score import CodeforcesRanker
from backend.ranking.weighted_ranker.coding_ranker.codechef_score import CodeChefRanker
from backend.ranking.weighted_ranker.coding_ranker.coding_aggregator import CodingAggregator
from backend.ranking.weighted_ranker.github_ranker.github_engineering import GitHubEngineeringRanker
from backend.ranking.weighted_ranker.rule_score import RuleScoreAggregator
from backend.ranking.weighted_ranker.common import ExplainableScore

# Mocks for Integration Tests
class MockModel:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
    def model_dump(self):
        return {k: v for k, v in self.__dict__.items() if not k.startswith('_')}

class MockGithubModel(MockModel):
    def __init__(self, github_strength=None, **kwargs):
        super().__init__(**kwargs)
        self.github_strength = github_strength

class MockStudentProfile:
    def __init__(self, leetcode=None, codeforces=None, codechef=None, github=None, metadata=None):
        self.leetcode = leetcode if leetcode is not None else MockModel()
        self.codeforces = codeforces if codeforces is not None else MockModel()
        self.codechef = codechef if codechef is not None else MockModel()
        self.github = github if github is not None else MockGithubModel()
        self.metadata = metadata if metadata is not None else MockModel(missing_platforms=[])
        self.ranking = None

def attach_ranking(profile, custom_weights: dict | None = None):
    """
    Extracted from backend.api.main to avoid FastAPI dependency.
    """
    lc = LeetCodeRanker.calculate(profile.leetcode.model_dump())
    cf = CodeforcesRanker.calculate(profile.codeforces.model_dump())
    cc = CodeChefRanker.calculate(profile.codechef.model_dump())

    # DSA aggregate: LC×0.33 + CC×0.34 + CF×0.33
    dsa = CodingAggregator.calculate(lc, cf, cc)

    # GitHub score
    gh_raw = profile.github.model_dump()
    if getattr(profile.github, 'github_strength', None):
        gh_raw.update(profile.github.github_strength.model_dump())
    gh = GitHubEngineeringRanker.calculate(gh_raw)

    # All three composite modes
    dsa_mode    = RuleScoreAggregator.calculate_dsa_mode(dsa.total_score, gh.total_score)
    github_mode = RuleScoreAggregator.calculate_github_mode(dsa.total_score, gh.total_score)

    cw = custom_weights or {}
    custom = RuleScoreAggregator.calculate_custom(
        lc_score=lc.total_score, cc_score=cc.total_score,
        cf_score=cf.total_score, github_score=gh.total_score,
        lc_weight=cw.get("lc", 25.0), cc_weight=cw.get("cc", 25.0),
        cf_weight=cw.get("cf", 25.0), gh_weight=cw.get("gh", 25.0),
    )

    profile.ranking = {
        "lc_score":  round(lc.total_score, 2),
        "cc_score":  round(cc.total_score, 2),
        "cf_score":  round(cf.total_score, 2),
        "dsa_score": round(dsa.total_score, 2),
        "github_score_total": round(gh.total_score, 2),
        "overall_dsa_mode":    round(dsa_mode.total_score, 2),
        "overall_github_mode": round(github_mode.total_score, 2),
        "custom_score":        round(custom.total_score, 2),
        "leetcode_score":   lc.to_dict(),
        "codechef_score":   cc.to_dict(),
        "codeforces_score": cf.to_dict(),
        "coding_score":     dsa.to_dict(),
        "github_score":     gh.to_dict(),
        "dsa_mode_breakdown":    dsa_mode.to_dict(),
        "github_mode_breakdown": github_mode.to_dict(),
        "custom_breakdown":      custom.to_dict(),
        "total_technical_score": round(dsa_mode.total_score, 2),
    }

passed_tests = 0
failed_tests = 0
failed_details = []

def run_test(test_name, test_func):
    global passed_tests, failed_tests
    try:
        test_func()
        print(f"✅ PASS: {test_name}")
        passed_tests += 1
    except AssertionError as e:
        print(f"❌ FAIL: {test_name} - {e}")
        failed_tests += 1
        failed_details.append(f"{test_name}: {e}")
    except Exception as e:
        print(f"❌ ERROR: {test_name} - {type(e).__name__}: {e}")
        traceback.print_exc(limit=2, file=sys.stdout)
        failed_tests += 1
        failed_details.append(f"{test_name}: {type(e).__name__} - {e}")

# ==========================================
# 1. LeetCodeRanker Unit Tests
# ==========================================
def test_leetcode_normal():
    data = {"easy": 100, "medium": 50, "hard": 20, "rating": 2000, "contests_participated": 30, "global_ranking": 50000}
    score = LeetCodeRanker.calculate(data)
    assert math.isclose(score.total_score, 63.95, abs_tol=0.1), f"Expected ~63.95, got {score.total_score}"

def test_leetcode_all_zeros():
    data = {"easy": 0, "medium": 0, "hard": 0, "rating": 0, "contests_participated": 0, "global_ranking": 0}
    score = LeetCodeRanker.calculate(data)
    assert score.total_score == 0.0

def test_leetcode_missing_keys():
    score1 = LeetCodeRanker.calculate({})
    assert score1.total_score == 0.0
    score2 = LeetCodeRanker.calculate({"easy": None, "rating": None})
    assert score2.total_score == 0.0

def test_leetcode_negative_numbers():
    data = {"easy": -10, "medium": -5, "rating": -100, "global_ranking": -50}
    score = LeetCodeRanker.calculate(data)
    assert score.total_score < 0.0

def test_leetcode_float_strings():
    data = {"easy": "100.5", "rating": "1,000"}
    score = LeetCodeRanker.calculate(data)
    assert score.breakdown["difficulty_score"]["raw_value"] == 100, "Expected string float to parse integer part 100"
    assert score.breakdown["contest_score"]["raw_value"] == 1, r"Expected '1,000' to parse as 1 (due to regex \d+ matching first group)"

def test_leetcode_extremely_large():
    data = {"easy": 9999, "rating": 9999, "global_ranking": 1}
    score = LeetCodeRanker.calculate(data)
    assert score.total_score <= 100.0

def test_leetcode_partial_data():
    data = {"easy": 50, "medium": 50}
    score = LeetCodeRanker.calculate(data)
    assert score.total_score > 0.0
    assert score.breakdown["contest_score"]["contribution"] == 0.0

def test_leetcode_zero_global_rank():
    data = {"global_ranking": 0}
    score = LeetCodeRanker.calculate(data)
    assert score.breakdown["global_rank_score"]["contribution"] == 0.0

def test_leetcode_mixed_keys():
    data1 = {"easy": 10}
    data2 = {"easy_solved": 10}
    assert LeetCodeRanker.calculate(data1).total_score == LeetCodeRanker.calculate(data2).total_score
    data3 = {"ranking": 1000}
    data4 = {"global_ranking": 1000}
    assert LeetCodeRanker.calculate(data3).total_score == LeetCodeRanker.calculate(data4).total_score

# ==========================================
# 2. CodeforcesRanker Unit Tests
# ==========================================
def test_codeforces_normal():
    data = {"rating": 1800, "max_rating": 2000, "rank": "candidate master", "solved": 500, "contests": 30}
    score = CodeforcesRanker.calculate(data)
    assert score.total_score > 0.0

def test_codeforces_missing_rank_inference():
    data = {"max_rating": 1900}
    score = CodeforcesRanker.calculate(data)
    assert score.breakdown["title_score"]["contribution"] == 8.0

def test_codeforces_empty_rank_string_bug8():
    data = {"max_rank": "", "rank": "", "max_rating": 2100}
    score = CodeforcesRanker.calculate(data)
    assert score.breakdown["title_score"]["contribution"] == 10.0, "Bug 8: Empty string rank should fallback to max_rating inference"

def test_codeforces_missing_both_ranks():
    data = {"max_rank": None, "rank": None, "max_rating": 1400}
    score = CodeforcesRanker.calculate(data)
    assert score.breakdown["title_score"]["contribution"] == 4.0

def test_codeforces_unrecognized_rank():
    data = {"max_rank": "supreme grandmaster", "max_rating": 3000}
    score = CodeforcesRanker.calculate(data)
    assert score.breakdown["title_score"]["contribution"] == 10.0

def test_codeforces_all_zeros():
    data = {"rating": 0, "max_rating": 0, "solved": 0, "contests": 0}
    assert CodeforcesRanker.calculate(data).total_score == 0.0

def test_codeforces_unsolved_only():
    data = {"solved": 1500}
    score = CodeforcesRanker.calculate(data)
    assert score.breakdown["solved_score"]["contribution"] == 10.0
    assert score.breakdown["contest_score"]["contribution"] == 0.0

def test_codeforces_max_rating_capping():
    data = {"rating": 4000, "max_rating": 4000, "solved": 5000, "contests": 200}
    score = CodeforcesRanker.calculate(data)
    assert score.total_score <= 100.0

# ==========================================
# 3. CodeChefRanker Unit Tests
# ==========================================
def test_codechef_all_stars():
    for stars in range(1, 8):
        data = {"stars": f"{stars}★"}
        score = CodeChefRanker.calculate(data)
        assert score.breakdown["star_score"]["contribution"] > 0

def test_codechef_zero_stars():
    data = {"stars": "0★"}
    score = CodeChefRanker.calculate(data)
    assert score.breakdown["star_score"]["contribution"] == 0.0

def test_codechef_invalid_stars():
    data = {"stars": "8★"}
    score = CodeChefRanker.calculate(data)
    assert score.breakdown["star_score"]["contribution"] == 0.0

def test_codechef_missing_stars():
    data = {}
    score = CodeChefRanker.calculate(data)
    assert score.breakdown["star_score"]["contribution"] == 0.0

def test_codechef_stars_types():
    assert CodeChefRanker.calculate({"stars": "3★"}).total_score == CodeChefRanker.calculate({"stars": 3}).total_score

def test_codechef_missing_highest_rating():
    data = {"rating": 2000}
    score = CodeChefRanker.calculate(data)
    assert math.isclose(score.breakdown["highest_rating_score"]["contribution"], (2000/3000)*10, abs_tol=0.1)

def test_codechef_highest_rating_zero():
    data = {"rating": 2000, "highest_rating": 0}
    score = CodeChefRanker.calculate(data)
    assert score.breakdown["highest_rating_score"]["contribution"] == 0.0

def test_codechef_capping():
    data = {"contests": 100, "solved_count": 2000, "rating": 4000, "stars": "7★"}
    score = CodeChefRanker.calculate(data)
    assert score.total_score <= 100.0

def test_codechef_normal():
    data = {"stars": "4★", "rating": 1800, "highest_rating": 2000, "solved_count": 400, "contests": 30}
    score = CodeChefRanker.calculate(data)
    assert score.total_score > 0

# ==========================================
# 4. GitHubEngineeringRanker Unit Tests
# ==========================================
def test_github_normal():
    data = {"public_repos": 10, "original_repos": 5, "total_stars": 20, "commits_last_365": 500, "contribution_days_365": 200, "merged_prs": 10, "issues_closed": 5, "active_days_90": 60, "active_days_30": 20, "project_depth": 25}
    score = GitHubEngineeringRanker.calculate(data)
    assert score.total_score > 0

def test_github_fresh_account():
    data = {"public_repos": 0, "original_repos": 0, "total_stars": 0, "commits_last_365": 0, "contribution_days_365": 0}
    assert GitHubEngineeringRanker.calculate(data).total_score == 0.0

def test_github_contrib_days_fraction():
    data = {"contribution_days_365": 1.0}
    score = GitHubEngineeringRanker.calculate(data)
    expected_if_bug_fixed = (1/365)*21
    assert math.isclose(score.breakdown["contribution_days_score"]["contribution"], expected_if_bug_fixed, abs_tol=0.1), "Bug 5: contrib_days=1 treated as 365 days instead of 1 day"

def test_github_contrib_days_others():
    data = {"contribution_days_365": 0.5}
    score = GitHubEngineeringRanker.calculate(data)
    assert math.isclose(score.breakdown["contribution_days_score"]["contribution"], (0.5*365/365)*21, abs_tol=0.1)

def test_github_active_days_missing():
    data = {"active_days_90": 60}
    score = GitHubEngineeringRanker.calculate(data)
    assert score.breakdown["momentum_score"]["raw_value"] == 30.0

def test_github_both_active_missing():
    data = {}
    score = GitHubEngineeringRanker.calculate(data)
    assert score.breakdown["momentum_score"]["raw_value"] == 0.0

def test_github_fallback_keys():
    data = {"commit_frequency": 100, "public_repos": 5}
    score = GitHubEngineeringRanker.calculate(data)
    assert score.breakdown["commits_score"]["raw_value"] == 100.0
    assert score.breakdown["original_repos_score"]["raw_value"] == 0.0, "Code does NOT fallback to public_repos for original_repos"

def test_github_very_high_values():
    data = {"total_stars": 10000, "original_repos": 500, "commits_last_365": 9999}
    score = GitHubEngineeringRanker.calculate(data)
    assert score.total_score <= 100.0

def test_github_all_none():
    data = {k: None for k in ["original_repos", "project_depth", "active_days_30", "total_stars", "commits_last_365", "contribution_days_365", "merged_prs", "issues_closed", "active_days_90"]}
    score = GitHubEngineeringRanker.calculate(data)
    assert score.total_score == 0.0

def test_github_mixed_types():
    data = {"total_stars": "100.5", "original_repos": "10 repos"}
    score = GitHubEngineeringRanker.calculate(data)
    assert score.breakdown["stars_score"]["raw_value"] == 100.5
    assert score.breakdown["original_repos_score"]["raw_value"] == 10.0

# ==========================================
# 5. CodingAggregator Tests
# ==========================================
def test_aggregator_all_three():
    lc = ExplainableScore(100, {})
    cf = ExplainableScore(100, {})
    cc = ExplainableScore(100, {})
    score = CodingAggregator.calculate(lc, cf, cc)
    assert math.isclose(score.total_score, 100.0, abs_tol=0.1)

def test_aggregator_only_one():
    lc = ExplainableScore(100, {})
    score = CodingAggregator.calculate(lc, None, None)
    assert math.isclose(score.total_score, 33.0, abs_tol=0.1)

def test_aggregator_all_none():
    score = CodingAggregator.calculate(None, None, None)
    assert score.total_score == 0.0

def test_aggregator_near_max():
    lc = ExplainableScore(99.9, {})
    cf = ExplainableScore(99.9, {})
    cc = ExplainableScore(99.9, {})
    score = CodingAggregator.calculate(lc, cf, cc)
    assert math.isclose(score.total_score, 99.9, abs_tol=0.1)

# ==========================================
# 6. RuleScoreAggregator Tests
# ==========================================
def test_rulescore_dsa_mode():
    score = RuleScoreAggregator.calculate_dsa_mode(100.0, 0.0)
    assert math.isclose(score.total_score, 60.0, abs_tol=0.1), f"Expected 60.0, got {score.total_score}"
    score2 = RuleScoreAggregator.calculate_dsa_mode(0.0, 100.0)
    assert math.isclose(score2.total_score, 40.0, abs_tol=0.1), f"Expected 40.0, got {score2.total_score}"
    score3 = RuleScoreAggregator.calculate_dsa_mode(0.0, 0.0)
    assert score3.total_score == 0.0

def test_rulescore_github_mode():
    score = RuleScoreAggregator.calculate_github_mode(100.0, 0.0)
    assert math.isclose(score.total_score, 40.0, abs_tol=0.1), f"Expected 40.0, got {score.total_score}"
    score2 = RuleScoreAggregator.calculate_github_mode(0.0, 100.0)
    assert math.isclose(score2.total_score, 60.0, abs_tol=0.1), f"Expected 60.0, got {score2.total_score}"

def test_rulescore_custom_unbalanced():
    score = RuleScoreAggregator.calculate_custom(100, 0, 0, 0, 100, 0, 0, 0)
    assert math.isclose(score.total_score, 100.0, abs_tol=0.1)

def test_rulescore_custom_sum_not_100():
    score = RuleScoreAggregator.calculate_custom(100, 100, 0, 0, 50, 50, 0, 0)
    assert math.isclose(score.total_score, 100.0, abs_tol=0.1)
    score2 = RuleScoreAggregator.calculate_custom(100, 100, 100, 100, 100, 100, 100, 100)
    assert math.isclose(score2.total_score, 100.0, abs_tol=0.1)

def test_rulescore_custom_negative():
    score = RuleScoreAggregator.calculate_custom(100, 100, 100, 100, -50, 50, 50, 50)
    assert math.isclose(score.total_score, 100.0, abs_tol=0.1)

def test_rulescore_custom_float():
    score = RuleScoreAggregator.calculate_custom(100, 100, 100, 100, 25.5, 24.5, 25.0, 25.0)
    assert math.isclose(score.total_score, 100.0, abs_tol=0.1)

# ==========================================
# 7. Integration Tests (attach_ranking)
# ==========================================
def test_integration_all_populated():
    profile = MockStudentProfile()
    profile.leetcode = MockModel(easy=10)
    profile.github = MockGithubModel(public_repos=10, github_strength=MockModel(project_depth=5))
    attach_ranking(profile)
    assert profile.ranking is not None
    assert "dsa_score" in profile.ranking
    assert "github_score_total" in profile.ranking

def test_integration_no_platforms():
    profile = MockStudentProfile()
    attach_ranking(profile)
    assert profile.ranking["dsa_score"] == 0.0
    assert profile.ranking["github_score_total"] == 0.0

def test_integration_only_github():
    profile = MockStudentProfile()
    profile.github = MockGithubModel(public_repos=100, commits_last_365=2000)
    attach_ranking(profile)
    assert profile.ranking["dsa_score"] == 0.0
    assert profile.ranking["github_score_total"] > 0.0

def test_integration_bug3_silent_failure():
    profile = MockStudentProfile(leetcode=None)
    attach_ranking(profile)
    assert profile.ranking is not None, "Bug 3: attach_ranking crashed and didn't set ranking"

def test_integration_github_strength_none():
    profile = MockStudentProfile()
    profile.github = MockGithubModel(github_strength=None)
    attach_ranking(profile)
    assert profile.ranking is not None

def test_integration_missing_platforms_reported():
    profile = MockStudentProfile()
    profile.metadata = MockModel(missing_platforms=["leetcode", "github"])
    attach_ranking(profile)
    assert "missing_platforms" in profile.ranking, "Expected attach_ranking to correctly report missing_platforms from metadata"

def test_integration_custom_weights_none():
    profile = MockStudentProfile()
    attach_ranking(profile, custom_weights=None)
    assert profile.ranking["custom_score"] == 0.0

def test_integration_custom_weights_partial():
    profile = MockStudentProfile()
    attach_ranking(profile, custom_weights={"lc": 50})
    assert profile.ranking["custom_score"] == 0.0

# ==========================================
# 8. Docstring vs Code Mismatch Tests
# ==========================================
def test_mismatch_leetcode_docstring():
    data = {"easy": 1500, "rating": 2500, "contests_participated": 50, "global_ranking": 1}
    score = LeetCodeRanker.calculate(data)
    assert score.breakdown["difficulty_score"]["weight"] == 0.30
    assert score.breakdown["contest_score"]["weight"] == 0.30
    assert score.breakdown["participation_score"]["weight"] == 0.20
    assert score.breakdown["global_rank_score"]["weight"] == 0.20

def test_mismatch_codechef_docstring():
    data = {"stars": "7★"}
    score = CodeChefRanker.calculate(data)
    assert score.breakdown["star_score"]["weight"] == 0.10
    assert score.breakdown["star_score"]["contribution"] == 10.0

def test_mismatch_docs_instructions_formula():
    data = {"easy": 100}
    score = LeetCodeRanker.calculate(data)
    assert not math.isclose(score.total_score, 20.0, abs_tol=0.1), "Formula mismatch"
    assert math.isclose(score.total_score, 2.0, abs_tol=0.1)

# ==========================================
# 9. Formula Boundary Tests
# ==========================================
def test_boundaries_leetcode_max():
    data = {"easy": 1500, "rating": 2500, "contests_participated": 50, "global_ranking": 1}
    score = LeetCodeRanker.calculate(data)
    assert score.total_score == 100.0

def test_boundaries_codeforces_max():
    data = {"rating": 3500, "max_rating": 3500, "max_rank": "grandmaster", "solved_count": 3000, "contests": 100}
    score = CodeforcesRanker.calculate(data)
    assert score.total_score == 100.0

def test_boundaries_codechef_max():
    data = {"stars": "7★", "rating": 3000, "highest_rating": 3000, "solved_count": 1000, "contests": 50}
    score = CodeChefRanker.calculate(data)
    assert score.total_score == 100.0

def test_boundaries_github_max():
    data = {"original_repos": 30, "project_depth": 50, "active_days_30": 30, "total_stars": 30, "commits_last_365": 1500, "contribution_days_365": 365, "merged_prs": 15, "issues_closed": 20, "active_days_90": 90}
    score = GitHubEngineeringRanker.calculate(data)
    assert score.total_score == 100.0

def test_boundaries_all_min():
    assert LeetCodeRanker.calculate({}).total_score == 0.0
    assert CodeforcesRanker.calculate({}).total_score == 0.0
    assert CodeChefRanker.calculate({}).total_score == 0.0
    assert GitHubEngineeringRanker.calculate({}).total_score == 0.0

# ==========================================
# 10. Edge Case Scoring Scenarios
# ==========================================
def test_scenario_new_student():
    profile = MockStudentProfile()
    attach_ranking(profile)
    assert profile.ranking["lc_score"] == 0.0
    assert profile.ranking["dsa_score"] == 0.0
    assert profile.ranking["github_score_total"] == 0.0

def test_scenario_leetcode_only():
    profile = MockStudentProfile()
    profile.leetcode = MockModel(easy=1500, rating=2500, contests_participated=50, global_ranking=1)
    attach_ranking(profile)
    assert profile.ranking["lc_score"] == 100.0
    assert math.isclose(profile.ranking["dsa_score"], 33.0, abs_tol=0.1)
    assert profile.ranking["github_score_total"] == 0.0
    assert math.isclose(profile.ranking["overall_dsa_mode"], 33.0 * 0.6, abs_tol=0.1)

def test_scenario_superstar():
    profile = MockStudentProfile()
    profile.leetcode = MockModel(easy=1500, rating=2500, contests_participated=50, global_ranking=1)
    profile.codeforces = MockModel(rating=3500, max_rating=3500, max_rank="grandmaster", solved_count=3000, contests=100)
    profile.codechef = MockModel(stars="7★", rating=3000, highest_rating=3000, solved_count=1000, contests=50)
    profile.github = MockGithubModel(original_repos=30, project_depth=50, active_days_30=30, total_stars=30, commits_last_365=1500, contribution_days_365=365, merged_prs=15, issues_closed=20, active_days_90=90)
    attach_ranking(profile)
    assert profile.ranking["lc_score"] == 100.0
    assert profile.ranking["cc_score"] == 100.0
    assert profile.ranking["cf_score"] == 100.0
    assert profile.ranking["github_score_total"] == 100.0
    assert profile.ranking["dsa_score"] == 100.0
    assert profile.ranking["overall_dsa_mode"] == 100.0

def test_scenario_huge_rank():
    data = {"global_ranking": 3500000}
    score = LeetCodeRanker.calculate(data)
    assert math.isclose(score.breakdown["global_rank_score"]["contribution"], 2.5, abs_tol=0.1)

if __name__ == "__main__":
    tests = [
        test_leetcode_normal, test_leetcode_all_zeros, test_leetcode_missing_keys, test_leetcode_negative_numbers, test_leetcode_float_strings, test_leetcode_extremely_large, test_leetcode_partial_data, test_leetcode_zero_global_rank, test_leetcode_mixed_keys,
        test_codeforces_normal, test_codeforces_missing_rank_inference, test_codeforces_empty_rank_string_bug8, test_codeforces_missing_both_ranks, test_codeforces_unrecognized_rank, test_codeforces_all_zeros, test_codeforces_unsolved_only, test_codeforces_max_rating_capping,
        test_codechef_all_stars, test_codechef_zero_stars, test_codechef_invalid_stars, test_codechef_missing_stars, test_codechef_stars_types, test_codechef_missing_highest_rating, test_codechef_highest_rating_zero, test_codechef_capping, test_codechef_normal,
        test_github_normal, test_github_fresh_account, test_github_contrib_days_fraction, test_github_contrib_days_others, test_github_active_days_missing, test_github_both_active_missing, test_github_fallback_keys, test_github_very_high_values, test_github_all_none, test_github_mixed_types,
        test_aggregator_all_three, test_aggregator_only_one, test_aggregator_all_none, test_aggregator_near_max,
        test_rulescore_dsa_mode, test_rulescore_github_mode, test_rulescore_custom_unbalanced, test_rulescore_custom_sum_not_100, test_rulescore_custom_negative, test_rulescore_custom_float,
        test_integration_all_populated, test_integration_no_platforms, test_integration_only_github, test_integration_bug3_silent_failure, test_integration_github_strength_none, test_integration_missing_platforms_reported, test_integration_custom_weights_none, test_integration_custom_weights_partial,
        test_mismatch_leetcode_docstring, test_mismatch_codechef_docstring, test_mismatch_docs_instructions_formula,
        test_boundaries_leetcode_max, test_boundaries_codeforces_max, test_boundaries_codechef_max, test_boundaries_github_max, test_boundaries_all_min,
        test_scenario_new_student, test_scenario_leetcode_only, test_scenario_superstar, test_scenario_huge_rank
    ]

    print("="*50)
    print("SCORING ENGINE COMPREHENSIVE TESTS")
    print("="*50)

    for t in tests:
        run_test(t.__name__, t)
    
    print("\n" + "="*50)
    print(f"RESULTS: {passed_tests} PASSED, {failed_tests} FAILED")
    print("="*50)
    if failed_details:
        print("Failures:")
        for fd in failed_details:
            print("  - " + fd)

