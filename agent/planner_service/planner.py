from typing import Dict, Any, List
from vision_service.utils.logger import logger
from planner_service.services.llm_service import LLMService
from planner_service.prompt_builder import PromptBuilder
from planner_service.schemas import PlannerOutput, Action
from pydantic import ValidationError

class ReasoningEngine:
    def __init__(self):
        self.llm = LLMService()
        self.prompt_builder = PromptBuilder()

    async def generate_next_steps(self, goal: str, ui_state: Dict[str, Any], history: List[Dict[str, Any]]) -> PlannerOutput:
        """
        Orchestrates the prompt building and LLM generation, then parses and validates the output.
        """
        logger.info(f"Generating plan for goal: {goal}")
        prompt = self.prompt_builder.build_planner_prompt(goal, ui_state, history)
        
        raw_json = await self.llm.generate_plan(prompt)
        raw_json = self._coerce_plan_payload(raw_json)
        
        if not raw_json:
            logger.warning("Empty response from LLM, returning fallback wait action.")
            return self._fallback_action()

        try:
            # Validate output using Pydantic
            plan = PlannerOutput(**raw_json)
            logger.debug(f"Plan generated: {plan.thought}")
            return plan
        except ValidationError as e:
            logger.error(f"LLM output failed schema validation: {e}")
            return self._fallback_action()

    def _coerce_plan_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Accept a few common action JSON shapes and normalize them to PlannerOutput."""
        if not payload:
            return {}

        if "actions" not in payload and "operations" in payload:
            payload["actions"] = payload.pop("operations")

        actions = payload.get("actions")
        if isinstance(actions, dict):
            actions = [actions]
        if not isinstance(actions, list):
            return payload

        normalized_actions = []
        for action in actions:
            if not isinstance(action, dict):
                continue
            if "action_type" not in action and "operation" in action:
                action["action_type"] = action.pop("operation")
            if action.get("action_type") == "write":
                action["action_type"] = "type"
            if action.get("action_type") in ("press", "key"):
                action["action_type"] = "hotkey"
            normalized_actions.append(action)

        payload["actions"] = normalized_actions
        return payload

    def _fallback_action(self) -> PlannerOutput:
        return PlannerOutput(
            thought="Fallback triggered due to error.",
            goal_progress="Unknown",
            actions=[Action(action_type="wait", confidence=0.0)],
            requires_new_screenshot=True,
            task_complete=False
        )
