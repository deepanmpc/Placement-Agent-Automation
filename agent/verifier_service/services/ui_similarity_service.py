from typing import List, Dict, Any
from rich.console import Console

from verifier_service.services.comparison_service import ComparisonService

console = Console()


class UISimilarityService:
    """Higher-level UI similarity checks combining structural and semantic analysis."""

    def __init__(self):
        self.comparison = ComparisonService()

    def are_states_identical(
        self,
        before: List[Dict[str, Any]],
        after: List[Dict[str, Any]],
        threshold: float = 0.95,
    ) -> bool:
        """Check if two UI states are effectively identical."""
        return self.comparison.compute_similarity(before, after) >= threshold

    def detect_navigation(
        self,
        before: List[Dict[str, Any]],
        after: List[Dict[str, Any]],
    ) -> bool:
        """Detect if a page/screen navigation occurred (major content change)."""
        similarity = self.comparison.compute_similarity(before, after)
        # If less than 50% overlap, likely a navigation event
        return similarity < 0.5

    def detect_dialog_appeared(
        self,
        before: List[Dict[str, Any]],
        after: List[Dict[str, Any]],
    ) -> bool:
        """Detect if a modal/dialog/popup appeared."""
        diff = self.comparison.compare_element_lists(before, after)
        added = diff["added"]
        dialog_keywords = [
            "ok", "cancel", "close", "dismiss", "allow", "deny",
            "accept", "decline", "yes", "no", "confirm",
        ]
        for text in added:
            if text.lower().strip() in dialog_keywords:
                return True
        return False

    def find_target_element(
        self,
        elements: List[Dict[str, Any]],
        target_text: str,
    ) -> bool:
        """Check if a target element (by text) exists in the current UI."""
        if not target_text:
            return False
        target_lower = target_text.lower().strip()
        for el in elements:
            el_text = el.get("text", "").lower().strip()
            if target_lower in el_text or el_text in target_lower:
                return True
        return False
