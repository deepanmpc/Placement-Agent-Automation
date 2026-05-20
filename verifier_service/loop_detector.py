import hashlib
import json
from typing import List, Dict, Any
from rich.console import Console

from verifier_service.config import Config

console = Console()


class LoopDetector:
    """
    Detect infinite execution loops.
    Fixed: only triggers on genuinely repeated patterns, not false positives.
    """

    def __init__(self):
        self._state_hashes: List[str] = []
        self._action_keys: List[str] = []

    def reset(self):
        self._state_hashes.clear()
        self._action_keys.clear()

    def _hash_state(self, ui_state: Dict[str, Any]) -> str:
        elements = ui_state.get("elements", [])
        texts = sorted(el.get("text", "").strip() for el in elements if el.get("text", "").strip())
        # Include element count for better differentiation
        raw = json.dumps({"count": len(elements), "texts": texts[:30]}, sort_keys=True)
        return hashlib.md5(raw.encode()).hexdigest()

    def _action_key(self, action: Dict[str, Any]) -> str:
        return f"{action.get('action_type', '')}:{action.get('target', '')}:{action.get('text', '')}"

    def record_state(self, ui_state: Dict[str, Any]) -> None:
        self._state_hashes.append(self._hash_state(ui_state))

    def record_action(self, action: Dict[str, Any]) -> None:
        self._action_keys.append(self._action_key(action))

    def is_state_loop(self) -> bool:
        """Same UI state N times in a row."""
        t = Config.LOOP_DETECTION_THRESHOLD
        if len(self._state_hashes) < t:
            return False
        return len(set(self._state_hashes[-t:])) == 1

    def is_action_loop(self) -> bool:
        """Same action repeated N times in a row."""
        t = Config.ACTION_REPEAT_THRESHOLD
        if len(self._action_keys) < t:
            return False
        return len(set(self._action_keys[-t:])) == 1

    def is_cyclic_navigation(self) -> bool:
        """A→B→A→B pattern."""
        if len(self._state_hashes) < 4:
            return False
        h = self._state_hashes[-4:]
        return h[0] == h[2] and h[1] == h[3] and h[0] != h[1]

    def detect_loop(self) -> bool:
        """
        Check all loop types. Only call ONCE per iteration (not per action).
        Returns True if loop detected.
        """
        if self.is_state_loop():
            console.print("  [bold red][Loop] Same UI state repeated — replanning.[/bold red]")
            return True
        if self.is_action_loop():
            console.print("  [bold red][Loop] Same action repeated — replanning.[/bold red]")
            return True
        if self.is_cyclic_navigation():
            console.print("  [bold red][Loop] Cyclic navigation — replanning.[/bold red]")
            return True
        return False
