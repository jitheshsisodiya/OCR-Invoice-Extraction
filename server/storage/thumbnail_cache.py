"""Cache rendered page thumbnails as PNG files."""
from __future__ import annotations
from pathlib import Path
from PIL import Image


def get_thumbnail_path(thumbnail_dir: Path, document_id: str, page_number: int) -> Path:
    return thumbnail_dir / f"{document_id}_p{page_number}.png"


def cache_thumbnail(image: Image.Image, thumbnail_dir: Path, document_id: str, page_number: int) -> Path:
    """Save thumbnail PNG and return its path."""
    thumbnail_dir.mkdir(parents=True, exist_ok=True)
    path = get_thumbnail_path(thumbnail_dir, document_id, page_number)
    image.save(str(path), format="PNG")
    return path


def thumbnail_exists(thumbnail_dir: Path, document_id: str, page_number: int) -> bool:
    return get_thumbnail_path(thumbnail_dir, document_id, page_number).exists()
