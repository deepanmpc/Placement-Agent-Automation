from typing import Optional
from rich.console import Console
from rich.prompt import Confirm

from executor_service.config import Config
from executor_service.schemas import ExecutorActionInput, SafetyLevel

console = Console()


class SafetyService:
    """
    Only blocks truly dangerous actions. No noise on normal operations.
    
    LOW    — auto-execute (click, type, scroll, hotkey, wait, launch_app, focus_window)
    HIGH   — block + require user confirmation (sudo, delete, payment, etc.)
    """

    def __init__(self):
        self.dangerous_keywords = Config.DANGEROUS_KEYWORDS

    def classify_action(self, action: ExecutorActionInput) -> SafetyLevel:
        """Only flag HIGH for genuinely dangerous content."""
        text_to_check = " ".join(filter(None, [
            action.target,
            action.text,
            action.app_name,
        ])).lower()

        for keyword in self.dangerous_keywords:
            if keyword in text_to_check:
                return SafetyLevel.HIGH

        # Everything else is LOW — no warnings needed
        return SafetyLevel.LOW

    def is_safe_to_execute(self, action: ExecutorActionInput) -> bool:
        """Returns True if safe. Only prompts for HIGH-risk actions."""
        level = self.classify_action(action)

        if level == SafetyLevel.LOW:
            return True

        # HIGH — require explicit confirmation
        console.print(
            f"\n  [bold red]🛑 HIGH-RISK ACTION[/bold red]\n"
            f"    Action: {action.action_type}\n"
            f"    Target: {action.target or 'N/A'}\n"
            f"    Text:   {action.text or 'N/A'}"
        )
        return Confirm.ask("  [bold]Proceed?[/bold]", default=False)
