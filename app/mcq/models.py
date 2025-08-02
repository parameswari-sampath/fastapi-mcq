"""
MCQ model for multiple choice questions.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, CheckConstraint
from sqlalchemy.orm import relationship, validates
from sqlalchemy.sql import func
from app.core.database import Base


class MCQ(Base):
    """MCQ model for multiple choice questions within tests."""
    
    __tablename__ = "mcq"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Question details
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True, default=None)
    
    # Four options for the multiple choice question
    option_1 = Column(String(500), nullable=False)
    option_2 = Column(String(500), nullable=False)
    option_3 = Column(String(500), nullable=False)
    option_4 = Column(String(500), nullable=False)
    
    # Correct answer (1, 2, 3, or 4)
    correct_answer = Column(Integer, nullable=False)
    
    # Foreign key to Test
    test_id = Column(Integer, ForeignKey("test.id"), nullable=False, index=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Soft delete flag
    is_deleted = Column(Boolean, default=False, nullable=False, index=True, server_default="false")
    
    # Database constraint for correct_answer validation
    __table_args__ = (
        CheckConstraint('correct_answer >= 1 AND correct_answer <= 4', name='check_correct_answer_range'),
    )
    
    # Relationships
    test = relationship("Test", back_populates="questions")
    
    @validates('correct_answer')
    def validate_correct_answer(self, key, value):
        """Validate that correct_answer is between 1 and 4."""
        if value is not None and (value < 1 or value > 4):
            raise ValueError("correct_answer must be between 1 and 4")
        return value
    
    def __repr__(self) -> str:
        """String representation of MCQ."""
        return f"<MCQ(id={self.id}, title='{self.title}', test_id={self.test_id}, correct_answer={self.correct_answer}, is_deleted={self.is_deleted})>"
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        return f"MCQ {self.id}: {self.title}"