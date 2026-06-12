from executor_service.services.mouse_service import MouseService
from executor_service.schemas import ExecutorActionInput

mouse = MouseService()


def execute_drag(action: ExecutorActionInput) -> str:
    """Click and drag from start to end coordinates."""
    start = action.start_coords or action.coordinates
    end = action.end_coords

    if not start or len(start) != 2:
        raise ValueError("Drag failed: missing start coordinates.")
    if not end or len(end) != 2:
        raise ValueError("Drag failed: missing end coordinates.")

    duration = action.duration if action.duration else 0.5
    return mouse.drag(start[0], start[1], end[0], end[1], duration=duration)
