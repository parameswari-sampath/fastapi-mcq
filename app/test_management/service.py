"""
Service layer for test management business logic.
"""
from typing import List, Optional
from app.test_management.models import Test
from app.test_management.repository import TestRepository
from app.test_management.schemas import TestCreateRequest, TestUpdateRequest, TestResponse, TestListResponse


class TestService:
    """Service layer for test management business logic."""
    
    def __init__(self, test_repository: TestRepository):
        """Initialize service with test repository."""
        self.test_repository = test_repository
    
    async def create_test(self, request: TestCreateRequest, user_id: int) -> TestResponse:
        """Create a new test for the authenticated user."""
        test = await self.test_repository.create(
            title=request.title,
            description=request.description,
            user_id=user_id
        )
        
        return TestResponse.model_validate(test)
    
    async def get_test(self, test_id: int, user_id: int) -> Optional[TestResponse]:
        """Get a test by ID for the authenticated user."""
        test = await self.test_repository.get_by_id(test_id, user_id)
        
        if not test:
            return None
        
        return TestResponse.model_validate(test)
    
    async def get_user_tests(self, user_id: int) -> TestListResponse:
        """Get all tests for the authenticated user."""
        tests = await self.test_repository.get_all_by_user(user_id)
        total = await self.test_repository.count_by_user(user_id)
        
        test_responses = [TestResponse.model_validate(test) for test in tests]
        
        return TestListResponse(tests=test_responses, total=total)
    
    async def update_test(self, test_id: int, request: TestUpdateRequest, user_id: int) -> Optional[TestResponse]:
        """Update a test for the authenticated user."""
        # Check if user owns the test
        if not await self.test_repository.exists(test_id, user_id):
            return None
        
        updated_test = await self.test_repository.update(
            test_id=test_id,
            user_id=user_id,
            title=request.title,
            description=request.description
        )
        
        if not updated_test:
            return None
        
        return TestResponse.model_validate(updated_test)
    
    async def delete_test(self, test_id: int, user_id: int) -> bool:
        """Soft delete a test for the authenticated user."""
        return await self.test_repository.soft_delete(test_id, user_id)
    
    async def user_owns_test(self, test_id: int, user_id: int) -> bool:
        """Check if the user owns the specified test."""
        return await self.test_repository.exists(test_id, user_id)