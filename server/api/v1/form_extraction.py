from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.session import get_session
from db.models.document import Document, DocumentPage
from schemas.export import FormExtractionRequest
from services.ai_service import extract_form_fields
from config import settings

router = APIRouter(prefix="/form-extraction", tags=["form-extraction"])


def _db():
    db = get_session()
    try:
        yield db
    finally:
        db.close()


@router.post("")
def extract_form(payload: FormExtractionRequest, db: Session = Depends(_db)):
    doc = db.query(Document).filter(Document.id == payload.document_id).first()
    if not doc:
        raise HTTPException(404, "Document not found")

    if payload.page_number:
        page = db.query(DocumentPage).filter(
            DocumentPage.document_id == payload.document_id,
            DocumentPage.page_number == payload.page_number,
        ).first()
        text = page.raw_text or "" if page else ""
    else:
        pages = db.query(DocumentPage).filter(
            DocumentPage.document_id == payload.document_id
        ).order_by(DocumentPage.page_number).all()
        text = "\n\n".join(p.raw_text or "" for p in pages)

    fields = extract_form_fields(text, settings.anthropic_api_key)
    return {"fields": fields}
