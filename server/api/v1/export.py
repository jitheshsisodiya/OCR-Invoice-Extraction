from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from db.session import get_session
from schemas.export import ExportRequest
from services.export_service import export_session_to_excel
from core.exceptions import SessionNotFoundError

router = APIRouter(prefix="/export", tags=["export"])


def _db():
    db = get_session()
    try:
        yield db
    finally:
        db.close()


@router.post("/excel")
def export_excel(payload: ExportRequest, db: Session = Depends(_db)):
    try:
        path = export_session_to_excel(db, payload.session_id)
    except SessionNotFoundError as e:
        raise HTTPException(404, str(e))
    return FileResponse(
        str(path),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=path.name,
    )
