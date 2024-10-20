from datetime import datetime

from sqlalchemy import Column, String, DateTime, Integer

from database import Base


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String, index=True, unique=True)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.now)

