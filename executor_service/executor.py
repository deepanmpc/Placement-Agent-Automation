import asyncio
import time
import json
import os
from typing import List, Optional
from datetime import datetime

import pyautogui
from rich.console import Console
from rich.panel import Panel

from executor_service.config import Config
from executor_service.schemas import (
    ExecutorActionInput, ExecutionResult, ActionStatus, TaskState, TaskStatus,
)
from executor_service.action_router import ActionRouter
from executor_service.action_queue import ActionQueue
from executor_service.execution_state import ExecutionStateManager
from executor_service.task_context import TaskContext
from executor_service.coordinate_mapper import CoordinateMapper
from executor_service.interrupt_manager import InterruptManager
from executor_service.retry_manager import RetryManager
from executor_service.services.safety_service import SafetyService
from vision_service.screenshot import ScreenshotCapturer
from vision_service.parser import parse_ui

console = Console()


class Executor:
    """
    Core Executor: deterministic action execution engine.
    
    Responsibilities:
      - Receive structured action plans (from Planner)
      - Validate and route each action
      - Execute with retries, timeouts, safety checks
      - Maintain persistent execution state
      - Support interrupt/cancel/pause
      - Log execution history
    """

    def __init__(self):
        pyautogui.FAILSAFE = Config.PYAUTOGUI_FAILSAFE
        pyautogui.PAUSE = Config.PYAUTOGUI_PAUSE

        self.router = ActionRouter()
        self.queue = ActionQueue()
        self.state_manager = ExecutionStateManager()
        self.task_context = TaskContext()
        self.coord_mapper = CoordinateMapper()
        self.interrupt_manager = InterruptManager()
        self.retry_manager = RetryManager()
        self.safety = SafetyService()
        
        self.screenshot_capturer = ScreenshotCapturer()
        self.action_count = 0

    async def execute_plan(self, task_id: str, goal: str, actions: List[ExecutorActionInput]) -> TaskState:
        """
        Execute a full action plan end-to-end.
        
        Args:
            task_id: Unique identifier for this task.
            goal: The user's original high-level goal.
            actions: Ordered list of actions from the Planner.
            
        Returns:
            Final TaskState after execution.
        """
        # Initialize state
        self.state_manager.create_task(task_id, goal)
        self.task_context.set_goal(goal)
        self.interrupt_manager.start()
        self.interrupt_manager.reset()
        await self.queue.reset()

        # Enqueue all actions
        await self.queue.enqueue_batch(actions)

        console.print(Panel(
            f"Goal: {goal}\nActions: {len(actions)} queued",
            title="[bold blue]Executor Starting[/bold blue]",
            border_style="blue",
        ))

        try:
            await self._execution_loop()
        except pyautogui.FailSafeException:
            console.print("[bold red]🛑 PyAutoGUI FailSafe triggered! Mouse moved to corner.[/bold red]")
            self.state_manager.mark_cancelled()
        except Exception as e:
            console.print(f"[bold red]Executor error: {e}[/bold red]")
            self.state_manager.mark_failed()
        finally:
            self.interrupt_manager.stop()

        state = self.state_manager.get_state()

        # Mark completed if all actions succeeded
        if state and state.status == TaskStatus.RUNNING:
            self.state_manager.mark_completed()
            state = self.state_manager.get_state()

        self._log_execution_history(state)
        self.task_context.clear()

        return state

    async def _execution_loop(self) -> None:
        """Main loop: dequeue → validate → execute → update state."""
        while not self.queue.is_empty:
            # Check for interrupts
            if self.interrupt_manager.is_interrupted:
                console.print("[bold red][Executor] Interrupted — halting execution.[/bold red]")
                self.state_manager.mark_cancelled()
                await self.queue.cancel()
                return

            action = await self.queue.dequeue()
            if action is None:
                if self.queue.is_paused:
                    await asyncio.sleep(0.5)
                    continue
                break

            result = await self._execute_single_action(action)

            if result.status == ActionStatus.SUCCESS:
                self.state_manager.record_success(result)
            else:
                self.state_manager.record_failure(result)
                # If max retries exceeded on this task, stop
                state = self.state_manager.get_state()
                if state and state.retry_count > Config.MAX_RETRIES:
                    console.print("[bold red][Executor] Max retries exceeded — marking task failed.[/bold red]")
                    self.state_manager.mark_failed()
                    return

    async def _execute_single_action(self, action: ExecutorActionInput) -> ExecutionResult:
        """Validate, safety-check, and execute a single action."""
        action_desc = f"{action.action_type} → {action.target or action.text or action.app_name or 'N/A'}"
        self.state_manager.update_current_action(action_desc)

        console.print(f"\n  [bold cyan][Executor][/bold cyan] {action_desc}")

        # 1. Validate coordinates if present
        if action.coordinates:
            valid, msg = self.coord_mapper.validate_coordinates(action.coordinates)
            if not valid:
                console.print(f"  [bold red][Coordinate] {msg}[/bold red]")
                return ExecutionResult(
                    action_type=action.action_type,
                    target=action.target,
                    status=ActionStatus.FAILED,
                    message=msg,
                )

        # 2. Safety check
        if not self.safety.is_safe_to_execute(action):
            console.print("  [bold red][Safety] Action blocked by user.[/bold red]")
            return ExecutionResult(
                action_type=action.action_type,
                target=action.target,
                status=ActionStatus.SKIPPED,
                message="Blocked by safety check.",
            )

