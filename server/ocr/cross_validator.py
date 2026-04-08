"""Cross-validate results from two OCR engines and produce a consensus."""
from __future__ import annotations
from .result import OCRResult

CONFIDENCE_DELTA_THRESHOLD = 0.20


def compare_results(r1: OCRResult, r2: OCRResult) -> dict:
    """
    Compare two OCR results and return a consensus dict.

    Returns:
        {
            "text":        str   — best text (higher-confidence engine wins),
            "confidence":  float — mean of both engines,
            "agreement":   bool  — True if texts are close / conf delta is small,
            "r1":          OCRResult,
            "r2":          OCRResult,
            "needs_review": bool — flag for low agreement / large delta
        }
    """
    delta = abs(r1.confidence - r2.confidence)
    text_match = _texts_similar(r1.full_text, r2.full_text)

    needs_review = (delta > CONFIDENCE_DELTA_THRESHOLD) and not text_match

    best = r1 if r1.confidence >= r2.confidence else r2
    mean_conf = (r1.confidence + r2.confidence) / 2.0

    return {
        "text": best.full_text,
        "confidence": mean_conf,
        "agreement": text_match,
        "needs_review": needs_review,
        "r1": r1,
        "r2": r2,
    }


def _texts_similar(a: str, b: str, threshold: float = 0.80) -> bool:
    """Return True if texts are ≥ threshold similar using token overlap."""
    if not a and not b:
        return True
    if not a or not b:
        return False
    tokens_a = set(a.lower().split())
    tokens_b = set(b.lower().split())
    if not tokens_a or not tokens_b:
        return False
    overlap = len(tokens_a & tokens_b)
    union = len(tokens_a | tokens_b)
    return (overlap / union) >= threshold
