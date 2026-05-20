from typing import List, Dict, Any, Set
from rich.console import Console

console = Console()


class ComparisonService:
    """Deterministic structural comparison of UI element lists."""

    def compare_element_lists(
        self,
        before: List[Dict[str, Any]],
        after: List[Dict[str, Any]],
    ) -> dict:
        """
        Compare two lists of UI elements by text content.
        Returns added, removed, and common element texts.
        """
        before_texts = {el.get("text", "").strip() for el in before if el.get("text", "").strip()}
        after_texts = {el.get("text", "").strip() for el in after if el.get("text", "").strip()}

        added = after_texts - before_texts
        removed = before_texts - after_texts
        common = before_texts & after_texts

        return {
            "added": list(added),
            "removed": list(removed),
            "common": list(common),
            "before_count": len(before),
            "after_count": len(after),
        }

    def compute_similarity(
        self,
        before: List[Dict[str, Any]],
        after: List[Dict[str, Any]],
    ) -> float:
        """
        Compute Jaccard similarity between two UI states based on element text.
        Returns 0.0 (completely different) to 1.0 (identical).
        """
        before_texts = {el.get("text", "").strip() for el in before if el.get("text", "").strip()}
        after_texts = {el.get("text", "").strip() for el in after if el.get("text", "").strip()}

        if not before_texts and not after_texts:
            return 1.0
        if not before_texts or not after_texts:
            return 0.0

        intersection = before_texts & after_texts
        union = before_texts | after_texts
        return len(intersection) / len(union) if union else 1.0

    def detect_error_indicators(self, elements: List[Dict[str, Any]]) -> List[str]:
        """Check for error-related text in UI elements."""
        error_keywords = [
            "error", "failed", "denied", "not found", "404", "500",
            "permission", "access denied", "login required", "timeout",
            "crash", "not responding", "unexpected",
        ]
        found = []
        for el in elements:
            text = el.get("text", "").lower()
            for kw in error_keywords:
                if kw in text:
                    found.append(el.get("text", ""))
                    break
        return found

    def detect_loading_indicators(self, elements: List[Dict[str, Any]]) -> bool:
        """Check if UI shows loading state."""
        loading_keywords = ["loading", "please wait", "spinner", "progress"]
        for el in elements:
            text = el.get("text", "").lower()
            for kw in loading_keywords:
                if kw in text:
                    return True
        return False
