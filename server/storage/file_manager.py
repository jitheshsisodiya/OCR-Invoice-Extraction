"""Manage uploaded files on disk."""
from __future__ import annotations
import shutil
import uuid
from pathlib import Path
from fastapi import UploadFile


async def save_upload(file: UploadFile, upload_dir: Path) -> Path:
    """Save an uploaded file to disk with a unique filename. Returns the saved path."""
    upload_dir.mkdir(parents=True, exist_ok=True)
    ext = Path(file.filename or "file").suffix.lower()
    unique_name = f"{uuid.uuid4()}{ext}"
    dest = upload_dir / unique_name
    with dest.open("wb") as f:
        shutil.copyfileobj(file.file, f)
    return dest


def save_bytes(data: bytes, upload_dir: Path, suffix: str = ".png") -> Path:
    """Save raw bytes to a uniquely named file. Returns path."""
    upload_dir.mkdir(parents=True, exist_ok=True)
    dest = upload_dir / f"{uuid.uuid4()}{suffix}"
    dest.write_bytes(data)
    return dest


def delete_file(path: str | Path) -> None:
    p = Path(path)
    if p.exists():
        p.unlink()
