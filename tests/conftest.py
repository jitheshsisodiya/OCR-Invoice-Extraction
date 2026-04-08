"""Pytest configuration and shared fixtures."""
import sys
import os
import pytest
from pathlib import Path
from unittest.mock import MagicMock

# Add server to path so imports work
sys.path.insert(0, str(Path(__file__).parent.parent / "server"))


@pytest.fixture
def sample_text():
    return """
    INVOICE
    Invoice No: INV-2024-001
    Date: 15/03/2024
    Due Date: 15/04/2024

    Vendor: Acme Supplies Ltd
    GSTIN: 27AADCB2230M1ZT
    PAN: AADCB2230M

    Bill To:
    XYZ Corporation

    Particulars          Amount
    Consulting Services  10,000.00
    Travel               2,500.00
    Subtotal             12,500.00
    GST @18%             2,250.00
    Total Amount         14,750.00
    """


@pytest.fixture
def mock_ocr_result():
    from ocr.result import OCRResult, OCRWord, BoundingBox
    word = OCRWord(
        text="Invoice",
        bbox=BoundingBox(x1=0.1, y1=0.1, x2=0.3, y2=0.15),
        confidence=0.95,
    )
    return OCRResult(full_text="Invoice", words=[word], confidence=0.95, engine="tesseract")
