import asyncio
from executor_service.schemas import ExecutorActionInput
from executor_service.config import Config
from rich.console import Console

console = Console()


async def execute_wait(action: ExecutorActionInput) -> str:
    """Pause execution for a specified duration."""
    duration = action.duration if action.duration else Config.DEFAULT_WAIT_SECONDS
    console.print(f"  [dim][Wait] Waiting {duration}s...[/dim]")
    await asyncio.sleep(duration)
    return f"Waited {duration} seconds."
