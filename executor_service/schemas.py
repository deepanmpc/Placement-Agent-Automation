from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum
from datetime import datetime


class SafetyLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class ActionStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"


class TaskStatus(str, Enum):
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ExecutionResult(BaseModel):
    """Result of a single executed action."""
    action_type: str
    target: Optional[str] = None
    status: ActionStatus
    message: str
    duration_ms: float = 0.0
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class TaskState(BaseModel):
    """Persistent state for a running task."""
    task_id: str
    goal: str
    status: TaskStatus = TaskStatus.RUNNING
    current_action: Optional[str] = None
    completed_actions: List[ExecutionResult] = []
    failed_actions: List[ExecutionResult] = []
    retry_count: int = 0
    started_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    last_updated: str = Field(default_factory=lambda: datetime.now().isoformat())


class ExecutorActionInput(BaseModel):
    """
    Normalized action input consumed by the Executor.
    Maps 1:1 from PlannerOutput.Action but lives in executor domain.
    """
    action_type: str
    target: Optional[str] = None
    coordinates: Optional[List[int]] = None
    text: Optional[str] = None
    key: Optional[str] = None
    keys: Optional[List[str]] = None
    direction: Optional[str] = None      # for scroll: up/down/left/right
    amount: Optional[int] = None         # for scroll amount
    app_name: Optional[str] = None       # for launch/focus
    duration: Optional[float] = None     # for wait
    start_coords: Optional[List[int]] = None  # for drag
    end_coords: Optional[List[int]] = None    # for drag
    confidence: float = 1.0
    safety_level: SafetyLevel = SafetyLevel.LOW
