import logging
import os

from botocore.exceptions import ClientError
from dotenv import load_dotenv

from database import SessionLocal
from task_info.celery import Celery
import time

from task_info.crud_ import update_task_status
from .aws_utils import create_aws_client
from .logging_config import setup_logging

setup_logging("task_master.log")

load_dotenv()
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

# Initializing Celery
celery_app = Celery(
    "tasks",
    broker="sqs://",
    broker_transport_options={
        "region": "eu-central-1",
        "queue_name_prefix": "",
        "polling_interval": 10,
        "visibility_timeout": 3600,
        "endpoint_url": "http://localstack:4566",
        "aws_access_key_id": AWS_ACCESS_KEY_ID,
        "aws_secret_access_key": AWS_SECRET_ACCESS_KEY,
    },
)

sqs = create_aws_client("sqs")
s3 = create_aws_client("s3")


# Create the SQS queue if it does not exist
def create_queue(queue_name):
    try:
        # Check if the queue already exists
        response = sqs.list_queues()
        for url in response.get("QueueUrls", []):
            if queue_name in url:
                logging.info(f"Queue already exists: {url}")
                return url

        response = sqs.create_queue(QueueName=queue_name)
        logging.info(f"Queue created: {response['QueueUrl']}")
        return response["QueueUrl"]
    except ClientError as e:
        logging.error(f"Error creating queue: {e}")
        return None


# Define and Create SQS Queue
queue_name = "my-queue"
create_queue(queue_name)


@celery_app.task
def process_task(task_id: str):
    logging.info(f"Processing task with task_id: {task_id}")
    db_session = SessionLocal()

    try:

        update_task_status(db_session, task_id, "in progress")

        time.sleep(5)

        logging.info(f"Updating task {task_id} status to 'completed'")
        update_task_status(db_session, task_id, "completed")
        logging.info(f"Task {task_id} status set to 'completed'")

        # Write a file to S3
        logging.info(f"Writing task {task_id} result to S3 bucket.")
        s3.put_object(
            Bucket="my-bucket", Key=f"{task_id}.txt", Body=f"Task ID: {task_id}"
        )
        logging.info(f"Task {task_id} result written to S3 bucket successfully.")

    except Exception as e:
        logging.error(f"An error occurred while processing task {task_id}: {str(e)}")
        update_task_status(db_session, task_id, "failed")
        logging.info(f"Task {task_id} status set to 'failed' due to an error.")
    finally:
        logging.info(f"Closing database session for task {task_id}.")
        db_session.close()
