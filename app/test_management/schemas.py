"""
Pydantic schemas for test management.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class TestCreateRequest(BaseModel):
    """Schema for creating a new test."""
    
    title: str = Field(..., min_length=1, max_length=200, description="Test title")
    description: Optional[str] = Field(None, max_length=1000, description="Optional test description")
    
    model_config = ConfigDict(
        str_strip_whitespace=True,
        json_schema_extra={
            "example": {
                "title": "Python Basics Quiz",
                "description": "A comprehensive quiz covering Python fundamentals"
            }
        }
    )


class TestUpdateRequest(BaseModel):
    """Schema for updating an existing test."""
    
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="Test title")
    description: Optional[str] = Field(None, max_length=1000, description="Test description")
    
    model_config = ConfigDict(
        str_strip_whitespace=True,
        json_schema_extra={
            "example": {
                "title": "Updated Python Quiz",
                "description": "An updated comprehensive quiz covering Python fundamentals"
            }
        }
    )


class TestResponse(BaseModel):
    """Schema for test response."""
    
    id: int = Field(..., description="Test ID")
    title: str = Field(..., description="Test title")
    description: Optional[str] = Field(None, description="Test description")
    user_id: int = Field(..., description="ID of the user who created the test")
    created_at: datetime = Field(..., description="Test creation timestamp")
    updated_at: datetime = Field(..., description="Test last update timestamp")
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "title": "Python Basics Quiz",
                "description": "A comprehensive quiz covering Python fundamentals",
                "user_id": 1,
                "created_at": "2024-01-08T10:00:00Z",
                "updated_at": "2024-01-08T10:00:00Z"
            }
        }
    )


class TestListResponse(BaseModel):
    """Schema for test list response."""
    
    tests: list[TestResponse] = Field(..., description="List of tests")
    total: int = Field(..., description="Total number of tests")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "tests": [
                    {
                        "id": 1,
                        "title": "Python Basics Quiz",
                        "description": "A comprehensive quiz covering Python fundamentals",
                        "user_id": 1,
                        "created_at": "2024-01-08T10:00:00Z",
                        "updated_at": "2024-01-08T10:00:00Z"
                    }
                ],
                "total": 1
            }
        }
    )