import os
from typing import Dict, Any, Optional
from rich.console import Console

from verifier_service.config import Config
from verifier_service.schemas import RecoveryAction, FailureReport, FailureType
from verifier_service.services.llm_service import VerifierLLMService

console = Console()


class RecoveryService:
    """Recommend and execute recovery strategies after failures."""

    def __init__(self):
        self.llm = VerifierLLMService()
        self._recovery_prompt = self._load_prompt("recovery_prompt.txt")

    def _load_prompt(self, filename: str) -> str:
        path = os.path.join(Config.PROMPTS_DIR, filename)
        if os.path.exists(path):
            with open(path, "r") as f:
                return f.read().strip()
        return ""

    def recommend_deterministic(self, failure: FailureReport) -> RecoveryAction:
        """Fast deterministic recovery recommendation based on failure type."""
        mapping = {
            FailureType.NO_CHANGE: RecoveryAction.RETRY,
            FailureType.ERROR_DIALOG: RecoveryAction.REPLAN,
            FailureType.WRONG_ELEMENT: RecoveryAction.NEW_SCREENSHOT,
            FailureType.LOADING_STUCK: RecoveryAction.RETRY,
            FailureType.MODAL_BLOCKING: RecoveryAction.REPLAN,
            FailureType.PERMISSION_POPUP: RecoveryAction.ASK_USER,
            FailureType.LOGIN_REQUIRED: RecoveryAction.ASK_USER,
            FailureType.APP_CRASH: RecoveryAction.RESTART_APP,
            FailureType.FROZEN_UI: RecoveryAction.REFRESH_APP,
            FailureType.LOOP_DETECTED: RecoveryAction.REPLAN,
        }
        return mapping.get(failure.failure_type, RecoveryAction.NEW_SCREENSHOT)

    async def recommend_with_llm(
        self,
        goal: str,
        failed_action: Dict[str, Any],
        current_ui: list,
        history: list,
    ) -> Dict[str, Any]:
        """Use LLM for nuanced recovery recommendation."""
        ui_summary = "\n".join(
            f"[{el.get('type', 'element')}] text='{el.get('text', '')}'"
            for el in current_ui[:30]
        )
        history_str = "\n".join(
            f"  {h.get('action', 'unknown')} (success={h.get('success', '?')})"
            for h in history[-5:]
        )

        prompt = (
            f"{self._recovery_prompt}\n\n"
            f"GOAL: {goal}\n\n"
            f"FAILED ACTION: {failed_action}\n\n"
            f"CURRENT UI ELEMENTS:\n{ui_summary}\n\n"
            f"RECENT HISTORY:\n{history_str}"
        )

        result = await self.llm.query(prompt)
        return result if result else {
            "recovery_action": "new_screenshot",
            "reason": "LLM recovery failed, defaulting to new screenshot",
        }
