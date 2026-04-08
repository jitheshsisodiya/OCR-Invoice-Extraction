from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.session import get_session
from db.models.document import Document, DocumentPage
from schemas.export import SummarizeRequest
from services.ai_service import summarize_document
from config import settings

router = APIRouter(prefix="/summarize", tags=["summarize"])


def _db():
    db = get_session()
    try:
        yield db
    finally:
        db.close()


@router.post("")
def summarize(payload: SummarizeRequest, db: Session = Depends(_db)):
    doc = db.query(Document).filter(Document.id == payload.document_id).first()
    if not doc:
        raise HTTPException(404, "Document not found")

    pages = db.query(DocumentPage).filter(
        DocumentPage.document_id == payload.document_id
    ).order_by(DocumentPage.page_number).all()
    full_text = "\n\n".join(p.raw_text or "" for p in pages)

    if not settings.anthropic_api_key:
        return {"summary": "", "note": "Set ANTHROPIC_API_KEY to enable AI summarization."}

    summary = summarize_document(full_text, settings.anthropic_api_key)
    return {"summary": summary}
