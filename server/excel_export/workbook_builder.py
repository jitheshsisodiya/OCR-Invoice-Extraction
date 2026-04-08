"""Build the exported Excel workbook from a WorkSession."""
from __future__ import annotations
import json
from pathlib import Path
import uuid
from openpyxl import Workbook
from db.models.work_session import WorkSession
from db.models.clip_mapping import ClipMapping
from .clip_writer import write_text_clip, write_table_clip
from .formula_writer import write_calc_clip
from .validation_styler import apply_validation_style
from .traceability_sheet import create_source_map_sheet
from loguru import logger


def build_workbook(session: WorkSession, export_dir: Path) -> Path:
    """
    Build an .xlsx file from all clips in the session.
    Returns the path to the saved file.
    """
    wb = Workbook()
    sheet_name = session.excel_sheet or "Sheet1"
    ws = wb.active
    ws.title = sheet_name

    clips = session.clips or []

    for clip in clips:
        try:
            val_status = clip.validation.status if clip.validation else "pending"
            _write_clip(ws, clip)
            # Apply validation color if cell is assigned
            if clip.excel_cell:
                cell_ref = clip.excel_cell.split("!")[-1] if "!" in clip.excel_cell else clip.excel_cell
                apply_validation_style(ws[cell_ref], val_status)
        except Exception as exc:
            logger.warning(f"Failed to write clip {clip.id}: {exc}")

    # Source Map sheet
    create_source_map_sheet(wb, clips)

    export_dir.mkdir(parents=True, exist_ok=True)
    out_path = export_dir / f"export_{session.id[:8]}_{uuid.uuid4().hex[:6]}.xlsx"
    wb.save(str(out_path))
    return out_path


def _write_clip(ws, clip: ClipMapping) -> None:
    value_raw = clip.extracted_value or "null"
    try:
        value = json.loads(value_raw)
    except Exception:
        value = value_raw

    if clip.clip_type == "text":
        if clip.excel_cell:
            write_text_clip(ws, clip.excel_cell, str(value))
    elif clip.clip_type == "table":
        if clip.excel_range and isinstance(value, list):
            write_table_clip(ws, clip.excel_range, value)
    elif clip.clip_type == "calc":
        if clip.excel_cell and isinstance(value, str) and value.startswith("="):
            write_calc_clip(ws, clip.excel_cell, value)
