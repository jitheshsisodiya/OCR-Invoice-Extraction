"""Page and document bulk extraction service."""
from __future__ import annotations
import json
from sqlalchemy.orm import Session
from db.models.clip_mapping import ClipMapping
from db.models.validation import ValidationRecord
from pdf_processing.page_renderer import render_page
from pdf_processing.detector import detect_document_type
from pdf_processing.digital_reader import extract_page_text, extract_page_blocks
from image_processing.preprocessor import preprocess_for_ocr
from image_processing.deskewer import deskew
from table_extraction.camelot_extractor import CamelotTableExtractor
from table_extraction.opencv_extractor import OpenCVTableExtractor
from table_extraction.table_merger import normalize_table
from ocr.registry import get_engine
from config import settings
from loguru import logger


def extract_page(db: Session, session_id: str, file_path: str, page_number: int) -> dict:
    """
    Extract all text + tables from a single page.
    Returns { "text_clips": [...], "table_clips": [...] }
    """
    doc_type = detect_document_type(file_path)
    results = {"text_clips": [], "table_clips": []}

    # Text extraction
    if doc_type == "digital" and file_path.endswith(".pdf"):
        text = extract_page_text(file_path, page_number)
        blocks = extract_page_blocks(file_path, page_number)
    else:
        img = render_page(file_path, page_number, dpi=settings.ocr_dpi)
        img = deskew(img)
        img = preprocess_for_ocr(img)
        engine = get_engine(settings.default_ocr_engine)
        ocr_result = engine.extract(img)
        text = ocr_result.full_text
        blocks = [{"text": text, "x1": 0.0, "y1": 0.0, "x2": 1.0, "y2": 1.0}]

    # Create one text clip per block
    for i, block in enumerate(blocks):
        if not block.get("text", "").strip():
            continue
        bbox = {"x1": block["x1"], "y1": block["y1"], "x2": block["x2"], "y2": block["y2"]}
        clip = ClipMapping(
            session_id=session_id,
            clip_type="text",
            page_number=page_number,
            bbox=json.dumps(bbox),
            extracted_value=json.dumps(block["text"].strip()),
            excel_cell=None,  # user assigns in Task Pane
            confidence=1.0 if doc_type == "digital" else 0.8,
            ocr_engine="pymupdf" if doc_type == "digital" else settings.default_ocr_engine,
        )
        db.add(clip)
        db.add(ValidationRecord(clip_mapping_id=clip.id, status="pending"))
        results["text_clips"].append(clip)

    # Table extraction
    tables = []
    if doc_type == "digital" and file_path.endswith(".pdf"):
        tables = CamelotTableExtractor().extract(file_path, page_number)
    else:
        img = render_page(file_path, page_number, dpi=settings.ocr_dpi)
        eng = get_engine(settings.default_ocr_engine)
        tables = OpenCVTableExtractor(ocr_engine=eng).extract_from_image(img)

    for table_data in tables:
        normalized = normalize_table(table_data)
        clip = ClipMapping(
            session_id=session_id,
            clip_type="table",
            page_number=page_number,
            bbox=json.dumps({"x1": 0.0, "y1": 0.0, "x2": 1.0, "y2": 1.0}),
            extracted_value=json.dumps(normalized),
            excel_range=None,
            confidence=0.9,
            ocr_engine="camelot" if doc_type == "digital" else "opencv",
        )
        db.add(clip)
        db.add(ValidationRecord(clip_mapping_id=clip.id, status="pending"))
        results["table_clips"].append(clip)

    db.commit()
    return results


def extract_document(db: Session, session_id: str, file_path: str, page_range: list[int]) -> dict:
    """Extract multiple pages. page_range = [start, end] inclusive, max 5 pages."""
    start, end = page_range[0], min(page_range[1], page_range[0] + 4)  # max 5 pages
    all_results = {"pages": {}}
    for page_num in range(start, end + 1):
        try:
            all_results["pages"][page_num] = extract_page(db, session_id, file_path, page_num)
        except Exception as exc:
            logger.warning(f"Failed to extract page {page_num}: {exc}")
            all_results["pages"][page_num] = {"error": str(exc)}
    return all_results
