"""
Test model for test management.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Test(Base):
    """Test model for organizing MCQ questions."""
    
    __tablename__ = "test"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Test details
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True, default=None)
    
    # Foreign key to User
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False, index=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Soft delete flag
    is_deleted = Column(Boolean, default=False, nullable=False, index=True, server_default="false")
    
    # Relationships
    user = relationship("User", back_populates="tests")
    questions = relationship("MCQ", back_populates="test", lazy="select")
    
    def __repr__(self) -> str:
        """String representation of Test."""
        return f"<Test(id={self.id}, title='{self.title}', user_id={self.user_id}, is_deleted={self.is_deleted})>"
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        return f"Test {self.id}: {self.title}"