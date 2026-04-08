from pydantic import BaseModel
from datetime import datetime


class BboxIn(BaseModel):
    x1: float
    y1: float
    x2: float
    y2: float


class TextClipIn(BaseModel):
    session_id: str
    document_id: str
    file_path: str
    page_number: int
    bbox: BboxIn
    excel_cell: str


class TableClipIn(BaseModel):
    session_id: str
    document_id: str
    file_path: str
    page_number: int
    bbox: BboxIn
    excel_range: str


class CalcClipIn(BaseModel):
    session_id: str
    clip_ids: list[str]
    excel_cell: str


class ClipOut(BaseModel):
    id: str
    session_id: str
    clip_type: str
    page_number: int
    bbox: str | None
    extracted_value: str | None
    excel_cell: str | None
    excel_range: str | None
    confidence: float
    ocr_engine: str
    created_at: datetime

    model_config = {"from_attributes": True}
