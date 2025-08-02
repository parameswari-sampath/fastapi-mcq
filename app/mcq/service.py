"""
Service layer for MCQ business logic.
"""
from typing import List, Optional
from app.mcq.models import MCQ
from app.mcq.repository import MCQRepository
from app.mcq.schemas import MCQCreateRequest, MCQUpdateRequest, MCQResponse, MCQListResponse, MCQPublicResponse
from app.test_management.repository import TestRepository


class MCQService:
    """Service layer for MCQ business logic."""
    
    def __init__(self, mcq_repository: MCQRepository, test_repository: TestRepository):
        """Initialize service with MCQ and test repositories."""
        self.mcq_repository = mcq_repository
        self.test_repository = test_repository
    
    async def create_mcq(self, request: MCQCreateRequest, test_id: int, user_id: int) -> Optional[MCQResponse]:
        """Create a new MCQ question for the authenticated user's test."""
        # Check if user owns the test
        if not await self.test_repository.exists(test_id, user_id):
            return None
        
        mcq = await self.mcq_repository.create(
            title=request.title,
            description=request.description,
            option_1=request.option_1,
            option_2=request.option_2,
            option_3=request.option_3,
            option_4=request.option_4,
            correct_answer=request.correct_answer,
            test_id=test_id
        )
        
        return MCQResponse.model_validate(mcq)
    
    async def get_mcq(self, mcq_id: int, user_id: int) -> Optional[MCQResponse]:
        """Get an MCQ by ID if the user owns the test."""
        mcq = await self.mcq_repository.get_by_id(mcq_id)
        
        if not mcq:
            return None
        
        # Check if user owns the test that contains this MCQ
        if not await self.test_repository.exists(mcq.test_id, user_id):
            return None
        
        return MCQResponse.model_validate(mcq)
    
    async def get_mcq_public(self, mcq_id: int, user_id: int) -> Optional[MCQPublicResponse]:
        """Get an MCQ by ID without correct answer if the user owns the test."""
        mcq = await self.mcq_repository.get_by_id(mcq_id)
        
        if not mcq:
            return None
        
        # Check if user owns the test that contains this MCQ
        if not await self.test_repository.exists(mcq.test_id, user_id):
            return None
        
        return MCQPublicResponse.model_validate(mcq)
    
    async def get_test_mcqs(self, test_id: int, user_id: int) -> Optional[MCQListResponse]:
        """Get all MCQ questions for a test if the user owns the test."""
        # Check if user owns the test
        if not await self.test_repository.exists(test_id, user_id):
            return None
        
        mcqs = await self.mcq_repository.get_all_by_test(test_id)
        total = await self.mcq_repository.count_by_test(test_id)
        
        mcq_responses = [MCQResponse.model_validate(mcq) for mcq in mcqs]
        
        return MCQListResponse(questions=mcq_responses, total=total)
    
    async def update_mcq(self, mcq_id: int, request: MCQUpdateRequest, user_id: int) -> Optional[MCQResponse]:
        """Update an MCQ question if the user owns the test."""
        # Get the MCQ to check test ownership
        mcq = await self.mcq_repository.get_by_id(mcq_id)
        if not mcq:
            return None
        
        # Check if user owns the test that contains this MCQ
        if not await self.test_repository.exists(mcq.test_id, user_id):
            return None
        
        updated_mcq = await self.mcq_repository.update(
            mcq_id=mcq_id,
            title=request.title,
            description=request.description,
            option_1=request.option_1,
            option_2=request.option_2,
            option_3=request.option_3,
            option_4=request.option_4,
            correct_answer=request.correct_answer
        )
        
        if not updated_mcq:
            return None
        
        return MCQResponse.model_validate(updated_mcq)
    
    async def delete_mcq(self, mcq_id: int, user_id: int) -> bool:
        """Soft delete an MCQ question if the user owns the test."""
        # Get the MCQ to check test ownership
        mcq = await self.mcq_repository.get_by_id(mcq_id)
        if not mcq:
            return False
        
        # Check if user owns the test that contains this MCQ
        if not await self.test_repository.exists(mcq.test_id, user_id):
            return False
        
        return await self.mcq_repository.soft_delete(mcq_id)
    
    async def user_can_access_mcq(self, mcq_id: int, user_id: int) -> bool:
        """Check if the user can access the specified MCQ (via test ownership)."""
        mcq = await self.mcq_repository.get_by_id(mcq_id)
        if not mcq:
            return False
        
        return await self.test_repository.exists(mcq.test_id, user_id)
    
    async def get_mcq_by_test(self, mcq_id: int, test_id: int, user_id: int) -> Optional[MCQResponse]:
        """Get an MCQ by ID and test ID if the user owns the test."""
        # Check if user owns the test
        if not await self.test_repository.exists(test_id, user_id):
            return None
        
        mcq = await self.mcq_repository.get_by_id_and_test(mcq_id, test_id)
        
        if not mcq:
            return None
        
        return MCQResponse.model_validate(mcq)
    
    async def delete_all_test_mcqs(self, test_id: int, user_id: int) -> Optional[int]:
        """Soft delete all MCQ questions for a test if the user owns the test."""
        # Check if user owns the test
        if not await self.test_repository.exists(test_id, user_id):
            return None
        
        return await self.mcq_repository.soft_delete_all_by_test(test_id)