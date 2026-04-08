"""Unit tests for form/invoice field extraction."""
import pytest


def test_heuristic_invoice_number(sample_text):
    from form_extraction.field_detector import heuristic_extract_fields
    fields = heuristic_extract_fields(sample_text)
    assert "invoice_number" in fields
    assert "INV-2024-001" in fields["invoice_number"]


def test_heuristic_invoice_date(sample_text):
    from form_extraction.field_detector import heuristic_extract_fields
    fields = heuristic_extract_fields(sample_text)
    assert "invoice_date" in fields


def test_heuristic_total_amount(sample_text):
    from form_extraction.field_detector import heuristic_extract_fields
    fields = heuristic_extract_fields(sample_text)
    assert "total_amount" in fields


def test_heuristic_gstin(sample_text):
    from form_extraction.field_detector import heuristic_extract_fields
    fields = heuristic_extract_fields(sample_text)
    assert "gstin" in fields
    assert fields["gstin"] == "27AADCB2230M1ZT"


def test_heuristic_pan(sample_text):
    from form_extraction.field_detector import heuristic_extract_fields
    fields = heuristic_extract_fields(sample_text)
    assert "pan" in fields
    assert fields["pan"] == "AADCB2230M"


def test_empty_text_returns_empty():
    from form_extraction.field_detector import heuristic_extract_fields
    fields = heuristic_extract_fields("")
    assert isinstance(fields, dict)
