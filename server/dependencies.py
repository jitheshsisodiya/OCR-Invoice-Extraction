"""FastAPI dependency injection helpers."""
from db.session import get_session as _get_session
from sqlalchemy.orm import Session


def get_db() -> Session:
    db = _get_session()
    try:
        yield db
    finally:
        db.close()
