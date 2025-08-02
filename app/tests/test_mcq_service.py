"""
Unit tests for MCQ service.
"""
import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime
from app.mcq.models import MCQ
from app.mcq.repository import MCQRepository
from app.mcq.service import MCQService
from app.mcq.schemas import MCQCreateRequest, MCQUpdateRequest, MCQResponse, MCQListResponse, MCQPublicResponse
from app.test_management.repository import TestRepository


@pytest_asyncio.fixture
async def mock_mcq_repository():
    """Create a mock MCQ repository."""
    return AsyncMock(spec=MCQRepository)


@pytest_asyncio.fixture
async def mock_test_repository():
    """Create a mock test repository."""
    return AsyncMock(spec=TestRepository)


@pytest_asyncio.fixture
async def mcq_service(mock_mcq_repository, mock_test_repository):
    """Create an MCQ service with mock repositories."""
    return MCQService(mock_mcq_repository, mock_test_repository)


@pytest_asyncio.fixture
def sample_mcq():
    """Create a sample MCQ object."""
    mcq = MagicMock(spec=MCQ)
    mcq.id = 1
    mcq.title = "What is the capital of France?"
    mcq.description = "A geography question"
    mcq.option_1 = "London"
    mcq.option_2 = "Berlin"
    mcq.option_3 = "Paris"
    mcq.option_4 = "Madrid"
    mcq.correct_answer = 3
    mcq.test_id = 1
    mcq.created_at = datetime(2024, 1, 8, 10, 0, 0)
    mcq.updated_at = datetime(2024, 1, 8, 10, 0, 0)
    mcq.is_deleted = False
    return mcq


