from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.session import get_session
from schemas.session import SessionIn, SessionOut
from services.session_service import create_session, get_session as get_sess

router = APIRouter(prefix="/sessions", tags=["sessions"])


def _db():
    db = get_session()
    try:
        yield db
    finally:
        db.close()


@router.post("", response_model=SessionOut)
def new_session(payload: SessionIn, db: Session = Depends(_db)):
    return create_session(db, payload.name, payload.document_id, payload.excel_sheet)


@router.get("/{session_id}", response_model=SessionOut)
def fetch_session(session_id: str, db: Session = Depends(_db)):
    try:
        return get_sess(db, session_id)
    except Exception:
        raise HTTPException(404, "Session not found")
