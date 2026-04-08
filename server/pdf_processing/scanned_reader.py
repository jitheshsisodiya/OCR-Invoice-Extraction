"""Convert scanned PDFs to PIL Images using pdf2image + poppler."""
from __future__ import annotations
from pathlib import Path
from PIL import Image


def pdf_to_images(file_path: str | Path, dpi: int = 300) -> list[Image.Image]:
    """
    Convert all pages of a scanned PDF to PIL Images.

    Args:
        file_path: Path to PDF.
        dpi:       Rendering resolution (300 recommended for OCR).

    Returns:
        List of PIL Images, one per page.
    """
    from pdf2image import convert_from_path
    images = convert_from_path(str(file_path), dpi=dpi)
    return images


def pdf_page_to_image(file_path: str | Path, page_number: int, dpi: int = 300) -> Image.Image:
    """
    Convert a single PDF page (1-based) to a PIL Image.
    """
    from pdf2image import convert_from_path
    images = convert_from_path(str(file_path), dpi=dpi, first_page=page_number, last_page=page_number)
    if not images:
        raise ValueError(f"Could not render page {page_number} of {file_path}")
    return images[0]
