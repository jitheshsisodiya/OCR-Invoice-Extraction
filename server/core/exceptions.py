"""Custom exception hierarchy for the OCR server."""


class OCRInvoiceError(Exception):
    """Base exception."""


class OCRError(OCRInvoiceError):
    """Raised when OCR extraction fails."""


class ExtractionError(OCRInvoiceError):
    """Raised when data extraction fails."""


class DocumentNotFoundError(OCRInvoiceError):
    """Raised when a document ID is not found in DB."""


class SessionNotFoundError(OCRInvoiceError):
    """Raised when a session ID is not found in DB."""


class UnsupportedFileTypeError(OCRInvoiceError):
    """Raised for unsupported file types."""
