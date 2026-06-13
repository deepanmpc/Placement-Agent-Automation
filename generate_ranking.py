import os
import json

base_dir = "backend/ranking/weighted_ranker"

def create_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)

common_utils = """
from typing import Dict, Any

class ScoreBreakdown:
    def __init__(self, name: str, raw_value: float, normalized_value: float, weight: float, max_expected: float = 1.0):
        self.name = name
        self.raw_value = raw_value
        self.normalized_value = min(raw_value / max_expected, 1.0) if max_expected > 0 else 0.0
        self.weight = weight
        self.contribution = self.normalized_value * weight * 100

    def to_dict(self):
        return {
            "raw_value": self.raw_value,
            "normalized_value": round(self.normalized_value, 4),
            "weight": self.weight,
            "contribution": round(self.contribution, 2)
        }

class ExplainableScore:
    def __init__(self, total_score: float, breakdown: Dict[str, Any]):
        self.total_score = round(total_score, 2)
        self.breakdown = breakdown

    def to_dict(self):
        return {
            "total_score": self.total_score,
            "breakdown": self.breakdown
        }
"""

create_file(f"{base_dir}/__init__.py", "")
create_file(f"{base_dir}/common.py", common_utils)

leetcode_content = """
from .common import ScoreBreakdown, ExplainableScore

class LeetCodeRanker:
    WEIGHTS = {
        "easy": 0.10, "medium": 0.20, "hard": 0.30,
        "rating": 0.20, "contest_count": 0.05,
        "acceptance": 0.05, "consistency": 0.05, "growth": 0.05
    }
    MAX_EXPECTED = {
        "easy": 1000, "medium": 1000, "hard": 300,
        "rating": 2500, "contest_count": 100,
        "acceptance": 100, "consistency": 100, "growth": 500
    }

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
"""

cf_content = """
from .common import ScoreBreakdown, ExplainableScore

class CodeforcesRanker:
    WEIGHTS = {
        "rating": 0.35, "max_rating": 0.15, "contest_count": 0.15,
        "solved": 0.15, "consistency": 0.10, "growth": 0.10
    }
    MAX_EXPECTED = {
        "rating": 2400, "max_rating": 2600, "contest_count": 100,
        "solved": 3000, "consistency": 100, "growth": 500
    }

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
"""

cc_content = """
from .common import ScoreBreakdown, ExplainableScore

class CodeChefRanker:
    WEIGHTS = {
        "rating": 0.35, "stars": 0.15, "highest_rating": 0.15,
        "contest_count": 0.10, "solved_count": 0.10, "consistency": 0.10, "growth": 0.05
    }
    MAX_EXPECTED = {
        "rating": 2500, "stars": 7, "highest_rating": 2800,
        "contest_count": 100, "solved_count": 3000, "consistency": 100, "growth": 500
    }

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
"""

coding_agg_content = """
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
"""

create_file(f"{base_dir}/coding_ranker/__init__.py", "")
create_file(f"{base_dir}/coding_ranker/leetcode_score.py", leetcode_content)
create_file(f"{base_dir}/coding_ranker/codeforces_score.py", cf_content)
create_file(f"{base_dir}/coding_ranker/codechef_score.py", cc_content)
create_file(f"{base_dir}/coding_ranker/coding_aggregator.py", coding_agg_content)

github_eng_content = """
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
"""

create_file(f"{base_dir}/github_ranker/__init__.py", "")
create_file(f"{base_dir}/github_ranker/github_engineering.py", github_eng_content)
create_file(f"{base_dir}/github_ranker/github_behavior.py", "# Managed directly in rule_score or future expansion\\n")

resume_content = """
from ..common import ScoreBreakdown, ExplainableScore

class ResumeRanker:
    WEIGHTS = {
        "skills": 0.30, "projects": 0.35, "experience": 0.20,
        "certifications": 0.05, "achievements": 0.10
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
"""

create_file(f"{base_dir}/resume_ranker/__init__.py", "")
create_file(f"{base_dir}/resume_ranker/resume_aggregator.py", resume_content)

academic_content = """
from .common import ScoreBreakdown, ExplainableScore

class AcademicRanker:
    WEIGHTS = {
        "cgpa": 0.50, "aptitude": 0.30, "communication": 0.20
    }
    MAX_EXPECTED = {
        "cgpa": 10.0, "aptitude": 100, "communication": 100
    }

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
"""
create_file(f"{base_dir}/academic_score.py", academic_content)

rule_score_content = """
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
"""

create_file(f"{base_dir}/rule_score.py", rule_score_content)

print("Generated ranking files successfully.")
