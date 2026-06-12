from executor_service.services.keyboard_service import KeyboardService
from executor_service.schemas import ExecutorActionInput

keyboard = KeyboardService()


def execute_hotkey(action: ExecutorActionInput) -> str:
    """Execute a keyboard shortcut (e.g., cmd+c, ctrl+shift+t)."""
    if action.keys and len(action.keys) >= 1:
        if len(action.keys) == 1:
            return keyboard.press_key(action.keys[0])
        return keyboard.hotkey(*action.keys)

    # Fallback: try to parse from text like "cmd+c" or "return"
    if action.text:
        parts = [k.strip() for k in action.text.split("+")]
        if len(parts) >= 2:
            return keyboard.hotkey(*parts)
        elif len(parts) == 1:
            return keyboard.press_key(parts[0])

    raise ValueError("Hotkey failed: provide 'keys' list (e.g. ['return']) or 'text' (e.g. 'cmd+c').")
