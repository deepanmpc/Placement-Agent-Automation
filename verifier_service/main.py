"""
Verifier Service — Standalone entry point for testing.

In production, the Verifier is called by the agent loop after each action execution.
This file demonstrates the verification pipeline independently.

Usage:
    cd /Users/deepandee/Desktop/ComputerUse/agent
    PYTHONPATH=. .venv/bin/python -m verifier_service.main
"""
import asyncio
from rich.console import Console
from rich.panel import Panel

from verifier_service.verifier import Verifier
from verifier_service.schemas import VerificationInput

console = Console()


async def demo():
    """Demonstrate the verification pipeline with mock data."""
    verifier = Verifier()

    # Simulate: before state (home page), after state (search bar appeared)
    previous_ui = {
        "elements": [
            {"type": "button", "text": "Home", "center": [100, 50]},
            {"type": "button", "text": "Search", "center": [200, 50]},
            {"type": "text", "text": "Welcome to Safari", "center": [400, 300]},
        ]
    }
    current_ui = {
        "elements": [
            {"type": "button", "text": "Home", "center": [100, 50]},
            {"type": "button", "text": "Search", "center": [200, 50]},
            {"type": "input", "text": "Search or enter URL", "center": [400, 50]},
            {"type": "text", "text": "Google", "center": [400, 300]},
        ]
    }

    v_input = VerificationInput(
        goal="Open Safari and search for YouTube",
        executed_action={"action_type": "click", "target": "Search Bar", "coordinates": [200, 50]},
        previous_ui_state=previous_ui,
        current_ui_state=current_ui,
        action_history=[],
    )

    console.print(Panel(
        "[bold]Verifier Service Demo[/bold]\n"
        "Running verification pipeline on simulated action...",
        title="[bold magenta]Phase 5 — Verifier[/bold magenta]",
        border_style="magenta",
    ))

    result = await verifier.verify_batch(v_input)

    console.print(Panel(
        f"[bold]Success:[/bold] {result.success}\n"
        f"[bold]Confidence:[/bold] {result.confidence:.2f}\n"
        f"[bold]Reason:[/bold] {result.verification_reason}\n"
        f"[bold]Progress:[/bold] {result.task_progress}\n"
        f"[bold]Recommendation:[/bold] {result.next_recommendation.value}\n"
        f"[bold]Replan:[/bold] {result.replan_required}\n"
        f"[bold]Retry:[/bold] {result.retry_required}",
        title="[bold green]Verification Result[/bold green]",
        border_style="green" if result.success else "red",
    ))

    # Test completion detection
    completion = await verifier.check_completion(
        "Open Safari and search for YouTube",
        current_ui,
        [{"action": "click → Search Bar", "success": True}],
    )
    console.print(Panel(
        f"[bold]Complete:[/bold] {completion.task_complete}\n"
        f"[bold]Confidence:[/bold] {completion.confidence:.2f}\n"
        f"[bold]Reason:[/bold] {completion.reason}",
        title="[bold blue]Completion Check[/bold blue]",
        border_style="blue",
    ))

    console.print("\n[bold green]✅ Verifier Service: Pipeline verified.[/bold green]")


if __name__ == "__main__":
    asyncio.run(demo())
