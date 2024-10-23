import os
import time
import psycopg2
from psycopg2 import OperationalError
from dotenv import load_dotenv


load_dotenv()

DB_HOST = os.getenv("POSTGRES_HOST")
DB_NAME = os.getenv("POSTGRES_DB")
DB_USER = os.getenv("POSTGRES_USER")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB_PORT = os.getenv("POSTGRES_PORT")


def wait_for_db():
    while True:
        try:

            conn = psycopg2.connect(
                host=DB_HOST,
                database=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD,
                port=DB_PORT,
            )
            conn.close()
            print("Database is ready!")
            break
        except OperationalError:
            print("Database not ready, waiting...")
            time.sleep(2)  # Wait for 2 seconds before retrying


if __name__ == "__main__":
    wait_for_db()
