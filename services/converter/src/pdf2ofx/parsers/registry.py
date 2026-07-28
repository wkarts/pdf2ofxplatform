from __future__ import annotations

from pdf2ofx.domain.models import ExtractedDocument
from pdf2ofx.parsers.base import StatementParser
from pdf2ofx.parsers.bnb import BnbParser
from pdf2ofx.parsers.catalog import (
    BANK_PROFILES,
    PROFILE_BY_KEY,
    canonical_bank_key,
    public_bank_catalog,
)
from pdf2ofx.parsers.generic import GenericParser
from pdf2ofx.parsers.itau import ItauParser
from pdf2ofx.parsers.profiled import ProfiledBankParser
from pdf2ofx.parsers.santander import SantanderParser


class ParserRegistry:
    def __init__(self) -> None:
        calibrated: tuple[StatementParser, ...] = (
            ItauParser(),
            BnbParser(),
            SantanderParser(),
        )
        calibrated_keys = {parser.key for parser in calibrated}
        profiled = tuple(
            ProfiledBankParser(profile)
            for profile in BANK_PROFILES
            if profile.key not in calibrated_keys
        )
        generic = GenericParser()

        ordered = (*calibrated, *profiled, generic)
        self.parsers: dict[str, StatementParser] = {parser.key: parser for parser in ordered}
        self._ordered = ordered

    @property
    def supported_keys(self) -> set[str]:
        return {"auto", *self.parsers.keys(), *PROFILE_BY_KEY.keys()}

    def catalog(self) -> list[dict[str, str]]:
        return public_bank_catalog()

    def select(self, document: ExtractedDocument, hint: str = "auto") -> StatementParser:
        canonical_hint = canonical_bank_key(hint)
        if canonical_hint != "auto":
            parser = self.parsers.get(canonical_hint)
            if parser is None:
                raise ValueError(f"Banco/parser não suportado: {hint}")
            return parser

        ranked = sorted(
            (
                (parser.detect(document), index, parser)
                for index, parser in enumerate(self._ordered)
            ),
            key=lambda item: (item[0], -item[1]),
            reverse=True,
        )
        score, _index, parser = ranked[0]
        if score < 0.18:
            return self.parsers["generic"]
        return parser
