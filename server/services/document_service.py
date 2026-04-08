"""Document upload, detection, and page ingestion service."""
from __future__ import annotations
import base64
from pathlib import Path
from sqlalchemy.orm import Session
from db.models.document import Document, DocumentPage
from pdf_processing.detector import detect_document_type
from pdf_processing.digital_reader import get_page_count, extract_page_text
from pdf_processing.scanned_reader import pdf_page_to_image
from pdf_processing.page_renderer import render_page
from storage.thumbnail_cache import cache_thumbnail
from image_processing.preprocessor import preprocess_for_ocr
from image_processing.deskewer import deskew
from ocr.registry import get_engine
from config import settings
from loguru import logger


SUPPORTED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".tiff", ".tif", ".bmp"}


def create_document_from_path(
    db: Session,
    file_path: Path,
    filename: str,
    source_type: str = "pdf_digital",
) -> Document:
    """Ingest a document: detect type, count pages, cache thumbnails, OCR text."""
    doc_type = detect_document_type(file_path)

    # Page count
    if file_path.suffix.lower() == ".pdf":
        from pdf_processing.digital_reader import get_page_count
        page_count = get_page_count(file_path)
    else:
        page_count = 1

    source_type = f"pdf_{doc_type}" if file_path.suffix.lower() == ".pdf" else source_type

    doc = Document(
        filename=filename,
        file_path=str(file_path),
        source_type=source_type,
        doc_type=doc_type,
        page_count=page_count,
    )
    db.add(doc)
    db.flush()  # get doc.id before adding pages

    for page_num in range(1, page_count + 1):
        _ingest_page(db, doc, file_path, page_num, doc_type)

    db.commit()
    db.refresh(doc)
    return doc


def _ingest_page(db: Session, doc: Document, file_path: Path, page_num: int, doc_type: str) -> None:
    """Render thumbnail + extract text for one page."""
    try:
        img = render_page(file_path, page_num, dpi=150)
        thumb_path = cache_thumbnail(img, settings.thumbnail_dir, doc.id, page_num)
        w, h = img.size
    except Exception as exc:
        logger.warning(f"Failed to render page {page_num}: {exc}")
        thumb_path = None
        w = h = None

    raw_text = ""
    if doc_type == "digital" and file_path.suffix.lower() == ".pdf":
        raw_text = extract_page_text(file_path, page_num)
    else:
        try:
            ocr_img = render_page(file_path, page_num, dpi=settings.ocr_dpi)
            ocr_img = deskew(ocr_img)
            ocr_img = preprocess_for_ocr(ocr_img)
            engine = get_engine(settings.default_ocr_engine)
            result = engine.extract(ocr_img)
            raw_text = result.full_text
        except Exception as exc:
            logger.warning(f"OCR failed for page {page_num}: {exc}")

    page = DocumentPage(
        document_id=doc.id,
        page_number=page_num,
        thumbnail_path=str(thumb_path) if thumb_path else None,
        raw_text=raw_text,
        width_px=w,
        height_px=h,
    )
    db.add(page)


def create_document_from_base64(db: Session, data_b64: str, suffix: str, source_type: str) -> Document:
    """Decode base64 image/PDF and ingest as document."""
    raw = base64.b64decode(data_b64)
    dest = settings.upload_dir / f"clipboard_{suffix}"
    from storage.file_manager import save_bytes
    path = save_bytes(raw, settings.upload_dir, suffix=suffix)
    return create_document_from_path(db, path, path.name, source_type=source_type)
