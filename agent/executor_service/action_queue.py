import asyncio
from typing import Optional, List
from collections import deque

from executor_service.schemas import ExecutorActionInput
from rich.console import Console

console = Console()


class ActionQueue:
    """
    FIFO action queue with priority insertion, pause/resume, and cancellation.
    Thread-safe via asyncio.Lock.
    """

    def __init__(self):
        self._queue: deque[ExecutorActionInput] = deque()
        self._priority_queue: deque[ExecutorActionInput] = deque()
        self._lock = asyncio.Lock()
        self._paused = False
        self._cancelled = False

    async def enqueue(self, action: ExecutorActionInput, priority: bool = False) -> None:
        """Add an action to the queue."""
        async with self._lock:
            if priority:
                self._priority_queue.append(action)
            else:
                self._queue.append(action)

    async def enqueue_batch(self, actions: List[ExecutorActionInput]) -> None:
        """Add multiple actions to the queue."""
        async with self._lock:
            self._queue.extend(actions)

    async def dequeue(self) -> Optional[ExecutorActionInput]:
        """Get the next action to execute. Priority actions come first."""
        async with self._lock:
            if self._cancelled:
                return None
            if self._paused:
                return None
            # Priority queue drains first
            if self._priority_queue:
                return self._priority_queue.popleft()
            if self._queue:
                return self._queue.popleft()
            return None

    async def pause(self) -> None:
        """Pause dequeuing (actions remain in queue)."""
        async with self._lock:
            self._paused = True
            console.print("  [bold yellow][Queue] Paused[/bold yellow]")

    async def resume(self) -> None:
        """Resume dequeuing."""
        async with self._lock:
            self._paused = False
            console.print("  [bold green][Queue] Resumed[/bold green]")

    async def cancel(self) -> None:
        """Cancel all pending actions."""
        async with self._lock:
            self._cancelled = True
            self._queue.clear()
            self._priority_queue.clear()
            console.print("  [bold red][Queue] Cancelled — all actions cleared[/bold red]")

    async def reset(self) -> None:
        """Reset queue state for a new task."""
        async with self._lock:
            self._queue.clear()
            self._priority_queue.clear()
            self._paused = False
            self._cancelled = False

    @property
    def is_paused(self) -> bool:
        return self._paused

    @property
    def is_cancelled(self) -> bool:
        return self._cancelled

    @property
    def size(self) -> int:
        return len(self._queue) + len(self._priority_queue)

    @property
    def is_empty(self) -> bool:
        return self.size == 0
