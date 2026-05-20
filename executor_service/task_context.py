from typing import Optional, List
from rich.console import Console

console = Console()


class TaskContext:
    """
    Holds the user's original goal persistently until success, cancellation, or failure.
    
    The task context is the single source of truth for:
    - What the user originally asked for
    - Current progress summary  
    - Pending sub-goals
    
    This context persists across retries, app launches, and navigation steps.
    """

    def __init__(self):
        self._goal: Optional[str] = None
        self._progress: str = "Not started"
        self._sub_goals: List[str] = []
        self._completed_sub_goals: List[str] = []

    def set_goal(self, goal: str) -> None:
        """Set the overarching user goal."""
        self._goal = goal
        self._progress = "Initialized"
        self._sub_goals = []
        self._completed_sub_goals = []
        console.print(f"  [dim][TaskContext] Goal set: {goal}[/dim]")

    @property
    def goal(self) -> Optional[str]:
        return self._goal

    @property
    def progress(self) -> str:
        return self._progress

    def update_progress(self, summary: str) -> None:
        """Update progress description."""
        self._progress = summary

    def add_sub_goals(self, sub_goals: List[str]) -> None:
        """Add sub-goals decomposed from the main goal."""
        self._sub_goals.extend(sub_goals)

    def complete_sub_goal(self, sub_goal: str) -> None:
        """Mark a sub-goal as completed."""
        if sub_goal in self._sub_goals:
            self._sub_goals.remove(sub_goal)
            self._completed_sub_goals.append(sub_goal)

    @property
    def pending_sub_goals(self) -> List[str]:
        return list(self._sub_goals)

    @property
    def is_active(self) -> bool:
        """Goal is active until explicitly cleared."""
        return self._goal is not None

    def clear(self) -> None:
        """Clear the task context after completion/cancellation."""
        self._goal = None
        self._progress = "Not started"
        self._sub_goals = []
        self._completed_sub_goals = []

    def to_dict(self) -> dict:
        return {
            "goal": self._goal,
            "progress": self._progress,
            "pending_sub_goals": self._sub_goals,
            "completed_sub_goals": self._completed_sub_goals,
        }
