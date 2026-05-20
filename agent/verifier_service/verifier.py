import os
from typing import Dict, Any, List
from rich.console import Console

from verifier_service.config import Config
from verifier_service.schemas import (
    VerificationResult, VerificationInput, RecoveryAction,
    FailureType, FailureSeverity, FailureReport, CompletionResult,
)
from verifier_service.state_diff import StateDiffEngine
from verifier_service.failure_detector import FailureDetector
from verifier_service.loop_detector import LoopDetector
from verifier_service.progress_tracker import ProgressTracker
from verifier_service.completion_detector import CompletionDetector
from verifier_service.verification_memory import VerificationMemory
from verifier_service.services.recovery_service import RecoveryService
from verifier_service.services.ui_similarity_service import UISimilarityService

console = Console()


class Verifier:
    """
    Core Verifier — BATCH verification (one check per iteration, not per action).
    
    Pipeline (deterministic-first):
      1. Diff pre/post UI states
      2. Detect failures (deterministic — no LLM)
      3. Evaluate batch success from diff
      4. Return recommendation
      
    Loop detection is separate — called once per iteration by the agent loop.
    """

    def __init__(self):
        self.diff_engine = StateDiffEngine()
        self.failure_detector = FailureDetector()
        self.loop_detector = LoopDetector()
        self.progress_tracker = ProgressTracker()
        self.completion_detector = CompletionDetector()
        self.memory = VerificationMemory()
        self.recovery = RecoveryService()
        self.ui_similarity = UISimilarityService()

    def reset(self):
        self.loop_detector.reset()
        self.progress_tracker.reset()
        self.memory.clear()

    def record_iteration(self, ui_state: Dict[str, Any], action_batch: Dict[str, Any]) -> None:
        """Record state + action for loop detection. Call ONCE per iteration."""
        self.loop_detector.record_state(ui_state)
        self.loop_detector.record_action(action_batch)

    def check_loop(self) -> bool:
        """Check for loops. Call ONCE per iteration BEFORE verification."""
        return self.loop_detector.detect_loop()

    async def verify_batch(self, v_input: VerificationInput) -> VerificationResult:
        """
        Verify a BATCH of actions at once (not individually).
        Compares pre-execution vs post-execution UI state.
        """
        action = v_input.executed_action
        prev_ui = v_input.previous_ui_state
        curr_ui = v_input.current_ui_state
        curr_elements = curr_ui.get("elements", [])

        # Step 1: Diff UI states
        state_diff = self.diff_engine.compare(prev_ui, curr_ui)

        # Step 2: Detect failures (deterministic)
        failure_report = self.failure_detector.detect(action, state_diff, curr_elements)

        if failure_report.failure_detected:
            recovery_action = self.recovery.recommend_deterministic(failure_report)
            result = VerificationResult(
                success=False,
                confidence=0.8,
                task_progress=self.progress_tracker.get_progress_summary(),
                next_recommendation=recovery_action,
                replan_required=(recovery_action == RecoveryAction.REPLAN),
                retry_required=(recovery_action == RecoveryAction.RETRY),
                verification_reason=failure_report.description,
                failure_report=failure_report,
                state_diff=state_diff,
            )
            self.progress_tracker.record_progress("batch", False, failure_report.description)
            self.memory.record_verification(result, action)
            return result

        # Step 3: Batch appears successful — score confidence
        action_type = action.get("action_type", "batch")
        
        if state_diff.layout_changed or len(state_diff.added_elements) > 0:
            confidence = 0.9
            reason = f"UI changed: +{len(state_diff.added_elements)} added, layout_changed={state_diff.layout_changed}"
        elif state_diff.similarity_score < 0.9:
            confidence = 0.8
            reason = f"UI updated (similarity={state_diff.similarity_score:.2f})"
        elif action_type in ("wait", "launch_app", "focus_window", "batch"):
            confidence = 0.85
            reason = "Actions executed — UI may have changed offscreen."
        else:
            confidence = 0.65
            reason = f"Minimal visible change (similarity={state_diff.similarity_score:.2f})"

        self.progress_tracker.record_progress("batch", True, reason)

        result = VerificationResult(
            success=True,
            confidence=confidence,
            task_progress=self.progress_tracker.get_progress_summary(),
            next_recommendation=RecoveryAction.CONTINUE,
            replan_required=False,
            retry_required=False,
            verification_reason=reason,
            state_diff=state_diff,
        )
        self.memory.record_verification(result, action)
        return result

    async def check_completion(
        self,
        goal: str,
        current_ui: Dict[str, Any],
        history: List[Dict[str, Any]],
    ) -> CompletionResult:
        """Deterministic first, then LLM if inconclusive."""
        curr_elements = current_ui.get("elements", [])

        det_result = self.completion_detector.detect_deterministic(goal, curr_elements, current_ui)
        if det_result.task_complete and det_result.confidence >= 0.6:
            return det_result

        llm_result = await self.completion_detector.detect_with_llm(goal, curr_elements, history, current_ui)
        return llm_result

    def save_history(self, task_id: str) -> None:
        self.memory.save_to_disk(task_id)
