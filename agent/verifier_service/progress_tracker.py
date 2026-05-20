from typing import List, Dict, Any
from rich.console import Console

console = Console()


class ProgressTracker:
    """
    Track long-running task progress with milestone tracking.
    """

    def __init__(self):
        self._milestones: List[str] = []
        self._completed_milestones: List[str] = []
        self._progress_log: List[Dict[str, Any]] = []

    def reset(self):
        """Clear tracker for a new task."""
        self._milestones.clear()
        self._completed_milestones.clear()
        self._progress_log.clear()

    def record_progress(self, action: str, success: bool, detail: str = "") -> None:
        """Record a step in the progress log."""
        entry = {"action": action, "success": success, "detail": detail}
        self._progress_log.append(entry)
        if success and detail:
            self._completed_milestones.append(detail)

    def add_milestones(self, milestones: List[str]) -> None:
        """Set expected milestones for the current goal."""
        self._milestones.extend(milestones)

    def get_progress_summary(self) -> str:
        """Return a human-readable progress summary."""
        total_actions = len(self._progress_log)
        successes = sum(1 for e in self._progress_log if e["success"])
        failures = total_actions - successes

        parts = [f"Actions: {total_actions} (✓{successes} ✗{failures})"]
        if self._completed_milestones:
            parts.append(f"Milestones: {', '.join(self._completed_milestones[-3:])}")
        return " | ".join(parts)

    @property
    def success_rate(self) -> float:
        """Ratio of successful actions."""
        if not self._progress_log:
            return 1.0
        successes = sum(1 for e in self._progress_log if e["success"])
        return successes / len(self._progress_log)

    @property
    def total_actions(self) -> int:
        return len(self._progress_log)

    @property
    def consecutive_failures(self) -> int:
        """Count consecutive failures from the end."""
        count = 0
        for entry in reversed(self._progress_log):
            if not entry["success"]:
                count += 1
            else:
                break
        return count
