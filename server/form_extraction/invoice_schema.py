"""Known invoice / form field definitions for heuristic extraction."""

INVOICE_FIELDS = [
    {
        "key": "vendor_name",
        "label": "Vendor Name",
        "patterns": [
            r"(?:vendor|supplier|from|bill\s+from)[:\s]+([^\n]+)",
            r"^([A-Z][A-Za-z\s&.,]+(?:Ltd|LLC|Inc|Corp|Limited|Pvt)\.?)",
        ],
    },
    {
        "key": "invoice_number",
        "label": "Invoice Number",
        "patterns": [
            r"(?:invoice\s*(?:no|number|#)|inv\s*#?)[:\s]*([A-Z0-9\-/]+)",
        ],
    },
    {
        "key": "invoice_date",
        "label": "Invoice Date",
        "patterns": [
            r"(?:invoice\s+date|date\s+of\s+invoice|date)[:\s]+(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})",
            r"(?:invoice\s+date|date)[:\s]+([A-Za-z]+\s+\d{1,2},?\s+\d{4})",
        ],
    },
    {
        "key": "due_date",
        "label": "Due Date",
        "patterns": [
            r"(?:due\s+date|payment\s+due)[:\s]+(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})",
        ],
    },
    {
        "key": "po_number",
        "label": "PO Number",
        "patterns": [
            r"(?:purchase\s+order|po\s*(?:no|number|#)?)[:\s]*([A-Z0-9\-/]+)",
        ],
    },
    {
        "key": "subtotal",
        "label": "Subtotal",
        "patterns": [
            r"(?:subtotal|sub\s+total)[:\s]*(?:USD|INR|€|£|\$|Rs\.?)?\s*([\d,]+\.?\d*)",
        ],
    },
    {
        "key": "tax",
        "label": "Tax / GST / VAT",
        "patterns": [
            r"(?:tax|gst|vat|cgst|sgst|igst)[:\s@%0-9]*(?:USD|INR|€|£|\$|Rs\.?)?\s*([\d,]+\.?\d*)",
        ],
    },
    {
        "key": "total_amount",
        "label": "Total Amount",
        "patterns": [
            r"(?:total\s+amount|grand\s+total|amount\s+due|total)[:\s]*(?:USD|INR|€|£|\$|Rs\.?)?\s*([\d,]+\.?\d*)",
        ],
    },
    {
        "key": "gstin",
        "label": "GSTIN",
        "patterns": [
            r"(?:gstin|gst\s+(?:no|number|in))[:\s]*([0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1})",
        ],
    },
    {
        "key": "pan",
        "label": "PAN",
        "patterns": [
            r"(?:pan\s*(?:no|number)?)[:\s]*([A-Z]{5}[0-9]{4}[A-Z]{1})",
        ],
    },
]
