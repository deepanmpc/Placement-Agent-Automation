import pyautogui
import pyperclip
from typing import List, Optional
from rich.console import Console

from executor_service.config import Config

console = Console()


class KeyboardService:
    """Low-level keyboard interaction with typing delay and modifier support."""

    def __init__(self):
        pyautogui.FAILSAFE = Config.PYAUTOGUI_FAILSAFE

    def _normalize_key(self, key: str) -> str:
        aliases = {
            "cmd": "command",
            "command": "command",
            "enter": "return",
            "esc": "escape",
            "spacebar": "space",
            "option": "alt",
        }
        cleaned = key.strip().lower()
        return aliases.get(cleaned, cleaned)

    def type_text(self, text: str, interval: Optional[float] = None) -> str:
        """Type text character by character with configurable delay."""
        ivl = interval if interval is not None else Config.TYPING_INTERVAL
        try:
            # pyautogui.write only supports basic ASCII; use clipboard for unicode
            if all(ord(c) < 128 for c in text):
                pyautogui.write(text, interval=ivl)
            else:
                self._type_via_clipboard(text)
            console.print(f"  [dim][Keyboard] Typed: '{text[:50]}{'...' if len(text) > 50 else ''}'[/dim]")
            return f"Typed: '{text[:80]}'"
        except Exception as e:
            return f"Type failed: {e}"

    def _type_via_clipboard(self, text: str) -> None:
        """Fallback: paste via clipboard for unicode text."""
        original = pyperclip.paste()
        try:
            pyperclip.copy(text)
            pyautogui.hotkey("command", "v")
        finally:
            pyperclip.copy(original)

    def press_key(self, key: str) -> str:
        """Press a single key (enter, tab, escape, etc.)."""
        key = self._normalize_key(key)
        pyautogui.press(key)
        console.print(f"  [dim][Keyboard] Pressed: '{key}'[/dim]")
        return f"Pressed key: '{key}'"

    def hotkey(self, *keys: str) -> str:
        """Press a key combination (e.g., cmd+c, ctrl+shift+t)."""
        keys = tuple(self._normalize_key(k) for k in keys)
        pyautogui.hotkey(*keys)
        combo = "+".join(keys)
        console.print(f"  [dim][Keyboard] Hotkey: {combo}[/dim]")
        return f"Hotkey: {combo}"

    def key_down(self, key: str) -> str:
        """Hold a key down."""
        pyautogui.keyDown(key)
        return f"Key down: '{key}'"

    def key_up(self, key: str) -> str:
        """Release a held key."""
        pyautogui.keyUp(key)
        return f"Key up: '{key}'"
