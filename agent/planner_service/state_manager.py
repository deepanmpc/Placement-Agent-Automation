import json
from typing import Optional, List, Dict, Any
from sqlmodel import Field, Session, SQLModel, create_engine
from vision_service.utils.logger import logger
from planner_service.config import Config

class TaskState(SQLModel, table=True):
    task_id: str = Field(default=None, primary_key=True)
    goal: str
    current_step: str
    completed_steps_json: str = Field(default="[]")
    pending_steps_json: str = Field(default="[]")
    status: str = Field(default="running")

# Initialize SQLite engine
sqlite_url = f"sqlite:///{Config.DB_PATH}"
engine = create_engine(sqlite_url, echo=False)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

class StateManager:
    def __init__(self):
        create_db_and_tables()

    def get_state(self, task_id: str) -> Optional[Dict[str, Any]]:
        with Session(engine) as session:
            state = session.get(TaskState, task_id)
            if state:
                return {
                    "task_id": state.task_id,
                    "goal": state.goal,
                    "current_step": state.current_step,
                    "completed_steps": json.loads(state.completed_steps_json),
                    "pending_steps": json.loads(state.pending_steps_json),
                    "status": state.status
                }
            return None

    def create_or_update_state(self, task_id: str, goal: str, current_step: str, completed_steps: List[str], pending_steps: List[str], status: str = "running"):
        with Session(engine) as session:
            state = session.get(TaskState, task_id)
            if not state:
                state = TaskState(
                    task_id=task_id, goal=goal, current_step=current_step,
                    completed_steps_json=json.dumps(completed_steps),
                    pending_steps_json=json.dumps(pending_steps),
                    status=status
                )
                session.add(state)
            else:
                state.goal = goal
                state.current_step = current_step
                state.completed_steps_json = json.dumps(completed_steps)
                state.pending_steps_json = json.dumps(pending_steps)
                state.status = status
                session.add(state)
            
            session.commit()
            logger.debug(f"State saved for Task: {task_id}")
