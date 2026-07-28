from __future__ import annotations

from decimal import Decimal
from typing import Any, Literal

from pydantic import BaseModel, Field


class TransactionPatch(BaseModel):
    posted_at: str | None = None
    description: str | None = Field(default=None, max_length=500)
    document_number: str | None = Field(default=None, max_length=100)
    amount: Decimal | None = None
    deleted: bool | None = None


class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"
    version: str


class JobResponse(BaseModel):
    job_id: str
    status: str
    ttl_hours: int | None = None
    original_name: str | None = None
    created_at: str | None = None
    updated_at: str | None = None
    expires_at: str | None = None
    progress: dict[str, Any] | None = None
    result: dict[str, Any] | None = None
    error: dict[str, Any] | None = None
