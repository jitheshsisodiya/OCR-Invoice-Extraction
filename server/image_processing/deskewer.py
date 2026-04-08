"""Deskew (rotation correction) for scanned documents."""
from __future__ import annotations
import cv2
import numpy as np
from PIL import Image


def deskew(image: Image.Image) -> Image.Image:
    """
    Detect and correct document skew using Hough line transform.
    Returns corrected PIL Image.
    """
    img = np.array(image.convert("L"))
    _, binary = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    coords = np.column_stack(np.where(binary > 0))
    if len(coords) < 10:
        return image  # not enough content to detect skew

    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle

    if abs(angle) < 0.5:
        return image  # negligible skew

    h, w = img.shape
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(np.array(image), M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return Image.fromarray(rotated)
