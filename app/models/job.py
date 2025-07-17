from sqlalchemy import Column, String, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid
from ..database import Base

class Job(Base):
    __tablename__ = "jobs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    video_id = Column(String(36), ForeignKey("videos.id"), nullable=False)
    status = Column(String(20), nullable=False, default="pending")  # pending, processing, completed, failed
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), onupdate=lambda: datetime.now(timezone.utc))
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    
    # Job metadata
    worker_id = Column(String(255))  # Identifier of the worker processing this job
    error_message = Column(String(1000))
    progress = Column(JSON)  # Progress information from worker
    
    # Relationship
    video = relationship("Video", backref="jobs")

    def to_dict(self):
        """Convert model to dictionary for API responses"""
        return {
            "id": self.id,
            "video_id": self.video_id,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "worker_id": self.worker_id,
            "error_message": self.error_message,
            "progress": self.progress,
        }