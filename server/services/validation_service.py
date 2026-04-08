"""Validation/Exception marking service."""
from __future__ import annotations
from datetime import datetime
from sqlalchemy.orm import Session
from db.models.validation import ValidationRecord


def set_validation_status(db: Session, clip_mapping_id: str, status: str, note: str | None = None) -> ValidationRecord:
    """status must be 'pending', 'validated', or 'exception'."""
    record = db.query(ValidationRecord).filter(
        ValidationRecord.clip_mapping_id == clip_mapping_id
    ).first()

    if record:
        record.status = status
        record.note = note
        record.updated_at = datetime.utcnow()
    else:
        record = ValidationRecord(
            clip_mapping_id=clip_mapping_id,
            status=status,
            note=note,
        )
        db.add(record)

    db.commit()
    db.refresh(record)
    return record


def get_validation(db: Session, validation_id: str) -> ValidationRecord | None:
    return db.query(ValidationRecord).filter(ValidationRecord.id == validation_id).first()


def update_validation(db: Session, validation_id: str, status: str, note: str | None = None) -> ValidationRecord:
    record = db.query(ValidationRecord).filter(ValidationRecord.id == validation_id).first()
    if not record:
        raise ValueError(f"ValidationRecord {validation_id} not found")
    record.status = status
    if note is not None:
        record.note = note
    record.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(record)
    return record
