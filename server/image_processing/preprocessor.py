"""Image preprocessing pipeline for OCR quality improvement."""
from __future__ import annotations
import cv2
import numpy as np
from PIL import Image


def preprocess_for_ocr(image: Image.Image) -> Image.Image:
    """
    Apply a standard preprocessing pipeline to improve OCR accuracy:
    1. Convert to grayscale
    2. Denoise
    3. Adaptive threshold (binarize)

    Returns a processed PIL Image.
    """
    img = np.array(image.convert("RGB"))
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    denoised = cv2.fastNlMeansDenoising(gray, h=10)
    binary = cv2.adaptiveThreshold(
        denoised, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, 11, 2
    )
    return Image.fromarray(binary)


def enhance_contrast(image: Image.Image) -> Image.Image:
    """Apply CLAHE contrast enhancement."""
    img = np.array(image.convert("L"))
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(img)
    return Image.fromarray(enhanced)
