import os
import json
from datetime import datetime
from typing import Optional

from executor_service.config import Config
from executor_service.schemas import TaskState, TaskStatus, ExecutionResult
from rich.console import Console

console = Console()


class ExecutionStateManager:
    """
    Persistent execution state backed by JSON files.
    Supports crash recovery and resumable execution.
    """

    def __init__(self):
        self._state: Optional[TaskState] = None

    def _state_path(self, task_id: str) -> str:
        return os.path.join(Config.TASK_STATE_DIR, f"{task_id}.json")

    def create_task(self, task_id: str, goal: str) -> TaskState:
        """Create a new task state and persist it."""
        self._state = TaskState(task_id=task_id, goal=goal)
        self._save()
        console.print(f"  [dim][State] Task created: {task_id}[/dim]")
        return self._state

    def get_state(self) -> Optional[TaskState]:
        """Return the current in-memory task state."""
        return self._state

    def load_task(self, task_id: str) -> Optional[TaskState]:
        """Load a task state from disk (crash recovery)."""
        path = self._state_path(task_id)
        if os.path.exists(path):
            with open(path, "r") as f:
                data = json.load(f)
            self._state = TaskState(**data)
            console.print(f"  [dim][State] Task loaded from disk: {task_id}[/dim]")
            return self._state
        return None

    def update_current_action(self, action_desc: str) -> None:
        """Update the currently executing action."""
        if self._state:
            self._state.current_action = action_desc
            self._state.last_updated = datetime.now().isoformat()
            self._save()

    def record_success(self, result: ExecutionResult) -> None:
        """Record a successfully completed action."""
        if self._state:
            self._state.completed_actions.append(result)
            self._state.current_action = None
            self._state.last_updated = datetime.now().isoformat()
            self._save()

    def record_failure(self, result: ExecutionResult) -> None:
        """Record a failed action."""
        if self._state:
            self._state.failed_actions.append(result)
            self._state.retry_count += 1
            self._state.last_updated = datetime.now().isoformat()
            self._save()

    def mark_completed(self) -> None:
        """Mark the task as completed."""
        if self._state:
            self._state.status = TaskStatus.COMPLETED
            self._state.last_updated = datetime.now().isoformat()
            self._save()
            console.print(f"  [bold green][State] Task completed: {self._state.task_id}[/bold green]")

    def mark_failed(self) -> None:
        """Mark the task as permanently failed."""
        if self._state:
            self._state.status = TaskStatus.FAILED
            self._state.last_updated = datetime.now().isoformat()
            self._save()

    def mark_cancelled(self) -> None:
        """Mark the task as cancelled."""
        if self._state:
            self._state.status = TaskStatus.CANCELLED
            self._state.last_updated = datetime.now().isoformat()
            self._save()

    def _save(self) -> None:
        """Persist current state to disk."""
        if self._state:
            path = self._state_path(self._state.task_id)
            with open(path, "w") as f:
                json.dump(self._state.model_dump(), f, indent=2)
