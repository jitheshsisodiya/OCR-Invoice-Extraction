"""Orchestrate full session export to .xlsx."""
from __future__ import annotations
from pathlib import Path
from sqlalchemy.orm import Session
from db.models.work_session import WorkSession
from excel_export.workbook_builder import build_workbook
from config import settings
from core.exceptions import SessionNotFoundError


def export_session_to_excel(db: Session, session_id: str) -> Path:
    """Export all clips in session to an .xlsx file. Returns file path."""
    session = db.query(WorkSession).filter(WorkSession.id == session_id).first()
    if not session:
        raise SessionNotFoundError(f"Session {session_id} not found")

    # Eagerly load clips + their validations + session.document
    db.refresh(session)
    path = build_workbook(session, settings.export_dir)

    # Update session with export path
    session.excel_path = str(path)
    db.commit()

    return path
