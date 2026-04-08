"""OCR engine factory / registry."""
from __future__ import annotations
from .base import OCREngine


_engines: dict[str, OCREngine] = {}


def register(engine: OCREngine) -> None:
    _engines[engine.name] = engine


def get_engine(name: str) -> OCREngine:
    if name not in _engines:
        raise KeyError(f"OCR engine '{name}' not registered. Available: {list(_engines)}")
    return _engines[name]


def available() -> list[str]:
    return list(_engines.keys())


def init_default_engines(tesseract_cmd: str | None = None, easyocr_model_dir: str | None = None) -> None:
    """Register the default Tesseract + EasyOCR engines."""
    from .tesseract_engine import TesseractOCREngine
    from .easyocr_engine import EasyOCREngine

    register(TesseractOCREngine(cmd_path=tesseract_cmd))
    register(EasyOCREngine(model_dir=easyocr_model_dir, gpu=False))
