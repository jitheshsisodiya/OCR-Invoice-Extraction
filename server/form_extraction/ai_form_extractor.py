"""Claude API-based form field extraction (optional, requires API key)."""
from __future__ import annotations
import json
from .invoice_schema import INVOICE_FIELDS
from loguru import logger


def claude_extract_fields(text: str, api_key: str) -> dict[str, str]:
    """
    Use Claude (haiku-4-5) to extract invoice fields from text.
    Falls back to empty dict on any error.
    """
    if not api_key:
        return {}

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)

        field_list = "\n".join(f"- {f['key']}: {f['label']}" for f in INVOICE_FIELDS)
        prompt = f"""Extract the following fields from this invoice/document text.
Return ONLY a valid JSON object with the field keys below.
Use null for fields not found. Do not include any explanation.

Fields to extract:
{field_list}

Document text:
\"\"\"
{text[:4000]}
\"\"\"

JSON:"""

        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=512,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = message.content[0].text.strip()
        # Extract JSON from response
        json_match = raw
        if "```" in raw:
            json_match = raw.split("```")[1].replace("json", "").strip()
        data = json.loads(json_match)
        # Filter out null values
        return {k: v for k, v in data.items() if v is not None and str(v).strip()}
    except Exception as exc:
        logger.warning(f"Claude form extraction failed: {exc}")
        return {}
