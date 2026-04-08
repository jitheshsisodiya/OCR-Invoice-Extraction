from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from db.session import get_session
from services.extraction_service import extract_page, extract_document

router = APIRouter(prefix="/extractions", tags=["extractions"])


def _db():
    db = get_session()
    try:
        yield db
    finally:
        db.close()


class PageExtractionIn(BaseModel):
    session_id: str
    file_path: str
    page_number: int


class DocumentExtractionIn(BaseModel):
    session_id: str
    file_path: str
    page_range: list[int]  # [start, end]


@router.post("/page")
def extract_page_endpoint(payload: PageExtractionIn, db: Session = Depends(_db)):
    result = extract_page(db, payload.session_id, payload.file_path, payload.page_number)
    return {
        "text_clips": len(result["text_clips"]),
        "table_clips": len(result["table_clips"]),
    }


@router.post("/document")
def extract_document_endpoint(payload: DocumentExtractionIn, db: Session = Depends(_db)):
    result = extract_document(db, payload.session_id, payload.file_path, payload.page_range)
    return {"pages_extracted": list(result["pages"].keys())}
