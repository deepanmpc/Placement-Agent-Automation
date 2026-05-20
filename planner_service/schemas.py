from pydantic import BaseModel, Field, ConfigDict
from typing import List, Dict, Any, Optional

# --- Input Schemas (From Vision Service) ---
class VisionPayload(BaseModel):
    session_id: str
    frame_id: str
    screen: Dict[str, Any]
    elements: List[Dict[str, Any]]
    relationships: List[Dict[str, Any]]
    metadata: Dict[str, Any]

# --- Input Schemas (From STT Voice) ---
class VoiceIntent(BaseModel):
    transcript: str
    confidence: float
    language: str

# --- Planner Output Schemas ---
class Action(BaseModel):
    model_config = ConfigDict(extra="ignore")

    action_type: str = Field(description="Types: click, double_click, right_click, type, hotkey, scroll, drag, wait, launch_app, focus_window, ask_user")
    target: Optional[str] = Field(None, description="The logical target or UI text")
    coordinates: Optional[List[int]] = Field(None, description="[x, y] coordinates if applicable")
    text: Optional[str] = Field(None, description="Text to type if action_type is 'type'")
    keys: Optional[List[str]] = Field(None, description="Keys for hotkey actions, e.g. ['command', 'l']")
    direction: Optional[str] = Field(None, description="Scroll direction: up, down, left, right")
    amount: Optional[int] = Field(None, description="Scroll amount")
    app_name: Optional[str] = Field(None, description="Application name for launch/focus")
    duration: Optional[float] = Field(None, description="Wait or drag duration in seconds")
    start_coords: Optional[List[int]] = Field(None, description="Drag start coordinates")
    end_coords: Optional[List[int]] = Field(None, description="Drag end coordinates")
    confidence: float = Field(default=1.0)

class PlannerOutput(BaseModel):
    model_config = ConfigDict(extra="ignore")

    thought: str = Field(description="Brief operational rationale for these actions")
    goal_progress: str = Field(description="Summary of progress toward the main goal")
    actions: List[Action]
    requires_new_screenshot: bool = Field(description="Whether the planner needs a new visual frame after these actions")
    task_complete: bool = Field(default=False)

# --- Memory/State Schemas ---
class TaskContext(BaseModel):
    task_id: str
    goal: str
    current_step: str
    completed_steps: List[str] = []
    pending_steps: List[str] = []
    status: str = "running"
    
class VerificationResult(BaseModel):
    success: bool
    reason: str
    needs_retry: bool
