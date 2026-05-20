"""
Autonomous Agent — Optimized Execution Loop

STABILITY > SPEED > HUMAN-LIKE BEHAVIOR

Key optimizations:
  - ONE screenshot per iteration (cached across steps)
  - UI compressed before LLM (40 element cap, deduplicated)
  - Element cache (avoids coordinate rediscovery)
  - Batch verification (one check per iteration, not per action)
  - Loop detection (once per iteration)
  - Instant mouse movement (0.02s)
  - No safety warnings on normal operations
  - Corner/[0,0] coordinate rejection

Usage:
    cd /Users/deepandee/Desktop/ComputerUse/agent
    PYTHONPATH=. .venv/bin/python -m executor_service.main
"""
import asyncio
import subprocess
import time
import uuid

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

from runtime_agent.services.vision_client import VisionClient
from runtime_agent.services.microphone_service import MicrophoneService
from planner_service.services.voice_service import VoiceService
from planner_service.planner import ReasoningEngine
from planner_service.schemas import PlannerOutput

from executor_service.executor import Executor
from executor_service.schemas import ExecutorActionInput
from executor_service.config import Config
from executor_service.services.app_service import AppService
from executor_service.element_cache import ElementCache
from executor_service.ui_compressor import compress_ui_for_llm

from verifier_service.verifier import Verifier
from verifier_service.schemas import VerificationInput, RecoveryAction

console = Console()
app_svc = AppService()

MAX_ITERATIONS = Config.MAX_AGENT_ITERATIONS
TERMINAL_APPS = {"Terminal", "iTerm2", "Alacritty", "kitty", "Warp"}


# ─── Terminal Management ───

def hide_terminal():
    try:
        app = app_svc.get_frontmost_app()
        if app in TERMINAL_APPS:
            subprocess.run(
                ["osascript", "-e",
                 f'tell application "System Events" to set visible of process "{app}" to false'],
                capture_output=True, timeout=3,
            )
            time.sleep(Config.SCREENSHOT_PRE_DELAY)
    except Exception:
        pass


def show_terminal():
    for term in ["Terminal", "iTerm2", "Alacritty", "kitty", "Warp"]:
        try:
            r = subprocess.run(["osascript", "-e", f'tell application "{term}" to activate'],
                               capture_output=True, timeout=2)
            if r.returncode == 0:
                return
        except Exception:
            continue


# ─── Action Conversion ───

def plan_to_executor_actions(plan: PlannerOutput, cache: ElementCache) -> list[ExecutorActionInput]:
    """Convert plan to executor actions, using cached coordinates when available."""
    actions = []
    for a in plan.actions:
        coords = a.coordinates

        # Try to resolve coordinates from cache if missing or [0,0]
        if (not coords or coords == [0, 0]) and a.target:
            cached_coords = cache.get_coordinates(a.target)
            if cached_coords:
                coords = list(cached_coords)
                console.print(f"  [dim]  ♻ Using cached coords for '{a.target}': {coords}[/dim]")

        ea = ExecutorActionInput(
            action_type=a.action_type,
            target=a.target,
            coordinates=coords if coords and coords != [0, 0] else None,
            text=a.text,
            keys=a.keys,
            direction=a.direction,
            amount=a.amount,
            app_name=a.app_name,
            duration=a.duration,
            start_coords=a.start_coords,
            end_coords=a.end_coords,
            confidence=a.confidence,
        )

        # Map action-specific fields
        if a.action_type == "hotkey" and not ea.keys and a.text:
            ea.keys = [k.strip() for k in a.text.split("+")]
        if a.action_type == "press" and a.text:
            ea.action_type = "hotkey"
            ea.keys = [a.text]
        if a.action_type in ("launch_app", "focus_window"):
            ea.app_name = a.app_name or a.target or a.text

        actions.append(ea)
    return actions


# ─── Screenshot ───

async def capture_screen(vision: VisionClient) -> dict:
    hide_terminal()
    await asyncio.sleep(0.2)
    return await vision.capture_and_parse()


async def verify_goal_complete(
    goal: str,
    ui_state: dict,
    history: list[dict],
    verifier: Verifier,
    *,
    min_confidence: float = 0.6,
) -> bool:
    """Ask the verifier whether the current screenshot proves the goal is done."""
    completion = await verifier.check_completion(goal, ui_state, history)
    if completion.task_complete and completion.confidence >= min_confidence:
        console.print(Panel(
            f"[bold]DONE[/bold] ({completion.confidence:.0%})\n{completion.reason}",
            title="[bold green]Goal Achieved[/bold green]", border_style="green",
        ))
        return True
    console.print(f"  [dim][Verifier] Not complete: {completion.reason} ({completion.confidence:.0%})[/dim]")
    return False


# ─── Main Agent Loop ───

