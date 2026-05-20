from executor_service.services.window_service import WindowService
from executor_service.schemas import ExecutorActionInput

window_svc = WindowService()


def execute_focus_window(action: ExecutorActionInput) -> str:
    """Bring a window to the foreground by app name."""
    name = action.app_name or action.target or action.text
    if not name:
        raise ValueError("Focus window failed: no app/window name provided.")
    result = window_svc.focus_window(name)
    if "failed" in result.lower():
        raise RuntimeError(result)
    return result
