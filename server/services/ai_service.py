"""AI-powered form extraction and document summarization via Claude API."""
from __future__ import annotations
from loguru import logger


def extract_form_fields(text: str, api_key: str) -> dict[str, str]:
    """
    Extract form fields from text using Claude API (if key available)
    with heuristic regex fallback.
    """
    from form_extraction.field_detector import heuristic_extract_fields
    from form_extraction.ai_form_extractor import claude_extract_fields

    # Try Claude first
    if api_key:
        claude_result = claude_extract_fields(text, api_key)
        if claude_result:
            return claude_result

    # Fallback to heuristic
    return heuristic_extract_fields(text)


def summarize_document(full_text: str, api_key: str) -> str:
    """
    Summarize a document using Claude API.
    Returns empty string if API key not available.
    """
    if not api_key:
        return ""

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        prompt = f"""Summarize this document in 3-5 bullet points covering:
- Document type and purpose
- Key parties involved
- Key amounts/dates/reference numbers
- Any important terms or flags

Document:
\"\"\"
{full_text[:6000]}
\"\"\"

Summary:"""
        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=400,
            messages=[{"role": "user", "content": prompt}],
        )
        return message.content[0].text.strip()
    except Exception as exc:
        logger.warning(f"Claude summarize failed: {exc}")
        return ""
