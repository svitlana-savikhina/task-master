import re
from datetime import datetime
from pydantic import BaseModel, Field, field_validator


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
    task_id: str = Field(..., description="Only letters and digits allowed, length between 2 and 10")

    @field_validator('task_id')
    def validate_task_id(cls, value):
        if not re.match(r'^[A-Za-z0-9]{2,10}$', value):
            raise ValueError(
                "Invalid task_id format. Only letters and digits are allowed, and length must be between 2 and 10 "
                "characters."
            )
        return value
