"""Document upload and retrieval endpoints."""
from __future__ import annotations
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from db.session import get_session
from db.models.document import Document, DocumentPage
from schemas.document import DocumentOut, DocumentPageOut
from schemas.export import ClipboardDocumentIn, EmailDocumentIn
from services.document_service import create_document_from_path, create_document_from_base64, SUPPORTED_EXTENSIONS
from storage.file_manager import save_upload
from pdf_processing.page_renderer import render_page_as_bytes
from config import settings
from pathlib import Path
import base64
import tempfile

router = APIRouter(prefix="/documents", tags=["documents"])


def _db() -> Session:
    db = get_session()
    try:
        yield db
    finally:
        db.close()


@router.post("/upload", response_model=DocumentOut)
async def upload_document(file: UploadFile = File(...), db: Session = Depends(_db)):
    ext = Path(file.filename or "").suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise HTTPException(400, f"Unsupported file type: {ext}")
    saved_path = await save_upload(file, settings.upload_dir)
    doc = create_document_from_path(db, saved_path, file.filename or saved_path.name)
    return doc


@router.post("/from-clipboard", response_model=DocumentOut)
def upload_clipboard(payload: ClipboardDocumentIn, db: Session = Depends(_db)):
    doc = create_document_from_base64(db, payload.data_b64, payload.suffix, source_type="clipboard")
    return doc


@router.post("/from-email", response_model=DocumentOut)
def upload_email(payload: EmailDocumentIn, db: Session = Depends(_db)):
    raw = base64.b64decode(payload.data_b64)
    ext = Path(payload.filename).suffix.lower() or ".pdf"
    from storage.file_manager import save_bytes
    path = save_bytes(raw, settings.upload_dir, suffix=ext)
    doc = create_document_from_path(db, path, payload.filename, source_type="email")
    return doc


@router.get("/{document_id}", response_model=DocumentOut)
def get_document(document_id: str, db: Session = Depends(_db)):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(404, "Document not found")
    return doc


@router.get("/{document_id}/pages/{page_number}", response_model=DocumentPageOut)
def get_page(document_id: str, page_number: int, db: Session = Depends(_db)):
    page = db.query(DocumentPage).filter(
        DocumentPage.document_id == document_id,
        DocumentPage.page_number == page_number,
    ).first()
    if not page:
        raise HTTPException(404, "Page not found")
    return page


@router.get("/{document_id}/pages/{page_number}/thumbnail")
def get_page_thumbnail(document_id: str, page_number: int, db: Session = Depends(_db)):
    page = db.query(DocumentPage).filter(
        DocumentPage.document_id == document_id,
        DocumentPage.page_number == page_number,
    ).first()
    if not page:
        raise HTTPException(404, "Page not found")

    if page.thumbnail_path and Path(page.thumbnail_path).exists():
        return FileResponse(page.thumbnail_path, media_type="image/png")

    # Re-render on demand
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(404, "Document not found")

    from fastapi.responses import Response
    img_bytes = render_page_as_bytes(doc.file_path, page_number, dpi=150, fmt="PNG")
    return Response(content=img_bytes, media_type="image/png")
