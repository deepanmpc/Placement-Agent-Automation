import time
from difflib import SequenceMatcher
from typing import Dict, Any, List, Optional, Tuple
from rich.console import Console

from executor_service.config import Config

console = Console()


class ElementCache:
    """
    Cache grounded UI elements to avoid rediscovering coordinates every loop.
    Elements expire after TTL_MS to handle UI changes.
    """

    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._ttl_ms = Config.ELEMENT_CACHE_TTL_MS

    def _make_key(self, text: str, element_type: str = "") -> str:
        return f"{element_type}:{text}".lower().strip()

    def store_elements(self, elements: List[Dict[str, Any]]) -> None:
        """Cache all elements from a UI parse with timestamps."""
        now = time.time() * 1000
        for el in elements:
            text = el.get("text", "").strip()
            if not text:
                continue
            key = self._make_key(text, el.get("type", ""))
            self._cache[key] = {
                "text": text,
                "type": el.get("type", "element"),
                "center": el.get("center", []),
                "bbox": el.get("bbox", []),
                "confidence": el.get("confidence", 1.0),
                "cached_at": now,
            }
        # Evict old entries
        self._evict_expired()

    def lookup(self, target_text: str, element_type: str = "") -> Optional[Dict[str, Any]]:
        """Find a cached element by text (fuzzy match). Returns None if not found or expired."""
        self._evict_expired()
        target_lower = target_text.lower().strip()

        # Exact match first
        for key, entry in self._cache.items():
            if target_lower == entry["text"].lower():
                return entry

        # Partial match
        for key, entry in self._cache.items():
            if target_lower in entry["text"].lower() or entry["text"].lower() in target_lower:
                return entry

        # Fuzzy match for OCR/model wording differences.
        best_entry = None
        best_score = 0.0
        for entry in self._cache.values():
            score = SequenceMatcher(None, target_lower, entry["text"].lower()).ratio()
            if score > best_score:
                best_entry = entry
                best_score = score
        if best_entry and best_score >= 0.72:
            return best_entry

        return None

    def get_coordinates(self, target_text: str) -> Optional[Tuple[int, int]]:
        """Shortcut: lookup element and return its center coordinates."""
        entry = self.lookup(target_text)
        if entry and entry.get("center") and len(entry["center"]) == 2:
            return tuple(entry["center"])
        return None

    def invalidate(self) -> None:
        """Clear entire cache (call on major UI changes)."""
        self._cache.clear()

    def _evict_expired(self) -> None:
        now = time.time() * 1000
        expired = [k for k, v in self._cache.items() if now - v["cached_at"] > self._ttl_ms]
        for k in expired:
            del self._cache[k]

    @property
    def size(self) -> int:
        return len(self._cache)
