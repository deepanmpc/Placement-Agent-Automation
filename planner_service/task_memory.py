import json
from typing import List, Dict, Any, Optional
from sqlmodel import Field, Session, SQLModel, create_engine, select
from planner_service.config import Config

class InteractionMemory(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: str
    action_taken_json: str
    success: bool
    context_summary: str

engine = create_engine(f"sqlite:///{Config.DB_PATH}", echo=False)

class TaskMemory:
    def __init__(self):
        SQLModel.metadata.create_all(engine)
        
    def store_interaction(self, task_id: str, action: Dict[str, Any], success: bool, context_summary: str):
        with Session(engine) as session:
            mem = InteractionMemory(
                task_id=task_id,
                action_taken_json=json.dumps(action),
                success=success,
                context_summary=context_summary
            )
            session.add(mem)
            session.commit()
            
    def get_recent_history(self, task_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        with Session(engine) as session:
            # Simple query using sqlmodel
            statement = select(InteractionMemory).where(InteractionMemory.task_id == task_id).order_by(InteractionMemory.id.desc()).limit(limit)
            result = session.exec(statement).all()
            return [{"action": json.loads(row.action_taken_json), "success": row.success} for row in result]
