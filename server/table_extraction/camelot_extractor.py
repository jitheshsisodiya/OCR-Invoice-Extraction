"""Table extractor for digital PDFs using camelot-py."""
from __future__ import annotations
from pathlib import Path
from .base import TableExtractor
from loguru import logger


class CamelotTableExtractor(TableExtractor):
    """
    Uses camelot-py with lattice (grid lines) first, stream (whitespace) fallback.
    Best for digital PDFs with visible table borders.
    """

    def extract(self, file_path: str | Path, page_number: int) -> list[list[list[str]]]:
        try:
            import camelot
            # Try lattice first (explicit grid lines)
            tables = camelot.read_pdf(str(file_path), pages=str(page_number), flavor="lattice")
            if len(tables) == 0:
                # Fallback to stream (whitespace-separated columns)
                tables = camelot.read_pdf(str(file_path), pages=str(page_number), flavor="stream")
            return [t.df.values.tolist() for t in tables]
        except Exception as exc:
            logger.warning(f"Camelot extraction failed (page {page_number}): {exc}")
            return []
