from __future__ import annotations

from pdf2ofx.domain.models import ExtractedDocument
from pdf2ofx.parsers.base import StatementParser
from pdf2ofx.parsers.bnb import BnbParser
from pdf2ofx.parsers.generic import GenericParser
from pdf2ofx.parsers.itau import ItauParser
from pdf2ofx.parsers.santander import SantanderParser


class ParserRegistry:
    def __init__(self) -> None:
        self.parsers: dict[str, StatementParser] = {
            parser.key: parser
            for parser in (ItauParser(), BnbParser(), SantanderParser(), GenericParser())
        }

    def select(self, document: ExtractedDocument, hint: str = "auto") -> StatementParser:
        if hint != "auto":
            parser = self.parsers.get(hint)
            if parser is None:
                raise ValueError(f"Banco/parser não suportado: {hint}")
            return parser

        ranked = sorted(
            ((parser.detect(document), parser) for parser in self.parsers.values()),
            key=lambda item: item[0],
            reverse=True,
        )
        score, parser = ranked[0]
        if score < 0.20:
            raise ValueError(
                "Não foi possível identificar o banco. Selecione o banco manualmente."
            )
        return parser
