from typing import List, Tuple, Dict, Any, Optional
from pydantic import BaseModel, Field

class OCRText(BaseModel):
    text: str
    confidence: float
    bbox: Tuple[int, int, int, int]  # x1, y1, x2, y2
    center: Tuple[int, int]

class UIElement(BaseModel):
    id: str
    type: str  # 'button', 'input', 'text', 'icon', etc.
    text: Optional[str] = None
    bbox: Tuple[int, int, int, int]
    center: Tuple[int, int]
    clickable: bool = False
    confidence: float
    source: str  # 'ocr', 'omniparser', 'ocr+omniparser'

class Relationship(BaseModel):
    parent: str
    child: str

class ScreenState(BaseModel):
    width: int
    height: int
    timestamp: str
    origin_x: int = 0
    origin_y: int = 0
    coordinate_system: str = "screen"
    capture_scope: str = "unknown"
    app: Optional[str] = None
    title: Optional[str] = None
    screenshot_path: Optional[str] = None

class PlannerPayload(BaseModel):
    session_id: str
    frame_id: str
    screen: ScreenState
    elements: List[UIElement]
    relationships: List[Relationship]
    metadata: Dict[str, Any] = Field(default_factory=dict)
