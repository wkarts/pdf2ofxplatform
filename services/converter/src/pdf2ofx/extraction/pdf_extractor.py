from __future__ import annotations

import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import pdfplumber
import pytesseract
from pdf2image import convert_from_path
from pypdf import PdfReader
from pytesseract import Output

from pdf2ofx.domain.models import ExtractedDocument, PositionedWord
from pdf2ofx.settings import Settings

_MONEY_OCCURRENCE = re.compile(r"\d{1,3}(?:\.\d{3})*,\d{2}")


class PdfExtractionError(RuntimeError):
    pass


class PdfExtractor:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def extract(self, path: Path) -> ExtractedDocument:
        self._validate_pdf(path)
        page_count, quick_text = self._inspect_pdf(path)

        # Some bank PDFs are printed as thousands of vector glyphs. Running
        # pdfplumber against those pages can be extremely slow even though
        # there is no usable text layer. The lightweight pypdf preflight lets
        # us go directly to OCR for that class of document.
        if self._quick_text_requires_ocr(quick_text):
            if not self.settings.ocr_enabled:
                raise PdfExtractionError(
                    "O PDF não possui texto utilizável e o OCR está desativado."
                )
            return self._extract_ocr(path, page_count)

        document = self._extract_native(path)
        if self._needs_ocr(document):
            if not self.settings.ocr_enabled:
                raise PdfExtractionError(
                    "O PDF não possui texto utilizável e o OCR está desativado."
                )
            return self._extract_ocr(path, page_count)
        return document

    def _validate_pdf(self, path: Path) -> None:
        if not path.is_file():
            raise PdfExtractionError("Arquivo PDF não encontrado.")
        if path.stat().st_size > self.settings.max_file_size:
            raise PdfExtractionError("O arquivo excede o limite configurado.")
        with path.open("rb") as stream:
            if stream.read(5) != b"%PDF-":
                raise PdfExtractionError(
                    "A assinatura do arquivo não corresponde a um PDF."
                )

    def _inspect_pdf(self, path: Path) -> tuple[int, str]:
        try:
            reader = PdfReader(str(path), strict=False)
            page_count = len(reader.pages)
        except Exception as exc:
            raise PdfExtractionError(f"Não foi possível inspecionar o PDF: {exc}") from exc

        if page_count < 1:
            raise PdfExtractionError("O PDF não possui páginas.")
        if page_count > self.settings.max_pages:
            raise PdfExtractionError(
                f"O PDF excede o limite de {self.settings.max_pages} páginas."
            )

        sample_indexes = list(range(min(page_count, 5)))
        if page_count > 5:
            sample_indexes.append(page_count - 1)

        fragments: list[str] = []
        for index in dict.fromkeys(sample_indexes):
            try:
                fragments.append(reader.pages[index].extract_text() or "")
            except Exception:
                # A native extractor will provide the final error when the PDF
                # appears to have text but a specific page is malformed.
                fragments.append("")
        return page_count, "\n".join(fragments)

    @staticmethod
    def _quick_text_requires_ocr(text: str) -> bool:
        visible_chars = len(re.sub(r"\s+", "", text))
        return visible_chars < 80

    def _extract_native(self, path: Path) -> ExtractedDocument:
        pages_text: list[str] = []
        words: list[PositionedWord] = []
        widths: dict[int, float] = {}
        heights: dict[int, float] = {}
        try:
            with pdfplumber.open(path) as pdf:
                if not pdf.pages:
                    raise PdfExtractionError("O PDF não possui páginas.")
                if len(pdf.pages) > self.settings.max_pages:
                    raise PdfExtractionError(
                        f"O PDF excede o limite de {self.settings.max_pages} páginas."
                    )
                for page_number, page in enumerate(pdf.pages, start=1):
                    widths[page_number] = float(page.width)
                    heights[page_number] = float(page.height)
                    page_text = page.extract_text(x_tolerance=2, y_tolerance=3) or ""
                    pages_text.append(page_text)
                    extracted = page.extract_words(
                        x_tolerance=2,
                        y_tolerance=3,
                        keep_blank_chars=False,
                        use_text_flow=False,
                    )
                    for item in extracted:
                        text = str(item.get("text", "")).strip()
                        if not text:
                            continue
                        words.append(
                            PositionedWord(
                                page=page_number,
                                text=text,
                                x0=float(item["x0"]),
                                top=float(item["top"]),
                                x1=float(item["x1"]),
                                bottom=float(item["bottom"]),
                            )
                        )
        except PdfExtractionError:
            raise
        except Exception as exc:
            raise PdfExtractionError(f"Falha ao ler o PDF: {exc}") from exc
        return ExtractedDocument(
            pages_text=pages_text,
            words=words,
            page_widths=widths,
            page_heights=heights,
            used_ocr=False,
        )

    @staticmethod
    def _needs_ocr(document: ExtractedDocument) -> bool:
        text = document.text
        money_count = len(_MONEY_OCCURRENCE.findall(text))
        visible_chars = len(re.sub(r"\s+", "", text))
        return visible_chars < 120 or money_count < 2 or len(document.words) < 20

    def _extract_ocr(self, path: Path, page_count: int) -> ExtractedDocument:
        def process(page_number: int) -> tuple[int, str, list[PositionedWord], float, float]:
            try:
                images = convert_from_path(
                    str(path),
                    dpi=self.settings.ocr_dpi,
                    fmt="png",
                    first_page=page_number,
                    last_page=page_number,
                    thread_count=1,
                    grayscale=True,
                    use_pdftocairo=False,
                )
                if not images:
                    raise PdfExtractionError(
                        f"A página {page_number} não pôde ser renderizada."
                    )
                image = images[0]
                data = pytesseract.image_to_data(
                    image,
                    lang=self.settings.ocr_language,
                    config=(
                        f"--oem 1 --psm {self.settings.ocr_psm} "
                        "-c preserve_interword_spaces=1"
                    ),
                    output_type=Output.DICT,
                    timeout=self.settings.ocr_page_timeout_seconds,
                )
            except PdfExtractionError:
                raise
            except Exception as exc:
                raise PdfExtractionError(
                    f"Falha no OCR da página {page_number}: {exc}"
                ) from exc

            page_words: list[PositionedWord] = []
            line_map: dict[tuple[int, int, int], list[tuple[int, str]]] = {}
            for index, raw_text in enumerate(data["text"]):
                text = str(raw_text).strip()
                if not text:
                    continue
                try:
                    confidence = max(
                        0.0,
                        min(1.0, float(data["conf"][index]) / 100.0),
                    )
                except (TypeError, ValueError):
                    confidence = 0.5
                left = float(data["left"][index])
                top = float(data["top"][index])
                width = float(data["width"][index])
                height = float(data["height"][index])
                page_words.append(
                    PositionedWord(
                        page=page_number,
                        text=text,
                        x0=left,
                        top=top,
                        x1=left + width,
                        bottom=top + height,
                        confidence=confidence,
                    )
                )
                key = (
                    int(data["block_num"][index]),
                    int(data["par_num"][index]),
                    int(data["line_num"][index]),
                )
                line_map.setdefault(key, []).append((int(left), text))
            page_lines = [
                " ".join(word for _, word in sorted(items))
                for _, items in sorted(line_map.items())
            ]
            return (
                page_number,
                "\n".join(page_lines),
                page_words,
                float(image.width),
                float(image.height),
            )

        workers = min(self.settings.ocr_workers, page_count)
        page_results: list[
            tuple[int, str, list[PositionedWord], float, float]
        ] = []
        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = {
                executor.submit(process, page_number): page_number
                for page_number in range(1, page_count + 1)
            }
            try:
                for future in as_completed(futures):
                    page_results.append(future.result())
            except Exception:
                for future in futures:
                    future.cancel()
                raise

        pages_text: list[str] = [""] * page_count
        words: list[PositionedWord] = []
        widths: dict[int, float] = {}
        heights: dict[int, float] = {}
        for page_number, page_text, page_words, width, height in sorted(page_results):
            pages_text[page_number - 1] = page_text
            words.extend(page_words)
            widths[page_number] = width
            heights[page_number] = height

        return ExtractedDocument(
            pages_text=pages_text,
            words=words,
            page_widths=widths,
            page_heights=heights,
            used_ocr=True,
        )
