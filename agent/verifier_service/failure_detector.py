from typing import List, Dict, Any
from rich.console import Console

from verifier_service.schemas import FailureReport, FailureType, FailureSeverity, StateDiff
from verifier_service.services.comparison_service import ComparisonService

console = Console()


class FailureDetector:
    """
    Detect execution failures from UI state changes.
    Deterministic checks — no LLM needed.
    """

    def __init__(self):
        self.comparison = ComparisonService()

    def detect(
        self,
        action: Dict[str, Any],
        state_diff: StateDiff,
        current_elements: List[Dict[str, Any]],
    ) -> FailureReport:
        """Run all failure detection checks and return a report."""
        action_type = action.get("action_type", "")

        # 1. Check for error dialogs/text
        errors = self.comparison.detect_error_indicators(current_elements)
        if errors:
            return FailureReport(
                failure_detected=True,
                failure_type=FailureType.ERROR_DIALOG,
                severity=FailureSeverity.MEDIUM,
                description=f"Error indicators found: {errors[:3]}",
            )

        # 2. No UI change after a click/type action
        if action_type in ("click", "double_click", "type", "hotkey"):
            if state_diff.similarity_score > 0.95 and not state_diff.layout_changed:
                return FailureReport(
                    failure_detected=True,
                    failure_type=FailureType.NO_CHANGE,
                    severity=FailureSeverity.LOW,
                    description=f"No UI change after '{action_type}' (similarity={state_diff.similarity_score:.2f})",
                )

        # 3. Loading stuck
        if self.comparison.detect_loading_indicators(current_elements):
            return FailureReport(
                failure_detected=True,
                failure_type=FailureType.LOADING_STUCK,
                severity=FailureSeverity.LOW,
                description="UI appears to be in a loading state.",
            )

        # 4. Zero elements (possibly app crashed or blank screen)
        if state_diff.element_count_after == 0 and state_diff.element_count_before > 0:
            return FailureReport(
                failure_detected=True,
                failure_type=FailureType.APP_CRASH,
                severity=FailureSeverity.HIGH,
                description="Screen went blank (0 elements after action).",
            )

        # No failure detected
        return FailureReport(failure_detected=False)
