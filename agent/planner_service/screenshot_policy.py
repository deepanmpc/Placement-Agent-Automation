from typing import Dict, Any, List

class ScreenshotPolicyEngine:
    def __init__(self):
        pass

    def should_capture_new_frame(self, state_context: Dict[str, Any], recent_actions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Determines if the planner needs a fresh screenshot from the vision service.
        Adaptive frequency rules based on latest actions.
        """
        if not recent_actions:
            # Start of a task, capture immediately
            return {"capture": True, "reason": "initial_state", "priority": "high"}
            
        last_action = recent_actions[-1]
        action_type = last_action.get("action_type")
        
        # If we just waited or slept, we might not need a new screenshot unless a timeout occurred.
        # But usually, 'wait' means waiting for UI to change, so if we wait, we definitely capture after.
        if action_type in ["click", "double_click", "type", "hotkey", "launch_app"]:
            return {"capture": True, "reason": f"post_action_{action_type}", "priority": "high"}
            
        if action_type == "wait":
            return {"capture": True, "reason": "post_wait_verification", "priority": "medium"}
            
        if state_context.get("uncertainty_high", False):
            return {"capture": True, "reason": "high_uncertainty", "priority": "high"}
            
        # Default fallback
        return {"capture": False, "reason": "no_trigger_event", "priority": "low"}
