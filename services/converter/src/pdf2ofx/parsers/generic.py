from __future__ import annotations

from pdf2ofx.domain.models import ExtractedDocument, Statement
from pdf2ofx.parsers.base import StatementParser
from pdf2ofx.parsers.universal import UniversalBrazilianParser


class GenericParser(StatementParser):
    key = "generic"
    name = "Layout bancário universal"

    def __init__(self) -> None:
        self._parser = UniversalBrazilianParser()

    def detect(self, document: ExtractedDocument) -> float:
        return min(0.48, self._parser.detect(document))

    def parse(self, document: ExtractedDocument) -> Statement:
        return self._parser.parse(document)
