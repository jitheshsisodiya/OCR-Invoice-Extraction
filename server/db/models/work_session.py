"""WorkSession database model."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from db.base import Base


class WorkSession(Base):
    __tablename__ = "work_sessions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    document_id = Column(String, ForeignKey("documents.id"), nullable=False)
    excel_sheet = Column(String, nullable=True)
    excel_path = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    document = relationship("Document", back_populates="sessions")
    clips = relationship("ClipMapping", back_populates="session", cascade="all, delete-orphan")
