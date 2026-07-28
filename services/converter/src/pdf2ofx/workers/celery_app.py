from __future__ import annotations

from celery import Celery

from pdf2ofx.settings import get_settings

settings = get_settings()

celery_app = Celery(
    "pdf2ofx",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["pdf2ofx.workers.tasks"],
)
celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="America/Sao_Paulo",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=1200,
    task_soft_time_limit=1140,
    worker_prefetch_multiplier=1,
    broker_connection_retry_on_startup=True,
    task_always_eager=settings.celery_eager,
    task_eager_propagates=settings.celery_eager,
)
