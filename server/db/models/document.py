"""Document and DocumentPage database models."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from db.base import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    source_type = Column(String, nullable=False)  # pdf_digital|pdf_scanned|image|email|clipboard
    doc_type = Column(String, nullable=False)      # digital|scanned
    page_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    pages = relationship("DocumentPage", back_populates="document", cascade="all, delete-orphan")
    sessions = relationship("WorkSession", back_populates="document")


class DocumentPage(Base):
    __tablename__ = "document_pages"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String, ForeignKey("documents.id"), nullable=False)
    page_number = Column(Integer, nullable=False)
    thumbnail_path = Column(String, nullable=True)
    raw_text = Column(String, nullable=True)
    width_px = Column(Integer, nullable=True)
    height_px = Column(Integer, nullable=True)

    document = relationship("Document", back_populates="pages")
