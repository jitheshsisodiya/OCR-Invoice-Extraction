"""Clip creation service — Text Clip, Table Clip, Calc Clip."""
from __future__ import annotations
from sqlalchemy.orm import Session
from db.models.clip_mapping import ClipMapping
from db.models.validation import ValidationRecord
from pdf_processing.page_renderer import render_page
from pdf_processing.detector import detect_document_type
from image_processing.preprocessor import preprocess_for_ocr
from image_processing.deskewer import deskew
from image_processing.region_extractor import crop_region
from ocr.registry import get_engine
from ocr.cross_validator import compare_results
from table_extraction.camelot_extractor import CamelotTableExtractor
from table_extraction.opencv_extractor import OpenCVTableExtractor
from table_extraction.table_merger import reconcile_tables, normalize_table
from config import settings
from loguru import logger


def create_text_clip(
    db: Session,
    session_id: str,
    document_id: str,
    file_path: str,
    page_number: int,
    bbox: dict,
    excel_cell: str,
) -> ClipMapping:
    """OCR a region and store as text clip."""
    img = render_page(file_path, page_number, dpi=settings.ocr_dpi)
    doc_type = detect_document_type(file_path)

    extracted_text = ""
    confidence = 0.0
    engine_used = settings.default_ocr_engine

    if doc_type == "digital" and file_path.endswith(".pdf"):
        # Try PyMuPDF direct text extraction first
        from pdf_processing.digital_reader import extract_page_blocks
        blocks = extract_page_blocks(file_path, page_number)
        matched = _find_text_in_bbox(blocks, bbox)
        if matched:
            extracted_text = matched
            confidence = 1.0
            engine_used = "pymupdf"

    if not extracted_text:
        region = crop_region(img, bbox)
        region = deskew(region)
        region = preprocess_for_ocr(region)

        primary = get_engine(settings.default_ocr_engine)
        r1 = primary.extract(region)

        if settings.cross_validate_ocr:
            try:
                secondary = get_engine("easyocr")
                r2 = secondary.extract(region)
                result = compare_results(r1, r2)
                extracted_text = result["text"]
                confidence = result["confidence"]
                engine_used = "consensus"
            except Exception:
                extracted_text = r1.full_text
                confidence = r1.confidence
        else:
            extracted_text = r1.full_text
            confidence = r1.confidence

    clip = ClipMapping(
        session_id=session_id,
        clip_type="text",
        page_number=page_number,
        bbox=bbox,
        extracted_value=extracted_text,
        excel_cell=excel_cell,
        confidence=confidence,
        ocr_engine=engine_used,
    )
    db.add(clip)
    db.flush()   # assign clip.id before creating ValidationRecord
    _add_pending_validation(db, clip)
    db.commit()
    db.refresh(clip)
    return clip


def create_table_clip(
    db: Session,
    session_id: str,
    document_id: str,
    file_path: str,
    page_number: int,
    bbox: dict,
    excel_range: str,
) -> ClipMapping:
    """Extract a table from a bbox region."""
    doc_type = detect_document_type(file_path)

    tables: list[list[list[str]]] = []
    if doc_type == "digital" and file_path.endswith(".pdf"):
        camelot = CamelotTableExtractor()
        tables = camelot.extract(file_path, page_number)

    if not tables:
        img = render_page(file_path, page_number, dpi=settings.ocr_dpi)
        region = crop_region(img, bbox)
        ocr_eng = get_engine(settings.default_ocr_engine)
        cv_extractor = OpenCVTableExtractor(ocr_engine=ocr_eng)
        tables = cv_extractor.extract_from_image(region)

    table_data = normalize_table(tables[0]) if tables else [[]]

    clip = ClipMapping(
        session_id=session_id,
        clip_type="table",
        page_number=page_number,
        bbox=bbox,
        extracted_value=table_data,
        excel_range=excel_range,
        confidence=0.9 if tables else 0.0,
        ocr_engine="camelot" if doc_type == "digital" else "opencv+ocr",
    )
    db.add(clip)
    db.flush()   # assign clip.id before creating ValidationRecord
    _add_pending_validation(db, clip)
    db.commit()
    db.refresh(clip)
    return clip


def create_calc_clip(
    db: Session,
    session_id: str,
    clip_ids: list[str],
    excel_cell: str,
) -> ClipMapping:
    """
    Sum all numeric values from the given clip_ids and create a CalcClip.
    The extracted_value will be the SUM formula string.
    """
    source_cells = []
    for cid in clip_ids:
        c = db.query(ClipMapping).filter(ClipMapping.id == cid).first()
        if c and c.excel_cell:
            source_cells.append(c.excel_cell)

    if source_cells:
        # Build a SUM formula over the referenced cells
        formula = "=SUM(" + ",".join(source_cells) + ")"
    else:
        formula = "=SUM()"

    clip = ClipMapping(
        session_id=session_id,
        clip_type="calc",
        page_number=0,
        bbox={},
        extracted_value=formula,
        excel_cell=excel_cell,
        confidence=1.0,
        ocr_engine="formula",
    )
    db.add(clip)
    db.flush()   # assign clip.id before creating ValidationRecord
    _add_pending_validation(db, clip)
    db.commit()
    db.refresh(clip)
    return clip


def _add_pending_validation(db: Session, clip: ClipMapping) -> None:
    v = ValidationRecord(clip_mapping_id=clip.id, status="pending")
    db.add(v)


def _find_text_in_bbox(blocks: list[dict], bbox: dict) -> str:
    """Find digital PDF text blocks that overlap with the given bbox."""
    matched = []
    for block in blocks:
        if _overlaps(block, bbox, threshold=0.3):
            matched.append(block["text"])
    return " ".join(matched).strip()


def _overlaps(block: dict, bbox: dict, threshold: float) -> bool:
    ix1 = max(block["x1"], bbox["x1"])
    iy1 = max(block["y1"], bbox["y1"])
    ix2 = min(block["x2"], bbox["x2"])
    iy2 = min(block["y2"], bbox["y2"])
    if ix2 <= ix1 or iy2 <= iy1:
        return False
    inter_area = (ix2 - ix1) * (iy2 - iy1)
    bbox_area = (bbox["x2"] - bbox["x1"]) * (bbox["y2"] - bbox["y1"])
    return (inter_area / bbox_area) >= threshold if bbox_area > 0 else False
