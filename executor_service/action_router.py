from typing import Callable, Dict, Optional
from rich.console import Console

from executor_service.schemas import ExecutorActionInput
from executor_service.actions.click_action import execute_click, execute_double_click, execute_right_click
from executor_service.actions.type_action import execute_type
from executor_service.actions.hotkey_action import execute_hotkey
from executor_service.actions.scroll_action import execute_scroll
from executor_service.actions.drag_action import execute_drag
from executor_service.actions.launch_action import execute_launch
from executor_service.actions.wait_action import execute_wait
from executor_service.actions.focus_window_action import execute_focus_window

console = Console()

# Registry: action_type → handler function
_ACTION_REGISTRY: Dict[str, Callable] = {
    "click":        execute_click,
    "double_click": execute_double_click,
    "right_click":  execute_right_click,
    "type":         execute_type,
    "hotkey":       execute_hotkey,
    "scroll":       execute_scroll,
    "drag":         execute_drag,
    "launch_app":   execute_launch,
    "wait":         execute_wait,
    "focus_window": execute_focus_window,
}


class ActionRouter:
    """Routes structured action payloads to the correct deterministic handler."""

    def get_handler(self, action_type: str) -> Optional[Callable]:
        """Look up the handler for a given action type."""
        return _ACTION_REGISTRY.get(action_type)

    def is_supported(self, action_type: str) -> bool:
        return action_type in _ACTION_REGISTRY

    def list_supported_actions(self):
        return list(_ACTION_REGISTRY.keys())

    async def route_and_execute(self, action: ExecutorActionInput) -> str:
        """Route an action to its handler and execute it."""
        handler = self.get_handler(action.action_type)
        if handler is None:
            raise ValueError(f"Unsupported action type: '{action.action_type}'")

        import asyncio
        if asyncio.iscoroutinefunction(handler):
            return await handler(action)
        else:
            return handler(action)
