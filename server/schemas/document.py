from pydantic import BaseModel
from datetime import datetime


class DocumentOut(BaseModel):
    id: str
    filename: str
    source_type: str
    doc_type: str
    page_count: int
    created_at: datetime

    model_config = {"from_attributes": True}


class DocumentPageOut(BaseModel):
    id: str
    document_id: str
    page_number: int
    thumbnail_path: str | None
    raw_text: str | None
    width_px: int | None
    height_px: int | None

    model_config = {"from_attributes": True}
