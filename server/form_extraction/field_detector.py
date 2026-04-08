"""Heuristic regex-based form field extraction from OCR text."""
from __future__ import annotations
import re
from .invoice_schema import INVOICE_FIELDS


def heuristic_extract_fields(text: str) -> dict[str, str]:
    """
    Extract known invoice fields from raw text using regex patterns.
    Returns dict of { field_key: extracted_value }.
    Only populated fields are returned.
    """
    results: dict[str, str] = {}
    for field in INVOICE_FIELDS:
        for pattern in field["patterns"]:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                value = match.group(1).strip()
                if value:
                    results[field["key"]] = value
                    break  # first pattern wins
    return results
