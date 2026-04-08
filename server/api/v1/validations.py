from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.session import get_session
from schemas.validation import ValidationIn, ValidationUpdate, ValidationOut
from services.validation_service import set_validation_status, update_validation, get_validation

router = APIRouter(prefix="/validations", tags=["validations"])


def _db():
    db = get_session()
    try:
        yield db
    finally:
        db.close()


@router.post("", response_model=ValidationOut)
def create_validation(payload: ValidationIn, db: Session = Depends(_db)):
    return set_validation_status(db, payload.clip_mapping_id, payload.status, payload.note)


@router.patch("/{validation_id}", response_model=ValidationOut)
def update_validation_endpoint(validation_id: str, payload: ValidationUpdate, db: Session = Depends(_db)):
    try:
        return update_validation(db, validation_id, payload.status, payload.note)
    except ValueError as e:
        raise HTTPException(404, str(e))
