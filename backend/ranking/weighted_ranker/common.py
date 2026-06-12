
from typing import Dict, Any

class ScoreBreakdown:
    def __init__(self, name: str, raw_value: Any, normalized_value: float, weight: float, max_expected: float = 1.0):
        self.name = name
        self.raw_value = raw_value
        
        # Robustly parse numeric value from raw_value
        val = 0.0
        if raw_value is not None:
            if isinstance(raw_value, str):
                import re
                match = re.search(r"[-+]?\d*\.\d+|\d+", raw_value)
                if match:
                    val = float(match.group())
            else:
                try:
                    val = float(raw_value)
                except (TypeError, ValueError):
                    pass
                    
        self.normalized_value = min(val / max_expected, 1.0) if max_expected > 0 else 0.0
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
