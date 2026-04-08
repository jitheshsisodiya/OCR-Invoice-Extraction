"""Table extractor for scanned images using OpenCV grid detection + OCR."""
from __future__ import annotations
from pathlib import Path
from PIL import Image
from .base import TableExtractor
from image_processing.grid_detector import detect_table_grid
from image_processing.region_extractor import crop_region
from loguru import logger


class OpenCVTableExtractor(TableExtractor):
    """
    Detects table cells via grid line morphology, then OCR's each cell.
    Used for scanned PDFs / images.
    """

    def __init__(self, ocr_engine=None):
        self._ocr = ocr_engine  # injected at runtime

    def extract_from_image(self, image: Image.Image) -> list[list[list[str]]]:
        cells = detect_table_grid(image)
        if not cells:
            return []

        # Sort cells into rows by y1
        cells_sorted = sorted(cells, key=lambda c: (round(c["y1"], 2), c["x1"]))
        rows: list[list[dict]] = []
        current_row: list[dict] = []
        last_y = None
        row_threshold = 0.01

        for cell in cells_sorted:
            if last_y is None or abs(cell["y1"] - last_y) > row_threshold:
                if current_row:
                    rows.append(sorted(current_row, key=lambda c: c["x1"]))
                current_row = [cell]
                last_y = cell["y1"]
            else:
                current_row.append(cell)
        if current_row:
            rows.append(sorted(current_row, key=lambda c: c["x1"]))

        table: list[list[str]] = []
        for row_cells in rows:
            row_texts: list[str] = []
            for cell in row_cells:
                if self._ocr:
                    result = self._ocr.extract_region(image, cell)
                    row_texts.append(result.full_text.strip())
                else:
                    row_texts.append("")
            table.append(row_texts)

        return [table] if table else []

    def extract(self, file_path: str | Path, page_number: int) -> list[list[list[str]]]:
        try:
            from pdf_processing.page_renderer import render_page
            image = render_page(file_path, page_number, dpi=300)
            return self.extract_from_image(image)
        except Exception as exc:
            logger.warning(f"OpenCV table extraction failed: {exc}")
            return []
