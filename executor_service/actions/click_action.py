from executor_service.services.mouse_service import MouseService
from executor_service.schemas import ExecutorActionInput

mouse = MouseService()


def execute_click(action: ExecutorActionInput) -> str:
    """Execute a left click at the specified coordinates."""
    if not action.coordinates or len(action.coordinates) != 2:
        raise ValueError("Click failed: missing or invalid coordinates.")
    x, y = action.coordinates
    return mouse.click(x, y, button="left")


def execute_double_click(action: ExecutorActionInput) -> str:
    """Execute a double click at the specified coordinates."""
    if not action.coordinates or len(action.coordinates) != 2:
        raise ValueError("Double-click failed: missing or invalid coordinates.")
    x, y = action.coordinates
    return mouse.double_click(x, y)


def execute_right_click(action: ExecutorActionInput) -> str:
    """Execute a right click at the specified coordinates."""
    if not action.coordinates or len(action.coordinates) != 2:
        raise ValueError("Right-click failed: missing or invalid coordinates.")
    x, y = action.coordinates
    return mouse.right_click(x, y)
