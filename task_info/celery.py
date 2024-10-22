from celery import Celery

app = Celery("task_master")

app.conf.broker_url = "redis://redis:6379/0"
app.conf.result_backend = "redis://redis:6379/0"

app.autodiscover_tasks(["task_info.tasks"])
