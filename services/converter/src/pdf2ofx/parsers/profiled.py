from __future__ import annotations

from pdf2ofx.domain.models import ExtractedDocument, Statement
from pdf2ofx.parsers.base import StatementParser
from pdf2ofx.parsers.catalog import BankProfile
from pdf2ofx.parsers.universal import UniversalBrazilianParser


class ProfiledBankParser(StatementParser):
    def __init__(self, profile: BankProfile) -> None:
        self.profile = profile
        self.key = profile.key
        self.name = profile.name
        self._parser = UniversalBrazilianParser(profile)

    def detect(self, document: ExtractedDocument) -> float:
        return self._parser.detect(document)

    def parse(self, document: ExtractedDocument) -> Statement:
        return self._parser.parse(document)
