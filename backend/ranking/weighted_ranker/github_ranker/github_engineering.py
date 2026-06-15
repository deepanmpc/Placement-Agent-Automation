"""
GitHub Score Formula (0-100):
  GITHUB_SCORE = MIN(OriginalRepos/30,1)×10
               + MIN(ProjectDepth/50,1)×10
               + MIN(ActiveDays30/30,1)×10
               + MIN(TotalStars/500,1)×15
               + MIN(Followers/250,1)×5
               + MIN(CommitsLast365/1500,1)×15
               + (ContributionDays365/365)×15
               + MIN(MergedPRs/100,1)×10
               + MIN(IssuesClosed/100,1)×5
               + MIN(ActiveDays90/90,1)×5
"""
from ..common import ExplainableScore
import re


def _safe_num(val, default=0) -> float:
    if isinstance(val, (int, float)):
        return float(val)
    if isinstance(val, str):
        m = re.search(r'[\d.]+', val)
        return float(m.group()) if m else float(default)
    return float(default)


class GitHubEngineeringRanker:

    @classmethod
    def calculate(cls, data: dict) -> ExplainableScore:
        repos        = _safe_num(data.get("public_repos", 0))
        stars        = _safe_num(data.get("total_stars", 0))
        followers    = _safe_num(data.get("followers", 0))
        commits_365  = _safe_num(data.get("commits_last_365", data.get("commit_frequency", 0)) )
        contrib_days = _safe_num(data.get("contribution_days_365", data.get("contribution_consistency", 0)))
        merged_prs   = _safe_num(data.get("merged_prs", 0))
        issues_closed= _safe_num(data.get("issues_closed", 0))
        active90     = _safe_num(data.get("active_days_90", 0))
        
        orig_repos   = _safe_num(data.get("original_repos", repos))
        active30     = _safe_num(data.get("active_days_30", min(active90, 30)))
        proj_depth   = _safe_num(data.get("project_depth", 0))

        # Contribution days: if stored as a fraction (0-1), multiply by 365
        if 0 < contrib_days <= 1.0:
            contrib_days = contrib_days * 365

        orig_repo_score= min(orig_repos / 30, 1) * 10
        depth_score   = min(proj_depth / 50, 1) * 10
        momentum_score= min(active30 / 30, 1) * 10
        stars_score   = min(stars / 500, 1) * 15
        follow_score  = min(followers / 250, 1) * 5
        commit_score  = min(commits_365 / 1500, 1) * 15
        contrib_score = (contrib_days / 365) * 15
        pr_score      = min(merged_prs / 100, 1) * 10
        issue_score   = min(issues_closed / 100, 1) * 5
        active90_score= min(active90 / 90, 1) * 5

        total = orig_repo_score + depth_score + momentum_score + stars_score + follow_score + commit_score + contrib_score + pr_score + issue_score + active90_score

        breakdown = {
            "original_repos_score": {
                "raw_value": orig_repos,
                "formula": f"MIN({orig_repos}/30,1)×10",
                "contribution": round(orig_repo_score, 2),
                "weight": 0.10
            },
            "project_depth_score": {
                "raw_value": proj_depth,
                "formula": f"MIN({proj_depth}/50,1)×10",
                "contribution": round(depth_score, 2),
                "weight": 0.10
            },
            "momentum_score": {
                "raw_value": active30,
                "formula": f"MIN({active30}/30,1)×10",
                "contribution": round(momentum_score, 2),
                "weight": 0.10
            },
            "stars_score": {
                "raw_value": stars,
                "formula": f"MIN({stars}/500,1)×15",
                "contribution": round(stars_score, 2),
                "weight": 0.15
            },
            "followers_score": {
                "raw_value": followers,
                "formula": f"MIN({followers}/250,1)×5",
                "contribution": round(follow_score, 2),
                "weight": 0.05
            },
            "commits_score": {
                "raw_value": commits_365,
                "formula": f"MIN({commits_365}/1500,1)×15",
                "contribution": round(commit_score, 2),
                "weight": 0.15
            },
            "contribution_days_score": {
                "raw_value": round(contrib_days, 1),
                "formula": f"({round(contrib_days,1)}/365)×15",
                "contribution": round(contrib_score, 2),
                "weight": 0.15
            },
            "merged_prs_score": {
                "raw_value": merged_prs,
                "formula": f"MIN({merged_prs}/100,1)×10",
                "contribution": round(pr_score, 2),
                "weight": 0.10
            },
            "issues_score": {
                "raw_value": issues_closed,
                "formula": f"MIN({issues_closed}/100,1)×5",
                "contribution": round(issue_score, 2),
                "weight": 0.05
            },
            "activity_score": {
                "raw_value": active90,
                "formula": f"MIN({active90}/90,1)×5",
                "contribution": round(active90_score, 2),
                "weight": 0.05
            }
        }
        return ExplainableScore(round(min(total, 100), 2), breakdown)
