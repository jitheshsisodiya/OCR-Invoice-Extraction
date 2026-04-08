from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.session import get_session
from schemas.clip import TextClipIn, TableClipIn, CalcClipIn, ClipOut
from services.clip_service import create_text_clip, create_table_clip, create_calc_clip

router = APIRouter(prefix="/clips", tags=["clips"])


def _db():
    db = get_session()
    try:
        yield db
    finally:
        db.close()


@router.post("/text", response_model=ClipOut)
def text_clip(payload: TextClipIn, db: Session = Depends(_db)):
    return create_text_clip(
        db,
        session_id=payload.session_id,
        document_id=payload.document_id,
        file_path=payload.file_path,
        page_number=payload.page_number,
        bbox=payload.bbox.model_dump(),
        excel_cell=payload.excel_cell,
    )


@router.post("/table", response_model=ClipOut)
def table_clip(payload: TableClipIn, db: Session = Depends(_db)):
    return create_table_clip(
        db,
        session_id=payload.session_id,
        document_id=payload.document_id,
        file_path=payload.file_path,
        page_number=payload.page_number,
        bbox=payload.bbox.model_dump(),
        excel_range=payload.excel_range,
    )


@router.post("/calc", response_model=ClipOut)
def calc_clip(payload: CalcClipIn, db: Session = Depends(_db)):
    return create_calc_clip(
        db,
        session_id=payload.session_id,
        clip_ids=payload.clip_ids,
        excel_cell=payload.excel_cell,
    )
