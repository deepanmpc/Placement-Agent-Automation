from executor_service.services.mouse_service import MouseService
from executor_service.schemas import ExecutorActionInput

mouse = MouseService()


def execute_scroll(action: ExecutorActionInput) -> str:
    """Scroll up or down at current or specified position."""
    amount = action.amount if action.amount else 3
    direction = (action.direction or "down").lower()

    clicks = amount if direction == "up" else -amount

    if action.coordinates and len(action.coordinates) == 2:
        return mouse.scroll(clicks, x=action.coordinates[0], y=action.coordinates[1])
    return mouse.scroll(clicks)
