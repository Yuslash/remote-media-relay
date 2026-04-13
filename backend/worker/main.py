import os
from celery import Celery
import logging

logging.basicConfig(level=logging.INFO, filename='logs/worker.log', filemode='a',
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

celery_app = Celery("worker", broker=REDIS_URL, backend=REDIS_URL)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600
)

# Autodiscover tasks
celery_app.autodiscover_tasks(["worker.tasks"])
