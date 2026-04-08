"""WorkSession CRUD service."""
from __future__ import annotations
from sqlalchemy.orm import Session
from db.models.work_session import WorkSession
from core.exceptions import SessionNotFoundError


def create_session(db: Session, name: str, document_id: str, excel_sheet: str = "Sheet1") -> WorkSession:
    session = WorkSession(name=name, document_id=document_id, excel_sheet=excel_sheet)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def get_session(db: Session, session_id: str) -> WorkSession:
    session = db.query(WorkSession).filter(WorkSession.id == session_id).first()
    if not session:
        raise SessionNotFoundError(f"Session {session_id} not found")
    return session


def list_sessions(db: Session, document_id: str | None = None) -> list[WorkSession]:
    q = db.query(WorkSession)
    if document_id:
        q = q.filter(WorkSession.document_id == document_id)
    return q.all()