class TestMCQService:
    """Test cases for MCQService."""
    
    @pytest.mark.asyncio
    async def test_create_mcq_success(self, mcq_service: MCQService, mock_mcq_repository: AsyncMock, 
                                     mock_test_repository: AsyncMock, sample_mcq: MCQ):
        """Test creating a new MCQ question successfully."""
        # Setup
        request = MCQCreateRequest(
            title="What is the capital of France?",
            description="A geography question",
            option_1="London",
            option_2="Berlin",
            option_3="Paris",
            option_4="Madrid",
            correct_answer=3
        )
        test_id = 1
        user_id = 1
        
        mock_test_repository.exists.return_value = True
        mock_mcq_repository.create.return_value = sample_mcq
        
        # Execute
        result = await mcq_service.create_mcq(request, test_id, user_id)
        
        # Verify
        mock_test_repository.exists.assert_called_once_with(test_id, user_id)
        mock_mcq_repository.create.assert_called_once_with(
            title="What is the capital of France?",
            description="A geography question",
            option_1="London",
            option_2="Berlin",
            option_3="Paris",
            option_4="Madrid",
            correct_answer=3,
            test_id=test_id
        )
        assert isinstance(result, MCQResponse)
        assert result.id == 1
        assert result.title == "What is the capital of France?"
        assert result.correct_answer == 3
        assert result.test_id == 1
    
    @pytest.mark.asyncio
    async def test_create_mcq_user_does_not_own_test(self, mcq_service: MCQService, mock_mcq_repository: AsyncMock, 
                                                    mock_test_repository: AsyncMock):
        """Test creating an MCQ when user doesn't own the test."""
        # Setup
        request = MCQCreateRequest(
            title="Question",
            option_1="A", option_2="B", option_3="C", option_4="D",
            correct_answer=1
        )
        test_id = 1
        user_id = 1
        
        mock_test_repository.exists.return_value = False
        
        # Execute
        result = await mcq_service.create_mcq(request, test_id, user_id)
        
        # Verify
        mock_test_repository.exists.assert_called_once_with(test_id, user_id)
        mock_mcq_repository.create.assert_not_called()
        assert result is None
    
    @pytest.mark.asyncio
    async def test_get_mcq_success(self, mcq_service: MCQService, mock_mcq_repository: AsyncMock, 
                                  mock_test_repository: AsyncMock, sample_mcq: MCQ):
        """Test getting an MCQ successfully."""
        # Setup
        mcq_id = 1
        user_id = 1
        
        mock_mcq_repository.get_by_id.return_value = sample_mcq
        mock_test_repository.exists.return_value = True
        
        # Execute
        result = await mcq_service.get_mcq(mcq_id, user_id)
        
        # Verify
        mock_mcq_repository.get_by_id.assert_called_once_with(mcq_id)
        mock_test_repository.exists.assert_called_once_with(sample_mcq.test_id, user_id)
        assert isinstance(result, MCQResponse)
        assert result.id == 1
        assert result.title == "What is the capital of France?"
        assert result.correct_answer == 3
    
    @pytest.mark.asyncio
    async def test_get_mcq_not_found(self, mcq_service: MCQService, mock_mcq_repository: AsyncMock, 
                                    mock_test_repository: AsyncMock):
        """Test getting a non-existent MCQ."""
        # Setup
        mcq_id = 999
        user_id = 1
        
        mock_mcq_repository.get_by_id.return_value = None
        
        # Execute
        result = await mcq_service.get_mcq(mcq_id, user_id)
        
        # Verify
        mock_mcq_repository.get_by_id.assert_called_once_with(mcq_id)
        mock_test_repository.exists.assert_not_called()
        assert result is None
    
    @pytest.mark.asyncio
    async def test_get_mcq_user_does_not_own_test(self, mcq_service: MCQService, mock_mcq_repository: AsyncMock, 
                                                 mock_test_repository: AsyncMock, sample_mcq: MCQ):
        """Test getting an MCQ when user doesn't own the test."""
        # Setup
        mcq_id = 1
        user_id = 2  # Different user
        
        mock_mcq_repository.get_by_id.return_value = sample_mcq
        mock_test_repository.exists.return_value = False
        
        # Execute
        result = await mcq_service.get_mcq(mcq_id, user_id)
        
        # Verify
        mock_mcq_repository.get_by_id.assert_called_once_with(mcq_id)
        mock_test_repository.exists.assert_called_once_with(sample_mcq.test_id, user_id)
        assert result is None
    
    @pytest.mark.asyncio
    async def test_get_mcq_public_success(self, mcq_service: MCQService, mock_mcq_repository: AsyncMock, 
                                         mock_test_repository: AsyncMock, sample_mcq: MCQ):
        """Test getting an MCQ in public format (without correct answer)."""
        # Setup
        mcq_id = 1
        user_id = 1
        
        mock_mcq_repository.get_by_id.return_value = sample_mcq
        mock_test_repository.exists.return_value = True
        
        # Execute
        result = await mcq_service.get_mcq_public(mcq_id, user_id)
        
        # Verify
        mock_mcq_repository.get_by_id.assert_called_once_with(mcq_id)
        mock_test_repository.exists.assert_called_once_with(sample_mcq.test_id, user_id)
        assert isinstance(result, MCQPublicResponse)
        assert result.id == 1
        assert result.title == "What is the capital of France?"
        # Verify correct_answer is not included in public response
        assert not hasattr(result, 'correct_answer')
    
    @pytest.mark.asyncio
    async def test_get_test_mcqs_success(self, mcq_service: MCQService, mock_mcq_repository: AsyncMock, 
                                        mock_test_repository: AsyncMock, sample_mcq: MCQ):
        """Test getting all MCQs for a test successfully."""
        # Setup
        test_id = 1
        user_id = 1
        mcqs = [sample_mcq]
        
        mock_test_repository.exists.return_value = True
        mock_mcq_repository.get_all_by_test.return_value = mcqs
        mock_mcq_repository.count_by_test.return_value = 1
        
        # Execute
        result = await mcq_service.get_test_mcqs(test_id, user_id)
        
        # Verify
        mock_test_repository.exists.assert_called_once_with(test_id, user_id)
        mock_mcq_repository.get_all_by_test.assert_called_once_with(test_id)
        mock_mcq_repository.count_by_test.assert_called_once_with(test_id)
        assert isinstance(result, MCQListResponse)
        assert len(result.questions) == 1
        assert result.total == 1
        assert result.questions[0].id == 1
    
    @pytest.mark.asyncio
    async def test_get_test_mcqs_user_does_not_own_test(self, mcq_service: MCQService, mock_mcq_repository: AsyncMock, 
                                                       mock_test_repository: AsyncMock):
        """Test getting MCQs when user doesn't own the test."""
        # Setup
        test_id = 1
        user_id = 2  # Different user
        
        mock_test_repository.exists.return_value = False
        
        # Execute
        result = await mcq_service.get_test_mcqs(test_id, user_id)
        
        # Verify
        mock_test_repository.exists.assert_called_once_with(test_id, user_id)
        mock_mcq_repository.get_all_by_test.assert_not_called()
        mock_mcq_repository.count_by_test.assert_not_called()
        assert result is None
    
    @pytest.mark.asyncio
    async def test_update_mcq_success(self, mcq_service: MCQService, mock_mcq_repository: AsyncMock, 
                                     mock_test_repository: AsyncMock, sample_mcq: MCQ):
        """Test updating an MCQ successfully."""
        # Setup
        mcq_id = 1
        user_id = 1
        request = MCQUpdateRequest(
            title="Updated question",
            correct_answer=2
        )
        
        updated_mcq = MagicMock(spec=MCQ)
        updated_mcq.id = 1
        updated_mcq.title = "Updated question"
        updated_mcq.description = "A geography question"
        updated_mcq.option_1 = "London"
        updated_mcq.option_2 = "Berlin"
        updated_mcq.option_3 = "Paris"
        updated_mcq.option_4 = "Madrid"
        updated_mcq.correct_answer = 2
        updated_mcq.test_id = 1
        updated_mcq.created_at = datetime(2024, 1, 8, 10, 0, 0)
        updated_mcq.updated_at = datetime(2024, 1, 8, 11, 0, 0)
        
        mock_mcq_repository.get_by_id.return_value = sample_mcq
        mock_test_repository.exists.return_value = True
        mock_mcq_repository.update.return_value = updated_mcq
        
        # Execute
        result = await mcq_service.update_mcq(mcq_id, request, user_id)
        
        # Verify
        mock_mcq_repository.get_by_id.assert_called_once_with(mcq_id)
        mock_test_repository.exists.assert_called_once_with(sample_mcq.test_id, user_id)
        mock_mcq_repository.update.assert_called_once_with(
            mcq_id=mcq_id,
            title="Updated question",
            description=None,
            option_1=None,
            option_2=None,
            option_3=None,
            option_4=None,
            correct_answer=2
        )
        assert isinstance(result, MCQResponse)
        assert result.id == 1
        assert result.title == "Updated question"
        assert result.correct_answer == 2
    
    @pytest.mark.asyncio
    async def test_update_mcq_not_found(self, mcq_service: MCQService, mock_mcq_repository: AsyncMock, 
                                       mock_test_repository: AsyncMock):
        """Test updating a non-existent MCQ."""
        # Setup
        mcq_id = 999
        user_id = 1
        request = MCQUpdateRequest(title="Updated question")
        
        mock_mcq_repository.get_by_id.return_value = None
        
        # Execute
        result = await mcq_service.update_mcq(mcq_id, request, user_id)
        
        # Verify
        mock_mcq_repository.get_by_id.assert_called_once_with(mcq_id)
        mock_test_repository.exists.assert_not_called()
        mock_mcq_repository.update.assert_not_called()
        assert result is None
    
    @pytest.mark.asyncio
    async def test_update_mcq_user_does_not_own_test(self, mcq_service: MCQService, mock_mcq_repository: AsyncMock, 
                                                    mock_test_repository: AsyncMock, sample_mcq: MCQ):
        """Test updating an MCQ when user doesn't own the test."""
        # Setup
        mcq_id = 1
        user_id = 2  # Different user
        request = MCQUpdateRequest(title="Updated question")
        
        mock_mcq_repository.get_by_id.return_value = sample_mcq
        mock_test_repository.exists.return_value = False
        
        # Execute
        result = await mcq_service.update_mcq(mcq_id, request, user_id)
        
        # Verify
        mock_mcq_repository.get_by_id.assert_called_once_with(mcq_id)
        mock_test_repository.exists.assert_called_once_with(sample_mcq.test_id, user_id)
        mock_mcq_repository.update.assert_not_called()
        assert result is None
    
    @pytest.mark.asyncio
    async def test_delete_mcq_success(self, mcq_service: MCQService, mock_mcq_repository: AsyncMock, 
                                     mock_test_repository: AsyncMock, sample_mcq: MCQ):
        """Test deleting an MCQ successfully."""
        # Setup
        mcq_id = 1
        user_id = 1
        
        mock_mcq_repository.get_by_id.return_value = sample_mcq
        mock_test_repository.exists.return_value = True
        mock_mcq_repository.soft_delete.return_value = True
        
        # Execute
        result = await mcq_service.delete_mcq(mcq_id, user_id)
        
        # Verify
        mock_mcq_repository.get_by_id.assert_called_once_with(mcq_id)
        mock_test_repository.exists.assert_called_once_with(sample_mcq.test_id, user_id)
        mock_mcq_repository.soft_delete.assert_called_once_with(mcq_id)
        assert result is True
    
    @pytest.mark.asyncio
    async def test_delete_mcq_not_found(self, mcq_service: MCQService, mock_mcq_repository: AsyncMock, 
                                       mock_test_repository: AsyncMock):
        """Test deleting a non-existent MCQ."""
        # Setup
        mcq_id = 999
        user_id = 1
        
        mock_mcq_repository.get_by_id.return_value = None
        
        # Execute
        result = await mcq_service.delete_mcq(mcq_id, user_id)
        
        # Verify
        mock_mcq_repository.get_by_id.assert_called_once_with(mcq_id)
        mock_test_repository.exists.assert_not_called()
        mock_mcq_repository.soft_delete.assert_not_called()
        assert result is False
    
    @pytest.mark.asyncio
    async def test_delete_mcq_user_does_not_own_test(self, mcq_service: MCQService, mock_mcq_repository: AsyncMock, 
                                                    mock_test_repository: AsyncMock, sample_mcq: MCQ):
        """Test deleting an MCQ when user doesn't own the test."""
        # Setup
        mcq_id = 1
        user_id = 2  # Different user
        
        mock_mcq_repository.get_by_id.return_value = sample_mcq
        mock_test_repository.exists.return_value = False
        
        # Execute
        result = await mcq_service.delete_mcq(mcq_id, user_id)
        
        # Verify
        mock_mcq_repository.get_by_id.assert_called_once_with(mcq_id)
        mock_test_repository.exists.assert_called_once_with(sample_mcq.test_id, user_id)
        mock_mcq_repository.soft_delete.assert_not_called()
        assert result is False
    
    @pytest.mark.asyncio
    async def test_user_can_access_mcq_success(self, mcq_service: MCQService, mock_mcq_repository: AsyncMock, 
                                              mock_test_repository: AsyncMock, sample_mcq: MCQ):
        """Test checking if user can access an MCQ successfully."""
        # Setup
        mcq_id = 1
        user_id = 1
        
        mock_mcq_repository.get_by_id.return_value = sample_mcq
        mock_test_repository.exists.return_value = True
        
        # Execute
        result = await mcq_service.user_can_access_mcq(mcq_id, user_id)
        
        # Verify
        mock_mcq_repository.get_by_id.assert_called_once_with(mcq_id)
        mock_test_repository.exists.assert_called_once_with(sample_mcq.test_id, user_id)
        assert result is True
    
    @pytest.mark.asyncio
    async def test_user_can_access_mcq_not_found(self, mcq_service: MCQService, mock_mcq_repository: AsyncMock, 
                                                 mock_test_repository: AsyncMock):
        """Test checking access for a non-existent MCQ."""
        # Setup
        mcq_id = 999
        user_id = 1
        
        mock_mcq_repository.get_by_id.return_value = None
        
        # Execute
        result = await mcq_service.user_can_access_mcq(mcq_id, user_id)
        
        # Verify
        mock_mcq_repository.get_by_id.assert_called_once_with(mcq_id)
        mock_test_repository.exists.assert_not_called()
        assert result is False
    
    @pytest.mark.asyncio
    async def test_get_mcq_by_test_success(self, mcq_service: MCQService, mock_mcq_repository: AsyncMock, 
                                          mock_test_repository: AsyncMock, sample_mcq: MCQ):
        """Test getting an MCQ by ID and test ID successfully."""
        # Setup
        mcq_id = 1
        test_id = 1
        user_id = 1
        
        mock_test_repository.exists.return_value = True
        mock_mcq_repository.get_by_id_and_test.return_value = sample_mcq
        
        # Execute
        result = await mcq_service.get_mcq_by_test(mcq_id, test_id, user_id)
        
        # Verify
        mock_test_repository.exists.assert_called_once_with(test_id, user_id)
        mock_mcq_repository.get_by_id_and_test.assert_called_once_with(mcq_id, test_id)
        assert isinstance(result, MCQResponse)
        assert result.id == 1
        assert result.title == "What is the capital of France?"
    
    @pytest.mark.asyncio
    async def test_get_mcq_by_test_user_does_not_own_test(self, mcq_service: MCQService, mock_mcq_repository: AsyncMock, 
                                                         mock_test_repository: AsyncMock):
        """Test getting an MCQ by test when user doesn't own the test."""
        # Setup
        mcq_id = 1
        test_id = 1
        user_id = 2  # Different user
        
        mock_test_repository.exists.return_value = False
        
        # Execute
        result = await mcq_service.get_mcq_by_test(mcq_id, test_id, user_id)
        
        # Verify
        mock_test_repository.exists.assert_called_once_with(test_id, user_id)
        mock_mcq_repository.get_by_id_and_test.assert_not_called()
        assert result is None
    
    @pytest.mark.asyncio
    async def test_delete_all_test_mcqs_success(self, mcq_service: MCQService, mock_mcq_repository: AsyncMock, 
                                               mock_test_repository: AsyncMock):
        """Test deleting all MCQs for a test successfully."""
        # Setup
        test_id = 1
        user_id = 1
        
        mock_test_repository.exists.return_value = True
        mock_mcq_repository.soft_delete_all_by_test.return_value = 3
        
        # Execute
        result = await mcq_service.delete_all_test_mcqs(test_id, user_id)
        
        # Verify
        mock_test_repository.exists.assert_called_once_with(test_id, user_id)
        mock_mcq_repository.soft_delete_all_by_test.assert_called_once_with(test_id)
        assert result == 3
    
    @pytest.mark.asyncio
    async def test_delete_all_test_mcqs_user_does_not_own_test(self, mcq_service: MCQService, mock_mcq_repository: AsyncMock, 
                                                              mock_test_repository: AsyncMock):
        """Test deleting all MCQs when user doesn't own the test."""
        # Setup
        test_id = 1
        user_id = 2  # Different user
        
        mock_test_repository.exists.return_value = False
        
        # Execute
        result = await mcq_service.delete_all_test_mcqs(test_id, user_id)
        
        # Verify
        mock_test_repository.exists.assert_called_once_with(test_id, user_id)
        mock_mcq_repository.soft_delete_all_by_test.assert_not_called()
        assert result is None