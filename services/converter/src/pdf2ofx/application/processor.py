from __future__ import annotations

import json
from collections.abc import Callable

from pdf2ofx.domain.models import Statement
from pdf2ofx.exporters.ofx_102 import write_ofx
from pdf2ofx.extraction.pdf_extractor import PdfExtractor
from pdf2ofx.parsers.registry import ParserRegistry
from pdf2ofx.settings import Settings
from pdf2ofx.storage.job_store import JobStore
from pdf2ofx.validation.reconciliation import reconcile

ProgressCallback = Callable[[int, str], None]


class ConversionProcessor:
    def __init__(self, settings: Settings, store: JobStore) -> None:
        self.settings = settings
        self.store = store
        self.extractor = PdfExtractor(settings)
        self.registry = ParserRegistry()

    def process(
        self,
        job_id: str,
        bank_hint: str = "auto",
        progress: ProgressCallback | None = None,
    ) -> dict[str, object]:
        notify = progress or (lambda _percent, _message: None)
        input_path = self.store.input_path(job_id)

        notify(10, "Validando e extraindo o conteúdo do PDF.")
        document = self.extractor.extract(input_path)

        notify(45, "Identificando o banco e o layout do extrato.")
        parser = self.registry.select(document, bank_hint)

        notify(60, f"Interpretando o extrato com o parser {parser.name}.")
        statement = parser.parse(document)

        notify(78, "Validando saldos, duplicidades e confiança.")
        reconciliation = reconcile(statement)
        for warning in reconciliation["warnings"]:
            if warning not in statement.warnings:
                statement.warnings.append(str(warning))

        notify(90, "Gerando o arquivo OFX.")
        statement_path = self.store.statement_path(job_id)
        statement_path.write_text(
            json.dumps(statement.to_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        write_ofx(statement, self.store.output_path(job_id))

        notify(100, "Conversão concluída.")
        result = statement.to_dict()
        result["reconciliation"] = reconciliation
        result["used_ocr"] = document.used_ocr
        return result

    def regenerate(self, job_id: str, statement: Statement) -> dict[str, object]:
        reconciliation = reconcile(statement)
        statement.warnings = list(
            dict.fromkeys(
                statement.warnings + list(reconciliation["warnings"])
            )
        )
        self.store.statement_path(job_id).write_text(
            json.dumps(statement.to_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        write_ofx(statement, self.store.output_path(job_id))
        result = statement.to_dict()
        result["reconciliation"] = reconciliation
        return result
