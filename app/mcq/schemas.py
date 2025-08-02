"""
Pydantic schemas for MCQ questions.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, field_validator


class MCQCreateRequest(BaseModel):
    """Schema for creating a new MCQ question."""
    
    title: str = Field(..., min_length=1, max_length=500, description="Question title")
    description: Optional[str] = Field(None, max_length=1000, description="Optional question description")
    option_1: str = Field(..., min_length=1, max_length=500, description="First option")
    option_2: str = Field(..., min_length=1, max_length=500, description="Second option")
    option_3: str = Field(..., min_length=1, max_length=500, description="Third option")
    option_4: str = Field(..., min_length=1, max_length=500, description="Fourth option")
    correct_answer: int = Field(..., ge=1, le=4, description="Correct answer (1, 2, 3, or 4)")
    
    @field_validator('correct_answer')
    @classmethod
    def validate_correct_answer(cls, v):
        """Validate that correct_answer is between 1 and 4."""
        if v < 1 or v > 4:
            raise ValueError('correct_answer must be between 1 and 4')
        return v
    
    model_config = ConfigDict(
        str_strip_whitespace=True,
        json_schema_extra={
            "example": {
                "title": "What is the capital of France?",
                "description": "A geography question about European capitals",
                "option_1": "London",
                "option_2": "Berlin",
                "option_3": "Paris",
                "option_4": "Madrid",
                "correct_answer": 3
            }
        }
    )


class MCQUpdateRequest(BaseModel):
    """Schema for updating an existing MCQ question."""
    
    title: Optional[str] = Field(None, min_length=1, max_length=500, description="Question title")
    description: Optional[str] = Field(None, max_length=1000, description="Question description")
    option_1: Optional[str] = Field(None, min_length=1, max_length=500, description="First option")
    option_2: Optional[str] = Field(None, min_length=1, max_length=500, description="Second option")
    option_3: Optional[str] = Field(None, min_length=1, max_length=500, description="Third option")
    option_4: Optional[str] = Field(None, min_length=1, max_length=500, description="Fourth option")
    correct_answer: Optional[int] = Field(None, ge=1, le=4, description="Correct answer (1, 2, 3, or 4)")
    
    @field_validator('correct_answer')
    @classmethod
    def validate_correct_answer(cls, v):
        """Validate that correct_answer is between 1 and 4."""
        if v is not None and (v < 1 or v > 4):
            raise ValueError('correct_answer must be between 1 and 4')
        return v
    
    model_config = ConfigDict(
        str_strip_whitespace=True,
        json_schema_extra={
            "example": {
                "title": "What is the capital of France?",
                "description": "An updated geography question about European capitals",
                "option_1": "London",
                "option_2": "Berlin",
                "option_3": "Paris",
                "option_4": "Madrid",
                "correct_answer": 3
            }
        }
    )


class MCQResponse(BaseModel):
    """Schema for MCQ question response."""
    
    id: int = Field(..., description="Question ID")
    title: str = Field(..., description="Question title")
    description: Optional[str] = Field(None, description="Question description")
    option_1: str = Field(..., description="First option")
    option_2: str = Field(..., description="Second option")
    option_3: str = Field(..., description="Third option")
    option_4: str = Field(..., description="Fourth option")
    correct_answer: int = Field(..., description="Correct answer (1, 2, 3, or 4)")
    test_id: int = Field(..., description="ID of the test this question belongs to")
    created_at: datetime = Field(..., description="Question creation timestamp")
    updated_at: datetime = Field(..., description="Question last update timestamp")
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "title": "What is the capital of France?",
                "description": "A geography question about European capitals",
                "option_1": "London",
                "option_2": "Berlin",
                "option_3": "Paris",
                "option_4": "Madrid",
                "correct_answer": 3,
                "test_id": 1,
                "created_at": "2024-01-08T10:00:00Z",
                "updated_at": "2024-01-08T10:00:00Z"
            }
        }
    )


class MCQListResponse(BaseModel):
    """Schema for MCQ question list response."""
    
    questions: list[MCQResponse] = Field(..., description="List of MCQ questions")
    total: int = Field(..., description="Total number of questions")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "questions": [
                    {
                        "id": 1,
                        "title": "What is the capital of France?",
                        "description": "A geography question about European capitals",
                        "option_1": "London",
                        "option_2": "Berlin",
                        "option_3": "Paris",
                        "option_4": "Madrid",
                        "correct_answer": 3,
                        "test_id": 1,
                        "created_at": "2024-01-08T10:00:00Z",
                        "updated_at": "2024-01-08T10:00:00Z"
                    }
                ],
                "total": 1
            }
        }
    )


class MCQPublicResponse(BaseModel):
    """Schema for MCQ question response without correct answer (for public viewing)."""
    
    id: int = Field(..., description="Question ID")
    title: str = Field(..., description="Question title")
    description: Optional[str] = Field(None, description="Question description")
    option_1: str = Field(..., description="First option")
    option_2: str = Field(..., description="Second option")
    option_3: str = Field(..., description="Third option")
    option_4: str = Field(..., description="Fourth option")
    test_id: int = Field(..., description="ID of the test this question belongs to")
    created_at: datetime = Field(..., description="Question creation timestamp")
    updated_at: datetime = Field(..., description="Question last update timestamp")
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "title": "What is the capital of France?",
                "description": "A geography question about European capitals",
                "option_1": "London",
                "option_2": "Berlin",
                "option_3": "Paris",
                "option_4": "Madrid",
                "test_id": 1,
                "created_at": "2024-01-08T10:00:00Z",
                "updated_at": "2024-01-08T10:00:00Z"
            }
        }
    )