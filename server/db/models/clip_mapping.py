"""ClipMapping database model — links extracted data to Excel cells."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from db.base import Base


class ClipMapping(Base):
    __tablename__ = "clip_mappings"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey("work_sessions.id"), nullable=False)
    clip_type = Column(String, nullable=False)          # text|table|calc
    page_number = Column(Integer, nullable=False)
    bbox = Column(JSON, nullable=True)                  # {x1,y1,x2,y2} normalized 0-1
    extracted_value = Column(JSON, nullable=True)       # string or 2D array for tables
    excel_cell = Column(String, nullable=True)          # e.g. "Sheet1!B5"
    excel_range = Column(String, nullable=True)         # e.g. "Sheet1!B5:E10" for tables
    confidence = Column(Float, default=0.0)
    ocr_engine = Column(String, default="tesseract")
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("WorkSession", back_populates="clips")
    validation = relationship("ValidationRecord", back_populates="clip", uselist=False, cascade="all, delete-orphan")
