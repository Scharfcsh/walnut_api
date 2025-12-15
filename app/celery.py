from celery import Celery
from app.config import settings

celery_app = Celery(
    settings.app_name,
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.worker"],
)

celery_app.conf.update(
    task_default_queue="transactions",
    task_routes={
        "app.worker.process_transaction": {"queue": "transactions"},
    },
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)
