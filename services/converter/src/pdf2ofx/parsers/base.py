from __future__ import annotations

from abc import ABC, abstractmethod

from pdf2ofx.domain.models import ExtractedDocument, Statement


class StatementParser(ABC):
    key: str
    name: str

    @abstractmethod
    def detect(self, document: ExtractedDocument) -> float:
        raise NotImplementedError

    @abstractmethod
    def parse(self, document: ExtractedDocument) -> Statement:
        raise NotImplementedError
