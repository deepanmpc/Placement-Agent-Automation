from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime


class VerificationStatus(str, Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    PARTIAL = "partial"
    UNKNOWN = "unknown"


class FailureType(str, Enum):
    NO_CHANGE = "no_ui_change"
    ERROR_DIALOG = "error_dialog"
    WRONG_ELEMENT = "wrong_element"
    LOADING_STUCK = "loading_stuck"
    MODAL_BLOCKING = "modal_blocking"
    PERMISSION_POPUP = "permission_popup"
    LOGIN_REQUIRED = "login_required"
    APP_CRASH = "app_crash"
    FROZEN_UI = "frozen_ui"
    LOOP_DETECTED = "loop_detected"
    UNKNOWN = "unknown"


class FailureSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RecoveryAction(str, Enum):
    CONTINUE = "continue"
    RETRY = "retry"
    REPLAN = "replan"
    NEW_SCREENSHOT = "new_screenshot"
    REFRESH_APP = "refresh_app"
    RESTART_APP = "restart_app"
    ASK_USER = "ask_user"
    ABORT = "abort"


# --- Diff Schemas ---
class ElementDiff(BaseModel):
    """A single UI element change."""
    element_text: str = ""
    element_type: str = ""
    center: Optional[List[int]] = None
    change_type: str = ""  # "added", "removed", "changed"


class StateDiff(BaseModel):
    """Result of comparing two UI states."""
    added_elements: List[ElementDiff] = []
    removed_elements: List[ElementDiff] = []
    changed_elements: List[ElementDiff] = []
    layout_changed: bool = False
    element_count_before: int = 0
    element_count_after: int = 0
    similarity_score: float = 1.0  # 1.0 = identical, 0.0 = completely different


# --- Failure Detection ---
class FailureReport(BaseModel):
    failure_detected: bool = False
    failure_type: FailureType = FailureType.UNKNOWN
    severity: FailureSeverity = FailureSeverity.LOW
    description: str = ""


# --- Verification Result ---
class VerificationResult(BaseModel):
    """Complete output of a verification pass."""
    success: bool
    confidence: float = Field(ge=0.0, le=1.0)
    task_progress: str = ""
    next_recommendation: RecoveryAction = RecoveryAction.CONTINUE
    replan_required: bool = False
    retry_required: bool = False
    verification_reason: str = ""
    failure_report: Optional[FailureReport] = None
    state_diff: Optional[StateDiff] = None
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


# --- Completion Detection ---
class CompletionResult(BaseModel):
    task_complete: bool = False
    confidence: float = 0.0
    reason: str = ""


# --- Verification Input ---
class VerificationInput(BaseModel):
    """Everything the verifier needs to evaluate an action."""
    goal: str
    executed_action: Dict[str, Any]
    previous_ui_state: Dict[str, Any]
    current_ui_state: Dict[str, Any]
    execution_result: Optional[Dict[str, Any]] = None
    action_history: List[Dict[str, Any]] = []
