"""
FastAPI router for MCQ endpoints.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.auth.models import User
from app.mcq.repository import MCQRepository
from app.mcq.service import MCQService
from app.mcq.schemas import (
    MCQCreateRequest,
    MCQUpdateRequest,
    MCQResponse,
    MCQListResponse,
    MCQPublicResponse
)
from app.test_management.repository import TestRepository

router = APIRouter(tags=["mcq"])


def get_mcq_service(db: AsyncSession = Depends(get_db)) -> MCQService:
    """Dependency to get MCQ service."""
    mcq_repository = MCQRepository(db)
    test_repository = TestRepository(db)
    return MCQService(mcq_repository, test_repository)


@router.post("/tests/{test_id}/questions", response_model=MCQResponse, status_code=status.HTTP_201_CREATED)
async def create_mcq_question(
    test_id: int,
    request: MCQCreateRequest,
    current_user: User = Depends(get_current_user),
    mcq_service: MCQService = Depends(get_mcq_service)
) -> MCQResponse:
    """Create a new MCQ question for a test."""
    try:
        mcq = await mcq_service.create_mcq(request, test_id, current_user.id)
        
        if not mcq:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Test not found or access denied"
            )
        
        return mcq
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create MCQ question"
        )


@router.get("/tests/{test_id}/questions", response_model=MCQListResponse)
async def get_test_questions(
    test_id: int,
    current_user: User = Depends(get_current_user),
    mcq_service: MCQService = Depends(get_mcq_service)
) -> MCQListResponse:
    """Get all MCQ questions for a test."""
    try:
        mcqs = await mcq_service.get_test_mcqs(test_id, current_user.id)
        
        if mcqs is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Test not found or access denied"
            )
        
        return mcqs
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve MCQ questions"
        )


@router.get("/questions/{question_id}", response_model=MCQResponse)
async def get_mcq_question(
    question_id: int,
    current_user: User = Depends(get_current_user),
    mcq_service: MCQService = Depends(get_mcq_service)
) -> MCQResponse:
    """Get a specific MCQ question by ID."""
    try:
        mcq = await mcq_service.get_mcq(question_id, current_user.id)
        
        if not mcq:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="MCQ question not found or access denied"
            )
        
        return mcq
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve MCQ question"
        )


@router.get("/questions/{question_id}/public", response_model=MCQPublicResponse)
async def get_mcq_question_public(
    question_id: int,
    current_user: User = Depends(get_current_user),
    mcq_service: MCQService = Depends(get_mcq_service)
) -> MCQPublicResponse:
    """Get a specific MCQ question by ID without correct answer."""
    try:
        mcq = await mcq_service.get_mcq_public(question_id, current_user.id)
        
        if not mcq:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="MCQ question not found or access denied"
            )
        
        return mcq
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve MCQ question"
        )


@router.get("/tests/{test_id}/questions/{question_id}", response_model=MCQResponse)
async def get_mcq_question_by_test(
    test_id: int,
    question_id: int,
    current_user: User = Depends(get_current_user),
    mcq_service: MCQService = Depends(get_mcq_service)
) -> MCQResponse:
    """Get a specific MCQ question by ID and test ID."""
    try:
        mcq = await mcq_service.get_mcq_by_test(question_id, test_id, current_user.id)
        
        if not mcq:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="MCQ question not found or access denied"
            )
        
        return mcq
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve MCQ question"
        )


@router.patch("/questions/{question_id}", response_model=MCQResponse)
async def update_mcq_question(
    question_id: int,
    request: MCQUpdateRequest,
    current_user: User = Depends(get_current_user),
    mcq_service: MCQService = Depends(get_mcq_service)
) -> MCQResponse:
    """Update a specific MCQ question."""
    try:
        updated_mcq = await mcq_service.update_mcq(question_id, request, current_user.id)
        
        if not updated_mcq:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="MCQ question not found or access denied"
            )
        
        return updated_mcq
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update MCQ question"
        )


@router.patch("/questions/{question_id}/delete", status_code=status.HTTP_204_NO_CONTENT)
async def delete_mcq_question(
    question_id: int,
    current_user: User = Depends(get_current_user),
    mcq_service: MCQService = Depends(get_mcq_service)
) -> None:
    """Soft delete a specific MCQ question."""
    try:
        success = await mcq_service.delete_mcq(question_id, current_user.id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="MCQ question not found or access denied"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete MCQ question"
        )