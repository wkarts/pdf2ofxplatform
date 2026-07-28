from __future__ import annotations

import logging
from typing import Any

from pdf2ofx.application.processor import ConversionProcessor
from pdf2ofx.application.status import result_status
from pdf2ofx.settings import get_settings
from pdf2ofx.storage.job_store import JobStore
from pdf2ofx.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(
    bind=True,
    autoretry_for=(),
    name="pdf2ofx.process_conversion",
)
def process_conversion(self: Any, job_id: str, bank_hint: str = "auto") -> dict[str, object]:
    settings = get_settings()
    store = JobStore(settings.data_dir, settings.job_ttl_hours)

    def progress(percent: int, message: str) -> None:
        store.update(
            job_id,
            status="processing",
            progress={"percent": percent, "message": message},
        )
        self.update_state(state="PROGRESS", meta={"percent": percent, "message": message})

    try:
        store.update(
            job_id,
            status="processing",
            progress={"percent": 5, "message": "Worker iniciou o processamento."},
            error=None,
        )
        result = ConversionProcessor(settings, store).process(
            job_id,
            bank_hint=bank_hint,
            progress=progress,
        )
        final_status = result_status(result)
        store.update(
            job_id,
            status=final_status,
            progress={
                "percent": 100,
                "message": (
                    "Conversão concluída com itens para revisão."
                    if final_status == "review_required"
                    else "Conversão concluída."
                ),
            },
            result=result,
            error=None,
        )
        return result
    except Exception as exc:
        logger.exception("Falha ao processar job %s", job_id)
        store.update(
            job_id,
            status="failed",
            progress={"percent": 100, "message": "Conversão interrompida."},
            error={
                "type": exc.__class__.__name__,
                "message": str(exc)[:1000],
            },
        )
        raise
    finally:
        store.input_path(job_id).unlink(missing_ok=True)
