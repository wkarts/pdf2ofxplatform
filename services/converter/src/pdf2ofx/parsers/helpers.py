from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Iterable

from pdf2ofx.domain.models import PositionedWord
from pdf2ofx.domain.normalization import clean_text


@dataclass(slots=True)
class TextLine:
    page: int
    top: float
    words: list[PositionedWord]

    @property
    def text(self) -> str:
        ordered = sorted(self.words, key=lambda item: item.x0)
        return clean_text(" ".join(word.text for word in ordered))

    @property
    def min_x(self) -> float:
        return min(word.x0 for word in self.words)

    @property
    def max_x(self) -> float:
        return max(word.x1 for word in self.words)

    @property
    def confidence(self) -> float:
        return sum(item.confidence for item in self.words) / max(1, len(self.words))


def group_words_into_lines(
    words: Iterable[PositionedWord],
    tolerance: float = 4.0,
) -> list[TextLine]:
    by_page: dict[int, list[PositionedWord]] = defaultdict(list)
    for word in words:
        by_page[word.page].append(word)

    result: list[TextLine] = []
    for page, page_words in sorted(by_page.items()):
        lines: list[list[PositionedWord]] = []
        for word in sorted(page_words, key=lambda item: (item.top, item.x0)):
            target: list[PositionedWord] | None = None
            for candidate in reversed(lines[-8:]):
                candidate_top = sum(item.top for item in candidate) / len(candidate)
                if abs(candidate_top - word.top) <= tolerance:
                    target = candidate
                    break
            if target is None:
                target = []
                lines.append(target)
            target.append(word)
        for line in lines:
            top = sum(item.top for item in line) / len(line)
            result.append(
                TextLine(
                    page=page,
                    top=top,
                    words=sorted(line, key=lambda item: item.x0),
                )
            )
    return sorted(result, key=lambda line: (line.page, line.top))


def words_between_x(line: TextLine, x0: float, x1: float) -> list[PositionedWord]:
    return [word for word in line.words if word.x0 >= x0 and word.x1 <= x1]


def text_between_x(line: TextLine, x0: float, x1: float) -> str:
    return clean_text(" ".join(word.text for word in words_between_x(line, x0, x1)))
