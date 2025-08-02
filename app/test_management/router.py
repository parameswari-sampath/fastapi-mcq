"""
FastAPI router for test management endpoints.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.auth.models import User
from app.test_management.repository import TestRepository
from app.test_management.service import TestService
from app.test_management.schemas import (
    TestCreateRequest,
    TestUpdateRequest,
    TestResponse,
    TestListResponse
)

router = APIRouter(prefix="/tests", tags=["tests"])


def get_test_service(db: AsyncSession = Depends(get_db)) -> TestService:
    """Dependency to get test service."""
    test_repository = TestRepository(db)
    return TestService(test_repository)


@router.post("/", response_model=TestResponse, status_code=status.HTTP_201_CREATED)
async def create_test(
    request: TestCreateRequest,
    current_user: User = Depends(get_current_user),
    test_service: TestService = Depends(get_test_service)
) -> TestResponse:
    """Create a new test."""
    try:
        return await test_service.create_test(request, current_user.id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create test"
        )


@router.get("/", response_model=TestListResponse)
async def get_user_tests(
    current_user: User = Depends(get_current_user),
    test_service: TestService = Depends(get_test_service)
) -> TestListResponse:
    """Get all tests for the authenticated user."""
    try:
        return await test_service.get_user_tests(current_user.id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve tests"
        )


@router.get("/{test_id}", response_model=TestResponse)
async def get_test(
    test_id: int,
    current_user: User = Depends(get_current_user),
    test_service: TestService = Depends(get_test_service)
) -> TestResponse:
    """Get a specific test by ID."""
    try:
        test = await test_service.get_test(test_id, current_user.id)
        
        if not test:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Test not found"
            )
        
        return test
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve test"
        )


@router.patch("/{test_id}", response_model=TestResponse)
async def update_test(
    test_id: int,
    request: TestUpdateRequest,
    current_user: User = Depends(get_current_user),
    test_service: TestService = Depends(get_test_service)
) -> TestResponse:
    """Update a specific test."""
    try:
        updated_test = await test_service.update_test(test_id, request, current_user.id)
        
        if not updated_test:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Test not found"
            )
        
        return updated_test
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update test"
        )


@router.patch("/{test_id}/delete", status_code=status.HTTP_204_NO_CONTENT)
async def delete_test(
    test_id: int,
    current_user: User = Depends(get_current_user),
    test_service: TestService = Depends(get_test_service)
) -> None:
    """Soft delete a specific test."""
    try:
        success = await test_service.delete_test(test_id, current_user.id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Test not found"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete test"
        )