"""Detect table grid lines in scanned images using OpenCV morphology."""
from __future__ import annotations
import cv2
import numpy as np
from PIL import Image


def detect_table_grid(image: Image.Image) -> list[dict]:
    """
    Detect table cells in a scanned image by finding horizontal and vertical lines.

    Returns:
        List of normalized bbox dicts {x1, y1, x2, y2} for each detected cell.
    """
    img = np.array(image.convert("L"))
    _, binary = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    h, w = binary.shape

    # Detect horizontal lines
    h_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (max(w // 30, 40), 1))
    h_lines = cv2.morphologyEx(binary, cv2.MORPH_OPEN, h_kernel)

    # Detect vertical lines
    v_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, max(h // 30, 40)))
    v_lines = cv2.morphologyEx(binary, cv2.MORPH_OPEN, v_kernel)

    # Combine
    grid = cv2.add(h_lines, v_lines)
    contours, _ = cv2.findContours(grid, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    cells: list[dict] = []
    min_area = (w * h) * 0.0005  # ignore tiny blobs
    for cnt in contours:
        x, y, cw, ch = cv2.boundingRect(cnt)
        if cw * ch < min_area:
            continue
        cells.append({
            "x1": x / w,
            "y1": y / h,
            "x2": (x + cw) / w,
            "y2": (y + ch) / h,
        })

    return cells
