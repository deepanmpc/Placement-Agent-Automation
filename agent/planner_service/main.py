from fastapi import FastAPI, BackgroundTasks
import uvicorn
from typing import Dict, Any

from planner_service.schemas import VisionPayload, VoiceIntent
from planner_service.state_manager import StateManager
from planner_service.task_memory import TaskMemory
from planner_service.screenshot_policy import ScreenshotPolicyEngine
from planner_service.planner import ReasoningEngine
from planner_service.stt import router as stt_router
from vision_service.utils.logger import logger

app = FastAPI(title="Planner Service (Cognitive Orchestrator)")

# Attach routers
app.include_router(stt_router, prefix="/voice", tags=["STT"])

# Services
state_manager = StateManager()
task_memory = TaskMemory()
policy_engine = ScreenshotPolicyEngine()
reasoning_engine = ReasoningEngine()

@app.post("/context/vision")
async def receive_vision_state(payload: VisionPayload, background_tasks: BackgroundTasks):
    """Endpoint called by the Vision Service to push the latest parsed UI state."""
    logger.info(f"Received Vision payload for Session: {payload.session_id} | Frame: {payload.frame_id}")
    
    # In a real async loop, this vision payload updates the active memory context.
    # We will trigger the reasoning engine in the background to avoid blocking.
    background_tasks.add_task(process_planning_cycle, payload)
    
    return {"status": "received", "frame_id": payload.frame_id}

@app.post("/intent")
async def receive_voice_intent(intent: VoiceIntent):
    """Endpoint for receiving the parsed voice transcript to kick off a new task."""
    logger.info(f"Received User Intent: {intent.transcript}")
    task_id = "task_" + str(hash(intent.transcript))[:8]
    
    state_manager.create_or_update_state(
        task_id=task_id,
        goal=intent.transcript,
        current_step="Initialize",
        completed_steps=[],
        pending_steps=[]
    )
    
    return {"status": "Task Started", "task_id": task_id}

async def process_planning_cycle(payload: VisionPayload):
    """Core autonomous loop tick triggered by new visual context."""
    # 1. Fetch active task
    # For prototype, we assume a hardcoded active task or fetch from DB
    task_id = "demo_task_id"
    state = state_manager.get_state(task_id)
    if not state:
        logger.debug("No active task running. Vision frame ignored.")
        return
        
    goal = state["goal"]
    
    # 2. Check if we actually need to process this frame
    history = task_memory.get_recent_history(task_id)
    decision = policy_engine.should_capture_new_frame(state, history)
    
    if not decision["capture"]:
        logger.debug("Skipping frame processing based on adaptive policy.")
        return
        
    # 3. Generate structured action plan
    plan = await reasoning_engine.generate_next_steps(goal, payload.model_dump(), history)
    
    # 4. Save interactions to memory
    for act in plan.actions:
        task_memory.store_interaction(task_id, act.model_dump(), success=True, context_summary=plan.thought)
        
    # 5. Route to Executor (Mocked here for now)
    logger.info(f"--- PLAN GENERATED ---")
    logger.info(f"Thought: {plan.thought}")
    logger.info(f"Actions: {[a.action_type for a in plan.actions]}")
    logger.info(f"Requires new screenshot? {plan.requires_new_screenshot}")

if __name__ == "__main__":
    from planner_service.config import Config
    logger.info(f"Starting Planner Service on {Config.PLANNER_HOST}:{Config.PLANNER_PORT}")
    uvicorn.run(app, host=Config.PLANNER_HOST, port=Config.PLANNER_PORT)
