"""SQLAlchemy engine + session factory."""
from __future__ import annotations
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from .base import Base

_engine = None
_SessionLocal = None


def init_db(database_url: str = "sqlite:///./ocr_invoice.db") -> None:
    global _engine, _SessionLocal
    _engine = create_engine(
        database_url,
        connect_args={"check_same_thread": False},  # SQLite-specific
    )
    _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)
    Base.metadata.create_all(bind=_engine)


def get_session() -> Session:
    if _SessionLocal is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    return _SessionLocal()
