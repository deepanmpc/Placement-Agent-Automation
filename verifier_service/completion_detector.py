import os
from typing import Dict, Any, List
from rich.console import Console

from verifier_service.config import Config
from verifier_service.schemas import CompletionResult
from verifier_service.services.llm_service import VerifierLLMService

console = Console()


class CompletionDetector:
    """
    Determine whether the user's task goal is fully completed.
    Uses deterministic checks first, then LLM reasoning.
    """

    def __init__(self):
        self.llm = VerifierLLMService()
        self._prompt = self._load_prompt("completion_prompt.txt")

    def _load_prompt(self, filename: str) -> str:
        path = os.path.join(Config.PROMPTS_DIR, filename)
        if os.path.exists(path):
            with open(path, "r") as f:
                return f.read().strip()
        return ""

    def detect_deterministic(
        self,
        goal: str,
        current_elements: List[Dict[str, Any]],
        current_ui: Dict[str, Any] | None = None,
    ) -> CompletionResult:
        """
        Quick deterministic checks for obvious completion.
        """
        goal_lower = goal.lower()
        current_ui = current_ui or {}
        screen = current_ui.get("screen", {})
        active_app = (screen.get("app") or "").lower()
        element_texts = [el.get("text", "").lower() for el in current_elements]
        all_text = " ".join(element_texts)

        if goal_lower.startswith("open "):
            requested = goal_lower.replace("open ", "", 1).strip()
            if requested and requested in active_app:
                return CompletionResult(
                    task_complete=True,
                    confidence=0.8,
                    reason=f"Requested app appears frontmost: {screen.get('app')}",
                )

        # Check if key goal words appear in the UI
        goal_words = [w for w in goal_lower.split() if len(w) > 3]
        if goal_words:
            matches = sum(1 for w in goal_words if w in all_text)
            match_ratio = matches / len(goal_words)
            if match_ratio > 0.6:
                return CompletionResult(
                    task_complete=True,
                    confidence=min(0.7, match_ratio),
                    reason=f"Goal keywords found in UI ({matches}/{len(goal_words)} matched)",
                )

        return CompletionResult(
            task_complete=False,
            confidence=0.3,
            reason="Deterministic check inconclusive",
        )

    async def detect_with_llm(
        self,
        goal: str,
        current_elements: List[Dict[str, Any]],
        action_history: List[Dict[str, Any]],
        current_ui: Dict[str, Any] | None = None,
    ) -> CompletionResult:
        """Use LLM to determine task completion."""
        current_ui = current_ui or {}
        screen = current_ui.get("screen", {})
        ui_summary = "\n".join(
            f"[{el.get('type', 'element')}] text='{el.get('text', '')}'"
            for el in current_elements[:40]
        )
        history_str = "\n".join(
            f"  {h.get('action', 'unknown')} (success={h.get('success', '?')})"
            for h in action_history[-8:]
        )

        prompt = (
            f"{self._prompt}\n\n"
            f"GOAL: {goal}\n\n"
            f"CURRENT APP: {screen.get('app', 'unknown')}\n"
            f"WINDOW TITLE: {screen.get('title', '')}\n\n"
            f"CURRENT UI ELEMENTS:\n{ui_summary}\n\n"
            f"ACTION HISTORY:\n{history_str}"
        )

        result = await self.llm.query(prompt)
        if result:
            return CompletionResult(
                task_complete=result.get("task_complete", False),
                confidence=result.get("confidence", 0.5),
                reason=result.get("reason", "LLM evaluation"),
            )

        return CompletionResult(
            task_complete=False,
            confidence=0.3,
            reason="LLM completion check failed",
        )
