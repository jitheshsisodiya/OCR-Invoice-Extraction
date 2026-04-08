"""Detect whether a PDF has a selectable text layer (digital) or is image-only (scanned)."""
from __future__ import annotations
from pathlib import Path

MIN_CHARS_PER_PAGE = 100  # below this → treat as scanned


def detect_document_type(file_path: str | Path) -> str:
    """
    Inspect the PDF and return 'digital' or 'scanned'.

    For image files (PNG/JPG/TIFF) always returns 'scanned'.
    """
    path = Path(file_path)
    suffix = path.suffix.lower()

    if suffix in {".png", ".jpg", ".jpeg", ".tiff", ".tif", ".bmp"}:
        return "scanned"

    if suffix != ".pdf":
        return "scanned"

    try:
        import fitz  # PyMuPDF
        doc = fitz.open(str(path))
        total_chars = sum(len(page.get_text("text")) for page in doc)
        page_count = max(len(doc), 1)
        doc.close()
        avg_chars = total_chars / page_count
        return "digital" if avg_chars >= MIN_CHARS_PER_PAGE else "scanned"
    except Exception:
        return "scanned"
