import asyncio
from typing import Callable, Any, Optional
from rich.console import Console

from executor_service.config import Config

console = Console()


class RetryManager:
    """
    Handles failed actions with exponential backoff retry logic.
    
    Retry conditions:
      - Element not found
      - App not responding
      - Focus lost
      - Timeout
      
    Strategy: exponential backoff with configurable max attempts and delay cap.
    """

    def __init__(
        self,
        max_retries: int = Config.MAX_RETRIES,
        base_delay: float = Config.RETRY_BASE_DELAY,
        max_delay: float = Config.RETRY_MAX_DELAY,
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay

    def compute_delay(self, attempt: int) -> float:
        """Compute exponential backoff delay for the given attempt number."""
        delay = self.base_delay * (2 ** attempt)
        return min(delay, self.max_delay)

    async def execute_with_retry(
        self,
        func: Callable,
        *args: Any,
        on_retry: Optional[Callable] = None,
        **kwargs: Any,
    ) -> Any:
        """
        Execute a function with automatic retry on failure.
        
        Args:
            func: The async or sync callable to execute.
            on_retry: Optional callback invoked before each retry (e.g., request new screenshot).
        """
        last_error = None

        for attempt in range(self.max_retries + 1):
            try:
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)

                # Check for soft failures (returned error strings)
                if isinstance(result, str) and "failed" in result.lower():
                    raise RuntimeError(result)

                return result

            except Exception as e:
                last_error = e
                if attempt < self.max_retries:
                    delay = self.compute_delay(attempt)
                    console.print(
                        f"  [bold yellow][Retry] Attempt {attempt + 1}/{self.max_retries} failed: {e}. "
                        f"Retrying in {delay:.1f}s...[/bold yellow]"
                    )
                    if on_retry:
                        if asyncio.iscoroutinefunction(on_retry):
                            await on_retry()
                        else:
                            on_retry()
                    await asyncio.sleep(delay)
                else:
                    console.print(
                        f"  [bold red][Retry] All {self.max_retries} retries exhausted. Last error: {e}[/bold red]"
                    )

        raise last_error if last_error else RuntimeError("Retry failed with no error captured.")
