"""Extract text and structure from digital (text-layer) PDFs using PyMuPDF."""
from __future__ import annotations
from pathlib import Path
import fitz  # PyMuPDF


def get_page_count(file_path: str | Path) -> int:
    doc = fitz.open(str(file_path))
    count = len(doc)
    doc.close()
    return count


def extract_page_text(file_path: str | Path, page_number: int) -> str:
    """
    Extract plain text from a single page (1-based).
    Returns empty string on error.
    """
    try:
        doc = fitz.open(str(file_path))
        page = doc[page_number - 1]
        text = page.get_text("text")
        doc.close()
        return text.strip()
    except Exception:
        return ""


def extract_page_blocks(file_path: str | Path, page_number: int) -> list[dict]:
    """
    Extract structured text blocks with their bounding boxes (normalized 0-1).

    Returns list of {text, x1, y1, x2, y2}.
    """
    try:
        doc = fitz.open(str(file_path))
        page = doc[page_number - 1]
        pw, ph = page.rect.width, page.rect.height
        blocks = []
        for block in page.get_text("blocks"):
            x1, y1, x2, y2, text = block[0], block[1], block[2], block[3], block[4]
            text = text.strip()
            if text:
                blocks.append({
                    "text": text,
                    "x1": x1 / pw,
                    "y1": y1 / ph,
                    "x2": x2 / pw,
                    "y2": y2 / ph,
                })
        doc.close()
        return blocks
    except Exception:
        return []


def extract_all_text(file_path: str | Path) -> str:
    """Extract and concatenate text from all pages."""
    try:
        doc = fitz.open(str(file_path))
        pages_text = [doc[i].get_text("text").strip() for i in range(len(doc))]
        doc.close()
        return "\n\n".join(pages_text)
    except Exception:
        return ""
