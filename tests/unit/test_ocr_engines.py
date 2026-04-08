"""Unit tests for OCR engine abstractions."""
import pytest
from unittest.mock import MagicMock, patch
from PIL import Image


def test_bounding_box_from_pixels():
    from ocr.result import BoundingBox
    bbox = BoundingBox.from_pixels(x=100, y=50, w=200, h=100, img_w=1000, img_h=500)
    assert bbox.x1 == pytest.approx(0.1)
    assert bbox.y1 == pytest.approx(0.1)
    assert bbox.x2 == pytest.approx(0.3)
    assert bbox.y2 == pytest.approx(0.3)


def test_bounding_box_to_pixels():
    from ocr.result import BoundingBox
    bbox = BoundingBox(x1=0.1, y1=0.1, x2=0.3, y2=0.3)
    x, y, w, h = bbox.to_pixels(1000, 500)
    assert x == 100
    assert y == 50
    assert w == 200
    assert h == 100


def test_bounding_box_to_dict():
    from ocr.result import BoundingBox
    bbox = BoundingBox(x1=0.1, y1=0.2, x2=0.5, y2=0.8)
    d = bbox.to_dict()
    assert d == {"x1": 0.1, "y1": 0.2, "x2": 0.5, "y2": 0.8}


def test_ocr_result_empty():
    from ocr.result import OCRResult
    r = OCRResult.empty("tesseract")
    assert r.full_text == ""
    assert r.confidence == 0.0
    assert r.engine == "tesseract"


def test_cross_validator_similar_texts():
    from ocr.cross_validator import compare_results, _texts_similar
    assert _texts_similar("hello world invoice", "hello world invoice") is True
    assert _texts_similar("hello world", "goodbye universe") is False


def test_cross_validator_picks_higher_confidence():
    from ocr.result import OCRResult
    from ocr.cross_validator import compare_results
    r1 = OCRResult(full_text="Invoice", words=[], confidence=0.9, engine="tesseract")
    r2 = OCRResult(full_text="Invoice", words=[], confidence=0.7, engine="easyocr")
    result = compare_results(r1, r2)
    assert result["text"] == "Invoice"
    assert result["confidence"] == pytest.approx(0.8)
    assert result["agreement"] is True
    assert result["needs_review"] is False


def test_cross_validator_flags_low_agreement():
    from ocr.result import OCRResult
    from ocr.cross_validator import compare_results
    r1 = OCRResult(full_text="INV-2024-001", words=[], confidence=0.95, engine="tesseract")
    r2 = OCRResult(full_text="TOTAL 14750", words=[], confidence=0.5, engine="easyocr")
    result = compare_results(r1, r2)
    assert result["needs_review"] is True


def test_ocr_registry_get_engine():
    from ocr.registry import _engines, register
    from ocr.result import OCRResult
    from ocr.base import OCREngine

    class DummyEngine(OCREngine):
        @property
        def name(self): return "dummy"
        def extract(self, image, lang="eng"): return OCRResult.empty("dummy")
        def extract_region(self, image, bbox_norm, lang="eng"): return OCRResult.empty("dummy")

    engine = DummyEngine()
    register(engine)
    from ocr.registry import get_engine
    assert get_engine("dummy") is engine
