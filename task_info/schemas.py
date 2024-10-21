from datetime import datetime
from pydantic import BaseModel, constr


class TaskBase(BaseModel):
    task_id: str


class Task(TaskBase):
    id: int
    task_id: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class TaskCreate(TaskBase):
    task_id: constr(min_length=2, max_length=10)
