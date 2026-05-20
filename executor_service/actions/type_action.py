from executor_service.services.keyboard_service import KeyboardService
from executor_service.schemas import ExecutorActionInput

keyboard = KeyboardService()


def execute_type(action: ExecutorActionInput) -> str:
    """Type text at the current cursor position."""
    if not action.text:
        raise ValueError("Type failed: no text provided.")
    return keyboard.type_text(action.text)