async def agent_loop(
    goal: str,
    vision: VisionClient,
    planner: ReasoningEngine,
    executor: Executor,
    verifier: Verifier,
    element_cache: ElementCache,
):
    """
    Optimized loop:
      📸 Screenshot → 🧠 Plan (full batch) → ⚡ Execute all → 🔍 Verify batch → ♻ or ✅
    """
    task_id = f"task_{uuid.uuid4().hex[:8]}"
    history = []
    cached_ui = None
    iteration = 0

    verifier.reset()
    element_cache.invalidate()

    console.print(Panel(f"[bold]Goal:[/bold] {goal}",
                        title="[bold blue]🤖 Agent[/bold blue]", border_style="blue"))

    for iteration in range(1, MAX_ITERATIONS + 1):
        console.print(f"\n[bold cyan]═══ Step {iteration}/{MAX_ITERATIONS} ═══[/bold cyan]")

        # ─── 1. ONE screenshot (or reuse cached) ───
        if cached_ui is None:
            console.print("[dim]📸 Capturing...[/dim]")
            cached_ui = await capture_screen(vision)
            n = len(cached_ui.get("elements", []))
            console.print(f"[dim]   {n} elements[/dim]")
            if n == 0:
                await asyncio.sleep(0.5)
                cached_ui = await capture_screen(vision)
                n = len(cached_ui.get("elements", []))
                console.print(f"[dim]   Retry: {n} elements[/dim]")

            # Cache discovered elements
            element_cache.store_elements(cached_ui.get("elements", []))

        pre_ui = cached_ui

        # ─── 2. Loop detection (once per iteration) ───
        verifier.record_iteration(cached_ui, {"action_type": "batch", "target": goal})
        if iteration > 1 and verifier.check_loop():
            console.print("[bold red]↻ Loop detected — replanning with fresh screenshot.[/bold red]")
            cached_ui = None
            element_cache.invalidate()
            continue

        # ─── 3. Check completion (skip first iteration) ───
        if iteration > 1:
            if await verify_goal_complete(goal, cached_ui, history, verifier):
                break

        # ─── 4. Plan (one LLM call) ───
        console.print("[dim]🧠 Planning...[/dim]")
        plan = await planner.generate_next_steps(goal, cached_ui, history)

        console.print(Panel(
            f"[bold]Thought:[/bold] {plan.thought}\n"
            f"[bold]Actions:[/bold] {len(plan.actions)}",
            title="[bold yellow]Plan[/bold yellow]", border_style="yellow",
        ))

        # ─── 5. Execute batch ───
        exec_actions = plan_to_executor_actions(plan, element_cache)
        if not exec_actions:
            if plan.task_complete and await verify_goal_complete(goal, cached_ui, history, verifier):
                break
            history.append({"action": "no_actions", "success": False})
            cached_ui = None
            continue

        console.print(f"[dim]⚡ Executing {len(exec_actions)} actions...[/dim]")
        task_state = await executor.execute_plan(
            task_id=f"{task_id}_s{iteration}", goal=goal, actions=exec_actions,
        )

        # Record history
        for r in task_state.completed_actions:
            history.append({"action": f"{r.action_type} → {r.target or 'N/A'}", "success": True})
        for r in task_state.failed_actions:
            history.append({"action": f"{r.action_type} → {r.target or 'N/A'}", "success": False})

        # ─── 6. ONE post-execution screenshot + batch verify ───
        console.print("[dim]🔍 Verifying...[/dim]")
        post_ui = await capture_screen(vision)
        element_cache.store_elements(post_ui.get("elements", []))

        v_result = await verifier.verify_batch(VerificationInput(
            goal=goal,
            executed_action={"action_type": "batch", "target": ", ".join(a.action_type for a in plan.actions)},
            previous_ui_state=pre_ui,
            current_ui_state=post_ui,
            action_history=history,
        ))

        icon = "✓" if v_result.success else "✗"
        color = "green" if v_result.success else "red"
        console.print(f"  [{color}]{icon}[/{color}] {v_result.verification_reason} ({v_result.confidence:.0%})")

        if await verify_goal_complete(goal, post_ui, history, verifier):
            cached_ui = post_ui
            break

        # ─── 7. Recovery ───
        if not v_result.success:
            rec = v_result.next_recommendation
            console.print(f"  [yellow]Recovery: {rec.value}[/yellow]")
            if rec == RecoveryAction.ABORT:
                break
            elif rec == RecoveryAction.ASK_USER:
                show_terminal()
                ui = Prompt.ask("  [bold]What should I do?[/bold]")
                if ui.lower() in ("abort", "stop", "quit"):
                    break
                goal = f"{goal} ({ui})"
            element_cache.invalidate()
            cached_ui = None  # Force fresh screenshot
        elif plan.requires_new_screenshot:
            cached_ui = None  # Planner wants fresh view
        else:
            cached_ui = post_ui  # Reuse for next iteration

        await asyncio.sleep(0.15)

    else:
        console.print(f"[bold red]⛔ Max steps ({MAX_ITERATIONS}).[/bold red]")

    show_terminal()
    verifier.save_history(task_id)
    console.print(Panel(
        f"Goal: {goal}\nSteps: {iteration}\nActions: {len(history)}\n"
        f"Cache hits: {element_cache.size} elements cached",
        title="[bold]Done[/bold]", border_style="green",
    ))


# ─── Main ───

async def main():
    console.print(Panel(
        "[bold]Autonomous Desktop Agent[/bold]\n"
        "Goal → Plan → Execute → Verify → Complete\n"
        "Type goal, 'v' for voice, 'exit' to quit.",
        title="[bold magenta]🤖 Agent[/bold magenta]", border_style="magenta",
    ))

    vision = VisionClient()
    planner = ReasoningEngine()
    executor = Executor()
    verifier = Verifier()
    element_cache = ElementCache()
    mic = MicrophoneService()
    stt = VoiceService()

    while True:
        choice = Prompt.ask("\n[bold cyan]Goal?[/bold cyan] ('v' = voice, 'exit' = quit)")
        if choice.lower() in ("exit", "quit"):
            break
        if choice.lower() == "v":
            audio_path = mic.record_until_keypress()
            if not audio_path:
                continue
            console.print("[dim]Transcribing...[/dim]")
            stt_result = await asyncio.to_thread(stt.transcribe_audio, audio_path)
            goal = stt_result["transcript"]
            console.print(f"[bold green]You said:[/bold green] {goal}")
        else:
            goal = choice
        if not goal.strip():
            continue
        await agent_loop(goal, vision, planner, executor, verifier, element_cache)


if __name__ == "__main__":
    asyncio.run(main())
