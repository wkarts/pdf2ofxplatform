from __future__ import annotations

import json
import os
import shutil
import time
from contextlib import contextmanager
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any, Iterator
from uuid import UUID


class JobNotFoundError(FileNotFoundError):
    pass


class JobStore:
    def __init__(self, data_dir: Path, ttl_hours: int) -> None:
        self.data_dir = data_dir
        self.ttl_hours = ttl_hours
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def path(self, job_id: str) -> Path:
        UUID(job_id)
        return self.data_dir / job_id

    def create(
        self,
        job_id: str,
        original_name: str,
        bank_hint: str,
        output_format: str,
    ) -> dict[str, Any]:
        job_path = self.path(job_id)
        job_path.mkdir(mode=0o700, parents=True, exist_ok=False)
        now = datetime.now(UTC)
        payload: dict[str, Any] = {
            "job_id": job_id,
            "status": "queued",
            "original_name": original_name,
            "bank_hint": bank_hint,
            "output_format": output_format,
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
            "expires_at": (now + timedelta(hours=self.ttl_hours)).isoformat(),
            "progress": {"percent": 0, "message": "Conversão adicionada à fila."},
            "result": None,
            "error": None,
        }
        self.write(job_id, payload)
        return payload

    def read(self, job_id: str) -> dict[str, Any]:
        metadata = self.path(job_id) / "job.json"
        if not metadata.is_file():
            raise JobNotFoundError(job_id)
        return json.loads(metadata.read_text(encoding="utf-8"))

    def write(self, job_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        job_path = self.path(job_id)
        if not job_path.is_dir():
            raise JobNotFoundError(job_id)
        payload["updated_at"] = datetime.now(UTC).isoformat()
        metadata = job_path / "job.json"
        temporary = job_path / f".job-{os.getpid()}.tmp"
        temporary.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        os.replace(temporary, metadata)
        return payload

    def update(self, job_id: str, **changes: Any) -> dict[str, Any]:
        with self.lock(job_id):
            payload = self.read(job_id)
            payload.update(changes)
            return self.write(job_id, payload)

    @contextmanager
    def lock(self, job_id: str, timeout: float = 15.0) -> Iterator[None]:
        lock_path = self.path(job_id) / ".lock"
        started = time.monotonic()
        descriptor: int | None = None
        while descriptor is None:
            try:
                descriptor = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            except FileExistsError:
                if time.monotonic() - started > timeout:
                    raise TimeoutError(f"Timeout ao bloquear o job {job_id}.")
                time.sleep(0.05)
        try:
            os.write(descriptor, str(os.getpid()).encode())
            yield
        finally:
            os.close(descriptor)
            lock_path.unlink(missing_ok=True)

    def input_path(self, job_id: str) -> Path:
        return self.path(job_id) / "input.pdf"

    def output_path(self, job_id: str) -> Path:
        return self.path(job_id) / "output.ofx"

    def statement_path(self, job_id: str) -> Path:
        return self.path(job_id) / "statement.json"

    def cleanup_expired(self) -> int:
        now = datetime.now(UTC)
        removed = 0
        for candidate in self.data_dir.iterdir():
            if not candidate.is_dir():
                continue
            try:
                payload = json.loads((candidate / "job.json").read_text(encoding="utf-8"))
                expires = datetime.fromisoformat(payload["expires_at"])
            except (OSError, KeyError, ValueError, json.JSONDecodeError):
                expires = datetime.fromtimestamp(candidate.stat().st_mtime, tz=UTC) + timedelta(
                    hours=self.ttl_hours
                )
            if expires <= now:
                shutil.rmtree(candidate, ignore_errors=True)
                removed += 1
        return removed
