from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum as SAEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from src.db.base import Base
import enum
import datetime

class ReviewStatus(enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class PRReview(Base):
    __tablename__ = "pr_reviews"

    id = Column(String, primary_key=True, index=True)
    pr_number = Column(Integer, nullable=False)
    repo_id = Column(String, ForeignKey("repositories.id"), nullable=False)
    status = Column(SAEnum(ReviewStatus), default=ReviewStatus.PENDING)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    results = Column(JSONB, nullable=True)
