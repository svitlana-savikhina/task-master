# Task master
Service for managing tasks that provides the ability to create, update, and retrieve information about tasks. The service uses FastAPI and SQLAlchemy to interact with the database and AWS SQS for asynchronous task processing. It also integrates S3 via LocalStack for file and data storage.
## Features
* Asynchronous task processing with AWS SQS.
* S3 integration for file storage (using LocalStack for local development).
* Automatic API documentation generation for http://127.0.0.1:8000/docs
##  Installation:
Python3 must be already installed

### 1.Clone the Repository:
```shell
git clone https://github.com/svitlana-savikhina/task-master.git
cd task-master
```
### 2.Environment Configuration: 
Create a .env file in the root directory with the following content, define environment variables in it (example you can find in .env_sample)

### 3.Activate venv:
```shell
python -m venv venv
source venv/bin/activate (Linux/Mac)
venv\Scripts\activate (Windows)
```
### 4.Install Dependencies:
```shell
pip install -r requirements.txt
```
### 5. Run Alembic Migrations:
```shell
 alembic upgrade head
```
### 6.Run:
```shell
uvicorn main:app --reload
```
This will start the FastAPI server and make the application available at http://127.0.0.1:8000.
## Run with Docker:
```shell
docker-compose build
docker-compose up
```






