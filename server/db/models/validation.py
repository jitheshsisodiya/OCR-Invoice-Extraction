"""ValidationRecord database model."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from db.base import Base


class ValidationRecord(Base):
    __tablename__ = "validation_records"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    clip_mapping_id = Column(String, ForeignKey("clip_mappings.id"), nullable=False)
    status = Column(String, default="pending")    # pending|validated|exception
    note = Column(String, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    clip = relationship("ClipMapping", back_populates="validation")
