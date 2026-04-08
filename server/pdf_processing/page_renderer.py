"""Render any supported document page to a PIL Image for display or OCR."""
from __future__ import annotations
from pathlib import Path
from PIL import Image


def render_page(file_path: str | Path, page_number: int, dpi: int = 150) -> Image.Image:
    """
    Render page_number (1-based) of any supported file to a PIL Image.

    Supported types: PDF (digital or scanned), PNG, JPG, TIFF.
    Uses lower DPI (150) for display thumbnails; use 300 for OCR.
    """
    path = Path(file_path)
    suffix = path.suffix.lower()

    if suffix in {".png", ".jpg", ".jpeg", ".tiff", ".tif", ".bmp"}:
        return Image.open(str(path)).convert("RGB")

    if suffix == ".pdf":
        try:
            import fitz
            doc = fitz.open(str(path))
            page = doc[page_number - 1]
            mat = fitz.Matrix(dpi / 72, dpi / 72)
            pix = page.get_pixmap(matrix=mat, alpha=False)
            doc.close()
            return Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
        except Exception:
            # Fallback to pdf2image
            from .scanned_reader import pdf_page_to_image
            return pdf_page_to_image(path, page_number, dpi=dpi)

    raise ValueError(f"Unsupported file type: {suffix}")


def render_page_as_bytes(file_path: str | Path, page_number: int, dpi: int = 150, fmt: str = "PNG") -> bytes:
    """Render page and return as PNG/JPEG bytes for API response."""
    import io
    img = render_page(file_path, page_number, dpi=dpi)
    buf = io.BytesIO()
    img.save(buf, format=fmt)
    return buf.getvalue()
