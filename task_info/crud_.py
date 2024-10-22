from fastapi import HTTPException
from sqlalchemy.orm import Session

from .models import Task
from .schemas import TaskCreate
import boto3
import os

SQS_QUEUE_URL = os.getenv("SQS_QUEUE_URL")

# Initializing the SQS Client
sqs_client = boto3.client("sqs",
                          endpoint_url="http://localstack:4566",
                          region_name="eu-central-1"
                          )


def create_task(db: Session, task: TaskCreate):
    if not task.task_id:
        raise HTTPException(status_code=422, detail="Field 'task_id' is required")

    existing_task = db.query(Task).filter(Task.task_id == task.task_id).first()
    if existing_task:
        raise HTTPException(
            status_code=400, detail="Task with this task_id already exists"
        )

    # Create a new task in the database
    db_task = Task(task_id=task.task_id, status="pending")
    db.add(db_task)
    db.commit()
    db.refresh(db_task)

    # Sending a task to the SQS queue
    sqs_client.send_message(QueueUrl=SQS_QUEUE_URL, MessageBody=task.task_id)

    return db_task


def get_task(db: Session, task_id: str):
    print(f"Searching for task_id: {task_id}")
    db_task = db.query(Task).filter(Task.task_id == task_id).first()
    if db_task is None:
        print("Task not found in database")
        raise HTTPException(status_code=404, detail="Task not found")
    print(f"Task found in database: {db_task}")
    return db_task


def update_task_status(db: Session, task_id: str, status: str):
    db_task = db.query(Task).filter(Task.task_id == task_id).first()
    if db_task:
        db_task.status = status
        db.commit()
        return db_task
    raise HTTPException(status_code=404, detail="Task not found")
