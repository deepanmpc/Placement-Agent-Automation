from executor_service.services.app_service import AppService
from executor_service.schemas import ExecutorActionInput

app_svc = AppService()


def execute_launch(action: ExecutorActionInput) -> str:
    """Launch a macOS application by name. Falls back to Spotlight if open -a fails."""
    name = action.app_name or action.target or action.text
    if not name:
        raise ValueError("Launch failed: no app name provided.")

    # Try standard launch first
    result = app_svc.launch_app(name)
    if "Failed" in result or "not found" in result:
        # Fallback to Spotlight search
        result = app_svc.launch_via_spotlight(name)
        if "failed" in result.lower():
            raise RuntimeError(result)
        return result
    return result
