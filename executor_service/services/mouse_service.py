import pyautogui
from typing import Tuple, Optional
from rich.console import Console

from executor_service.config import Config

console = Console()

# Safe margin from corners - reduced to avoid triggering fail-safe
EDGE_MARGIN = 5


class MouseService:
    """Low-level mouse control — instant movement, pre-click validation."""

    def __init__(self):
        pyautogui.FAILSAFE = Config.PYAUTOGUI_FAILSAFE
        pyautogui.PAUSE = Config.PYAUTOGUI_PAUSE
        self.screen_width, self.screen_height = pyautogui.size()

    def _safe_clamp(self, x: int, y: int) -> Tuple[int, int]:
        """Clamp coordinates to safe zone (away from screen corners)."""
        # Never clamp to exactly 0 to avoid fail-safe
        x = max(10, min(x, self.screen_width - 10 - 1))
        y = max(10, min(y, self.screen_height - 10 - 1))
        return x, y

    def _is_dangerous(self, x: int, y: int) -> bool:
        """Reject coordinates that would trigger PyAutoGUI fail-safe."""
        # Check if within 10 pixels of any corner (fail-safe trigger zone)
        if x < 10 or y < 10:
            return True
        if x > self.screen_width - 10 or y > self.screen_height - 10:
            return True
        return False

    def move(self, x: int, y: int, duration: Optional[float] = None) -> str:
        """Move mouse instantly (or with minimal duration)."""
        x, y = self._safe_clamp(x, y)
        dur = duration if duration is not None else Config.MOUSE_MOVE_DURATION
        pyautogui.moveTo(x, y, duration=dur)
        return f"Moved to ({x}, {y})"

    def click(self, x: int, y: int, button: str = "left") -> str:
        """Pre-validate, then click with slight pause for accuracy."""
        if self._is_dangerous(x, y):
            x, y = self._safe_clamp(x, y)
            console.print(f"  [dim][Mouse] Clamped to safe zone: ({x}, {y})[/dim]")
        else:
            x, y = self._safe_clamp(x, y)

        # Move to position first (slower, more accurate)
        pyautogui.moveTo(x, y, duration=Config.MOUSE_MOVE_DURATION)
        time.sleep(0.1)  # Brief pause before clicking for accuracy
        pyautogui.click(x=x, y=y, button=button, _pause=False)
        console.print(f"  [dim][Mouse] {button.capitalize()} clicked at ({x}, {y})[/dim]")
        return f"{button.capitalize()} clicked at ({x}, {y})"

    def double_click(self, x: int, y: int) -> str:
        x, y = self._safe_clamp(x, y)
        pyautogui.doubleClick(x=x, y=y, _pause=False)
        console.print(f"  [dim][Mouse] Double-clicked at ({x}, {y})[/dim]")
        return f"Double-clicked at ({x}, {y})"

    def right_click(self, x: int, y: int) -> str:
        return self.click(x, y, button="right")

    def drag(self, start_x: int, start_y: int, end_x: int, end_y: int, duration: float = 0.3) -> str:
        start_x, start_y = self._safe_clamp(start_x, start_y)
        end_x, end_y = self._safe_clamp(end_x, end_y)
        pyautogui.moveTo(start_x, start_y, duration=0.05)
        pyautogui.drag(end_x - start_x, end_y - start_y, duration=duration)
        console.print(f"  [dim][Mouse] Dragged ({start_x},{start_y}) → ({end_x},{end_y})[/dim]")
        return f"Dragged ({start_x},{start_y}) → ({end_x},{end_y})"

    def scroll(self, clicks: int, x: Optional[int] = None, y: Optional[int] = None) -> str:
        if x is not None and y is not None:
            x, y = self._safe_clamp(x, y)
            pyautogui.scroll(clicks, x=x, y=y)
        else:
            pyautogui.scroll(clicks)
        direction = "up" if clicks > 0 else "down"
        console.print(f"  [dim][Mouse] Scrolled {direction} ({abs(clicks)} clicks)[/dim]")
        return f"Scrolled {direction} ({abs(clicks)} clicks)"

    def get_position(self) -> Tuple[int, int]:
        return pyautogui.position()
