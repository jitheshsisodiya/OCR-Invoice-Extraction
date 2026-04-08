from pydantic import BaseModel
from datetime import datetime


class SessionIn(BaseModel):
    name: str
    document_id: str
    excel_sheet: str = "Sheet1"


class SessionOut(BaseModel):
    id: str
    name: str
    document_id: str
    excel_sheet: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
