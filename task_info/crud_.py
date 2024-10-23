import logging

from fastapi import HTTPException
from sqlalchemy.orm import Session

from .aws_utils import create_aws_client
from .models import Task
from .schemas import TaskCreate
import os
from .logging_config import setup_logging

setup_logging("task_master.log")

SQS_QUEUE_URL = os.getenv("SQS_QUEUE_URL")


def create_task(db: Session, task: TaskCreate):
    logging.info(f"Creating a new task with task_id: {task.task_id}")

    if not task.task_id:
        logging.error("Task creation failed: task_id is missing.")
        raise HTTPException(status_code=422, detail="Field 'task_id' is required")

    existing_task = db.query(Task).filter(Task.task_id == task.task_id).first()
    if existing_task:
        logging.error(
            f"Task creation failed: Task with task_id {task.task_id} already exists."
        )
        raise HTTPException(
            status_code=400, detail="Task with this task_id already exists"
        )

    # Create a new task in the database
    db_task = Task(task_id=task.task_id, status="pending")
    db.add(db_task)
    db.commit()
    db.refresh(db_task)

    logging.info(
        f"Task {task.task_id} created successfully. Sending task to SQS queue."
    )

    # Creating an SQS client
    sqs_client = create_aws_client("sqs")

    # Sending a task to the SQS queue
    try:
        sqs_client.send_message(QueueUrl=SQS_QUEUE_URL, MessageBody=task.task_id)
        logging.info(f"Task {task.task_id} successfully sent to SQS queue.")
    except Exception as e:
        logging.error(f"Failed to send task {task.task_id} to SQS queue: {e}")
        raise HTTPException(status_code=500, detail="Failed to send task to SQS queue")

    return db_task


def get_task(db: Session, task_id: str):
    logging.info(f"Fetching task with task_id: {task_id}")

    db_task = db.query(Task).filter(Task.task_id == task_id).first()
    if db_task is None:
        logging.warning(f"Task with task_id {task_id} not found.")
        raise HTTPException(status_code=404, detail="Task not found")

    logging.info(f"Task with task_id {task_id} found: {db_task}")
    return db_task


def update_task_status(db: Session, task_id: str, status: str):
    logging.info(f"Updating task status: task_id={task_id}, new_status={status}")

    db_task = db.query(Task).filter(Task.task_id == task_id).first()
    if db_task:
        db_task.status = status
        db.commit()
        logging.info(f"Task status updated: task_id={task_id}, new_status={status}")
        return db_task
    logging.warning(f"Task not found for task_id={task_id}")
    raise HTTPException(status_code=404, detail="Task not found")
