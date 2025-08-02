"""
User model for authentication.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class User(Base):
    """User model for authentication and authorization."""
    
    __tablename__ = "user"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # User credentials
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Soft delete flag
    is_deleted = Column(Boolean, default=False, nullable=False, index=True, server_default="false")
    
    # Relationships (lazy loaded to avoid circular imports)
    tests = relationship("Test", back_populates="user", lazy="select")
    
    def __repr__(self) -> str:
        """String representation of User."""
        return f"<User(id={self.id}, email='{self.email}', is_deleted={self.is_deleted})>"
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        return f"User {self.id}: {self.email}"