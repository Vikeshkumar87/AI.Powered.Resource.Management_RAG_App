"""
Feedback database model.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.sql import func

from app.database import Base


class Feedback(Base):
    """Represents user feedback and recommendation acceptance tracking."""

    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String(100), nullable=False, index=True)
    rating = Column(Integer, nullable=False)
    message = Column(Text, nullable=False)
    source_page = Column(String(100), nullable=True, index=True)
    accepted_recommendation = Column(Boolean, nullable=True, index=True)
    submitted_by = Column(String(150), nullable=True)
    user_role = Column(String(50), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Feedback(id={self.id}, category='{self.category}', rating={self.rating})>"