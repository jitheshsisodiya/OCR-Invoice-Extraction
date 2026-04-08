from pydantic import BaseModel
from datetime import datetime


class ValidationIn(BaseModel):
    clip_mapping_id: str
    status: str  # pending|validated|exception
    note: str | None = None


class ValidationUpdate(BaseModel):
    status: str
    note: str | None = None


class ValidationOut(BaseModel):
    id: str
    clip_mapping_id: str
    status: str
    note: str | None
    updated_at: datetime

    model_config = {"from_attributes": True}
