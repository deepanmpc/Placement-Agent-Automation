from typing import Tuple, Optional, List

import Quartz
from rich.console import Console

console = Console()

# Minimum safe margin from screen edges (pixels)
# PyAutoGUI fail-safe triggers when mouse moves to corners
EDGE_MARGIN = 10


class CoordinateMapper:
    """
    Validates and adjusts coordinates against actual screen bounds.
    Rejects coordinates near screen edges/corners to prevent fail-safe triggers.
    """

    def __init__(self):
        self._screen_width, self._screen_height = self._get_screen_size()
        console.print(f"  [dim][CoordinateMapper] Screen: {self._screen_width}x{self._screen_height}[/dim]")

    def _get_screen_size(self) -> Tuple[int, int]:
        bounds = Quartz.CGDisplayBounds(Quartz.CGMainDisplayID())
        return int(bounds.size.width), int(bounds.size.height)

    @property
    def screen_width(self) -> int:
        return self._screen_width

    @property
    def screen_height(self) -> int:
        return self._screen_height

    def is_within_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self._screen_width and 0 <= y < self._screen_height

    def is_safe_coordinate(self, x: int, y: int) -> bool:
        """Check that coordinates are NOT in the fail-safe trigger zones (screen corners/edges)."""
        if x < EDGE_MARGIN and y < EDGE_MARGIN:
            return False  # Top-left corner
        if x >= self._screen_width - EDGE_MARGIN and y < EDGE_MARGIN:
            return False  # Top-right corner
        if x < EDGE_MARGIN and y >= self._screen_height - EDGE_MARGIN:
            return False  # Bottom-left corner
        if x >= self._screen_width - EDGE_MARGIN and y >= self._screen_height - EDGE_MARGIN:
            return False  # Bottom-right corner
        return True

    def clamp_safe(self, x: int, y: int) -> Tuple[int, int]:
        """Clamp coordinates to safe area (away from corners)."""
        x = max(EDGE_MARGIN, min(x, self._screen_width - EDGE_MARGIN - 1))
        y = max(EDGE_MARGIN, min(y, self._screen_height - EDGE_MARGIN - 1))
        return x, y

    def validate_coordinates(self, coords: Optional[List[int]]) -> Tuple[bool, str]:
        """Validate a [x, y] coordinate pair. Rejects invalid, out-of-bounds, and corner coordinates."""
        if coords is None or len(coords) != 2:
            return False, "Coordinates must be [x, y]."

        x, y = coords
        if not isinstance(x, (int, float)) or not isinstance(y, (int, float)):
            return False, f"Coordinates must be numeric, got ({type(x).__name__}, {type(y).__name__})."

        x, y = int(x), int(y)

        # Reject [0,0] — this is almost always an LLM hallucination
        if x == 0 and y == 0:
            return False, "Coordinates (0, 0) rejected — likely LLM hallucination."

        if not self.is_within_bounds(x, y):
            return False, f"({x}, {y}) outside screen ({self._screen_width}x{self._screen_height})."

        if not self.is_safe_coordinate(x, y):
            return False, f"({x}, {y}) too close to screen corner — fail-safe zone."

        return True, "Valid"
