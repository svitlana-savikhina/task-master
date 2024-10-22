import logging
import os

from botocore.exceptions import ClientError
from dotenv import load_dotenv

from database import SessionLocal
from task_info.celery import Celery
import time
import boto3

from task_info.crud_ import get_task, update_task_status
from .logging_config import setup_logging

setup_logging("task_master.log")

load_dotenv()
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

# Initializing the SQS client
sqs = boto3.client("sqs", endpoint_url="http://localstack:4566", region_name="eu-central-1")


# Create the SQS queue if it does not exist
def create_queue(queue_name):
    try:
        # Check if the queue already exists
        response = sqs.list_queues()
        for url in response.get('QueueUrls', []):
            if queue_name in url:
                logging.info(f"Queue already exists: {url}")
                return url
        # Create the queue if it does not exist
        response = sqs.create_queue(QueueName=queue_name)
        logging.info(f"Queue created: {response['QueueUrl']}")
        return response['QueueUrl']
    except ClientError as e:
        logging.error(f"Error creating queue: {e}")
        return None


# Initialize the Celery app
queue_name = "my-queue"
create_queue(queue_name)

# Initializing Celery
celery_app = Celery("tasks",
                    broker="sqs://",
                    broker_transport_options={
                        'region': 'eu-central-1',
                        'queue_name_prefix': '',
                        'polling_interval': 10,
                        'visibility_timeout': 3600,
                        'endpoint_url': "http://localstack:4566",
                        'aws_access_key_id': AWS_ACCESS_KEY_ID,
                        'aws_secret_access_key': AWS_SECRET_ACCESS_KEY,
                    }
                    )

# Initializing the S3 client
s3 = boto3.client("s3", endpoint_url="http://localstack:4566")

# Getting parameters from environment variables
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")


@celery_app.task
def process_task(task_id: str):
    logging.info(f"Processing task with task_id: {task_id}")
    db_session = SessionLocal()

    try:
        db_task = get_task(db_session, task_id)

        update_task_status(db_session, task_id, "in progress")

        time.sleep(5)

        logging.info(f"Updating task {task_id} status to 'completed'")
        update_task_status(db_session, task_id, "completed")
        logging.info(f"Task {task_id} status set to 'completed'")

        # Write a file to S3
        logging.info(f"Writing task {task_id} result to S3 bucket.")
        s3.put_object(Bucket="my-bucket", Key=f"{task_id}.txt", Body=f"Task ID: {task_id}")
        logging.info(f"Task {task_id} result written to S3 bucket successfully.")

    except Exception as e:
        logging.error(f"An error occurred while processing task {task_id}: {str(e)}")
        update_task_status(db_session, task_id, "failed")
        logging.info(f"Task {task_id} status set to 'failed' due to an error.")
    finally:
        logging.info(f"Closing database session for task {task_id}.")
        db_session.close()
