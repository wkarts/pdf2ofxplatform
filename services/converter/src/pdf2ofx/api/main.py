from __future__ import annotations

import json
import shutil
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Annotated
from uuid import uuid4

from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from pdf2ofx import __version__
from pdf2ofx.api.dependencies import require_api_key
from pdf2ofx.api.schemas import HealthResponse, JobResponse, TransactionPatch
from pdf2ofx.application.processor import ConversionProcessor
from pdf2ofx.application.status import result_status
from pdf2ofx.domain.models import Statement
from pdf2ofx.domain.normalization import classify_transaction, create_fitid
from pdf2ofx.parsers.registry import ParserRegistry
from pdf2ofx.settings import get_settings
from pdf2ofx.storage.job_store import JobNotFoundError, JobStore
from pdf2ofx.workers.tasks import process_conversion

settings = get_settings()
store = JobStore(settings.data_dir, settings.job_ttl_hours)
registry = ParserRegistry()

app = FastAPI(
    title="PDF2OFX Converter API",
    version=__version__,
    docs_url="/docs" if settings.env != "production" else None,
    redoc_url=None,
    openapi_url="/openapi.json" if settings.env != "production" else None,
)

if settings.cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST", "PATCH"],
        allow_headers=["X-Internal-API-Key", "Content-Type"],
    )


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(version=__version__)


@app.get(
    "/v1/banks",
    dependencies=[Depends(require_api_key)],
)
def supported_banks() -> dict[str, object]:
    return {
        "banks": registry.catalog(),
        "fallback": {
            "key": "generic",
            "name": "Layout bancário universal",
        },
    }


def _read_job(job_id: str) -> dict:
    try:
        return store.read(job_id)
    except (JobNotFoundError, ValueError):
        raise HTTPException(status_code=404, detail="Conversão não encontrada.") from None


def _response(payload: dict, include_ttl: bool = False) -> JobResponse:
    response = dict(payload)
    if include_ttl:
        response["ttl_hours"] = settings.job_ttl_hours
    return JobResponse.model_validate(response)


@app.post(
    "/v1/conversions",
    response_model=JobResponse,
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(require_api_key)],
)
async def create_conversion(
    file: Annotated[UploadFile, File()],
    bank_hint: Annotated[str, Form()] = "auto",
    output_format: Annotated[str, Form()] = "ofx_102",
) -> JobResponse:
    if bank_hint not in registry.supported_keys:
        raise HTTPException(status_code=422, detail="Banco/parser inválido.")
    if output_format != "ofx_102":
        raise HTTPException(status_code=422, detail="Formato de saída não suportado.")

    original_name = Path(file.filename or "extrato.pdf").name[:255]
    job_id = str(uuid4())
    payload = store.create(job_id, original_name, bank_hint, output_format)
    destination = store.input_path(job_id)
    size = 0
    first_bytes = b""

    try:
        with destination.open("wb") as output:
            while chunk := await file.read(1024 * 1024):
                if not first_bytes:
                    first_bytes = chunk[:5]
                size += len(chunk)
                if size > settings.max_file_size:
                    raise HTTPException(status_code=413, detail="O PDF excede o limite permitido.")
                output.write(chunk)
        if first_bytes != b"%PDF-":
            raise HTTPException(
                status_code=422,
                detail="O arquivo enviado não possui assinatura PDF.",
            )
        process_conversion.delay(job_id, bank_hint)
    except Exception:
        shutil.rmtree(store.path(job_id), ignore_errors=True)
        raise
    finally:
        await file.close()

    return _response(payload, include_ttl=True)


@app.get(
    "/v1/conversions/{job_id}",
    response_model=JobResponse,
    dependencies=[Depends(require_api_key)],
)
def conversion_status(job_id: str) -> JobResponse:
    return _response(_read_job(job_id))


@app.patch(
    "/v1/conversions/{job_id}/transactions/{index}",
    response_model=JobResponse,
    dependencies=[Depends(require_api_key)],
)
def update_transaction(job_id: str, index: int, patch: TransactionPatch) -> JobResponse:
    payload = _read_job(job_id)
    if payload.get("status") not in {"completed", "review_required"}:
        raise HTTPException(status_code=409, detail="A conversão ainda não foi concluída.")

    statement_path = store.statement_path(job_id)
    if not statement_path.is_file():
        raise HTTPException(status_code=409, detail="Resultado intermediário indisponível.")
    statement = Statement.from_dict(json.loads(statement_path.read_text(encoding="utf-8")))
    if index < 0 or index >= len(statement.transactions):
        raise HTTPException(status_code=404, detail="Transação não encontrada.")

    transaction = statement.transactions[index]
    values = patch.model_dump(exclude_unset=True)
    if "posted_at" in values and values["posted_at"] is not None:
        try:
            transaction.posted_at = date.fromisoformat(values["posted_at"])
        except ValueError:
            raise HTTPException(status_code=422, detail="Data inválida.") from None
    if "description" in values and values["description"] is not None:
        transaction.description = values["description"].strip()
        if not transaction.description:
            raise HTTPException(status_code=422, detail="A descrição não pode ficar vazia.")
    if "document_number" in values:
        transaction.document_number = values["document_number"]
    if "amount" in values and values["amount"] is not None:
        transaction.amount = Decimal(str(values["amount"])).quantize(Decimal("0.01"))
    if "deleted" in values and values["deleted"] is not None:
        transaction.deleted = values["deleted"]

    transaction.transaction_type = classify_transaction(
        transaction.description, transaction.amount
    )
    transaction.fitid = create_fitid(
        transaction.posted_at,
        transaction.amount,
        transaction.description,
        transaction.document_number,
        index,
    )
    active = statement.active_transactions()
    if active:
        statement.start_date = min(item.posted_at for item in active)
        statement.end_date = max(item.posted_at for item in active)

    result = ConversionProcessor(settings, store).regenerate(job_id, statement)
    payload["result"] = result
    payload["status"] = result_status(result)
    payload["progress"] = {
        "percent": 100,
        "message": (
            "Alterações salvas; ainda existem itens para revisão."
            if payload["status"] == "review_required"
            else "Alterações salvas e extrato conciliado."
        ),
    }
    store.write(job_id, payload)
    return _response(payload)


@app.get(
    "/v1/conversions/{job_id}/download",
    dependencies=[Depends(require_api_key)],
)
def download_conversion(job_id: str) -> FileResponse:
    payload = _read_job(job_id)
    if payload.get("status") not in {"completed", "review_required"}:
        raise HTTPException(status_code=409, detail="O arquivo OFX ainda não está disponível.")
    output = store.output_path(job_id)
    if not output.is_file():
        raise HTTPException(status_code=404, detail="Arquivo OFX expirado ou indisponível.")
    filename = f"{Path(payload.get('original_name', 'extrato')).stem}.ofx"
    return FileResponse(
        path=output,
        filename=filename,
        media_type="application/x-ofx",
        headers={"Cache-Control": "private, no-store, max-age=0"},
    )
