"""Crop image regions using normalized bounding boxes."""
from __future__ import annotations
from PIL import Image


def crop_region(image: Image.Image, bbox_norm: dict) -> Image.Image:
    """
    Crop a region from image using normalized coordinates.

    Args:
        image:     Full-page PIL Image.
        bbox_norm: {x1, y1, x2, y2} all in 0–1 range.

    Returns:
        Cropped PIL Image.
    """
    w, h = image.size
    x1 = int(bbox_norm["x1"] * w)
    y1 = int(bbox_norm["y1"] * h)
    x2 = int(bbox_norm["x2"] * w)
    y2 = int(bbox_norm["y2"] * h)
    x1, x2 = max(0, x1), min(w, x2)
    y1, y2 = max(0, y1), min(h, y2)
    return image.crop((x1, y1, x2, y2))
