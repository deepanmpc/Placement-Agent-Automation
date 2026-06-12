from typing import List, Dict, Any
from rich.console import Console

from verifier_service.schemas import StateDiff, ElementDiff
from verifier_service.services.comparison_service import ComparisonService

console = Console()


class StateDiffEngine:
    """
    Compare previous and current UI states.
    Deterministic-first: no LLM needed.
    """

    def __init__(self):
        self.comparison = ComparisonService()

    def compare(
        self,
        previous_ui: Dict[str, Any],
        current_ui: Dict[str, Any],
    ) -> StateDiff:
        """
        Diff two UI states and produce a structured StateDiff.
        """
        prev_elements = previous_ui.get("elements", [])
        curr_elements = current_ui.get("elements", [])

        diff_raw = self.comparison.compare_element_lists(prev_elements, curr_elements)
        similarity = self.comparison.compute_similarity(prev_elements, curr_elements)

        added = [
            ElementDiff(element_text=t, change_type="added")
            for t in diff_raw["added"]
        ]
        removed = [
            ElementDiff(element_text=t, change_type="removed")
            for t in diff_raw["removed"]
        ]

        # Detect significant layout change (element count changed by >30%)
        before_count = len(prev_elements)
        after_count = len(curr_elements)
        layout_changed = False
        if before_count > 0:
            ratio = abs(after_count - before_count) / before_count
            layout_changed = ratio > 0.3 or similarity < 0.5

        return StateDiff(
            added_elements=added,
            removed_elements=removed,
            changed_elements=[],
            layout_changed=layout_changed,
            element_count_before=before_count,
            element_count_after=after_count,
            similarity_score=similarity,
        )