# 3. Execute with retry
        start = time.time()
        try:
            message = await self.retry_manager.execute_with_retry(
                self.router.route_and_execute, action
            )
            elapsed = (time.time() - start) * 1000
            console.print(f"  [bold green]✓[/bold green] {message} ({elapsed:.0f}ms)")
            
            # Wait for UI to update after action
            await asyncio.sleep(Config.DEFAULT_WAIT_SECONDS)
            
            # Take verification screenshot after each action
            self.action_count += 1
            console.print(f"  [dim][Verify] Capturing step {self.action_count} screenshot...[/dim]")
            try:
                np_img, img_pil, screenshot_path = self.screenshot_capturer.capture_active_window()
                capture_info = {
                    "capture_scope": "active_window",
                    "screenshot_path": screenshot_path
                }
                # Run OCR on the verification screenshot
                from vision_service.ocr import extract_text
                import numpy as np
                img_np = np.array(img_pil)
                ocr_data = extract_text(img_np)
                verification_state = parse_ui(img_pil, ocr_data, capture_info)
                console.print(f"  [dim][Verify] Step {self.action_count}: {len(verification_state.get('elements', []))} elements detected[/dim]")
            except Exception as ve:
                console.print(f"  [dim][Verify] Step {self.action_count} failed: {ve}[/dim]")
            
            return ExecutionResult(
                action_type=action.action_type,
                target=action.target,
                status=ActionStatus.SUCCESS,
                message=message,
                duration_ms=elapsed,
            )
        except Exception as e:
            elapsed = (time.time() - start) * 1000
            console.print(f"  [bold red]✗ Failed: {str(e)}[/bold red] ({elapsed:.0f}ms)")
            return ExecutionResult(
                action_type=action.action_type,
                target=action.target,
                status=ActionStatus.FAILED,
                message=str(e),
                duration_ms=elapsed,
            )
            return ExecutionResult(
                action_type=action.action_type,
                target=action.target,
                status=ActionStatus.FAILED,
                message=str(e),
                duration_ms=elapsed,
            )

    def _log_execution_history(self, state: Optional[TaskState]) -> None:
        """Write JSON execution log to the action_history directory."""
        if not state:
            return
        log_path = os.path.join(
            Config.ACTION_HISTORY_DIR,
            f"{state.task_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        )
        with open(log_path, "w") as f:
            json.dump(state.model_dump(), f, indent=2)
        console.print(f"  [dim][Log] Execution history saved: {os.path.basename(log_path)}[/dim]")
