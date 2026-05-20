import os
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from rich.console import Console

from verifier_service.config import Config
from verifier_service.schemas import VerificationResult

console = Console()


class VerificationMemory:
    """
    Store verification history for learning and replay.
    Tracks successful patterns, failure signatures, and recovery outcomes.
    """

    def __init__(self):
        self._history: List[Dict[str, Any]] = []
        self._failure_patterns: List[Dict[str, Any]] = []
        self._successful_recoveries: List[Dict[str, Any]] = []

    def record_verification(self, result: VerificationResult, action: Dict[str, Any]) -> None:
        """Store a verification result."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "success": result.success,
            "confidence": result.confidence,
            "reason": result.verification_reason,
            "recommendation": result.next_recommendation.value,
        }
        self._history.append(entry)

        # Track failure patterns
        if not result.success and result.failure_report:
            self._failure_patterns.append({
                "action_type": action.get("action_type", ""),
                "failure_type": result.failure_report.failure_type.value,
                "severity": result.failure_report.severity.value,
                "description": result.failure_report.description,
            })

    def record_recovery(self, action: str, recovery: str, succeeded: bool) -> None:
        """Record whether a recovery strategy worked."""
        self._successful_recoveries.append({
            "timestamp": datetime.now().isoformat(),
            "failed_action": action,
            "recovery": recovery,
            "succeeded": succeeded,
        })

    def get_recent_failures(self, n: int = 5) -> List[Dict[str, Any]]:
        """Get the N most recent failure patterns."""
        return self._failure_patterns[-n:]

    def get_success_rate(self) -> float:
        """Overall verification success rate."""
        if not self._history:
            return 1.0
        successes = sum(1 for e in self._history if e["success"])
        return successes / len(self._history)

    def save_to_disk(self, task_id: str) -> None:
        """Persist verification history to JSON."""
        filename = f"{task_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        path = os.path.join(Config.VERIFICATION_HISTORY_DIR, filename)
        data = {
            "history": self._history,
            "failure_patterns": self._failure_patterns,
            "recoveries": self._successful_recoveries,
            "success_rate": self.get_success_rate(),
        }
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
        console.print(f"  [dim][Memory] Saved verification history: {filename}[/dim]")

    def clear(self) -> None:
        """Reset memory for a new task."""
        self._history.clear()
        self._failure_patterns.clear()
        self._successful_recoveries.clear()
