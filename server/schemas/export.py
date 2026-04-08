from pydantic import BaseModel


class ExportRequest(BaseModel):
    session_id: str
    include_source_map: bool = True


class FormExtractionRequest(BaseModel):
    document_id: str
    page_number: int | None = None


class SummarizeRequest(BaseModel):
    document_id: str


class ClipboardDocumentIn(BaseModel):
    data_b64: str        # base64-encoded image or PDF
    suffix: str = ".png" # file extension


class EmailDocumentIn(BaseModel):
    data_b64: str        # base64-encoded attachment
    filename: str
