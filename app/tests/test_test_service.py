"""
Unit tests for Test service.
"""
import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime
from app.test_management.models import Test
from app.test_management.repository import TestRepository
from app.test_management.service import TestService
from app.test_management.schemas import TestCreateRequest, TestUpdateRequest, TestResponse, TestListResponse


@pytest_asyncio.fixture
async def mock_repository():
    """Create a mock test repository."""
    return AsyncMock(spec=TestRepository)


@pytest_asyncio.fixture
async def test_service(mock_repository):
    """Create a test service with mock repository."""
    return TestService(mock_repository)


@pytest_asyncio.fixture
def sample_test():
    """Create a sample test object."""
    test = MagicMock(spec=Test)
    test.id = 1
    test.title = "Python Quiz"
    test.description = "A comprehensive Python quiz"
    test.user_id = 1
    test.created_at = datetime(2024, 1, 8, 10, 0, 0)
    test.updated_at = datetime(2024, 1, 8, 10, 0, 0)
    test.is_deleted = False
    return test


class TestTestService:
    """Test cases for TestService."""
    
    @pytest.mark.asyncio
    async def test_create_test(self, test_service: TestService, mock_repository: AsyncMock, sample_test: Test):
        """Test creating a new test."""
        # Setup
        request = TestCreateRequest(
            title="Python Quiz",
            description="A comprehensive Python quiz"
        )
        user_id = 1
        mock_repository.create.return_value = sample_test
        
        # Execute
        result = await test_service.create_test(request, user_id)
        
        # Verify
        mock_repository.create.assert_called_once_with(
            title="Python Quiz",
            description="A comprehensive Python quiz",
            user_id=1
        )
        assert isinstance(result, TestResponse)
        assert result.id == 1
        assert result.title == "Python Quiz"
        assert result.description == "A comprehensive Python quiz"
        assert result.user_id == 1
    
    @pytest.mark.asyncio
    async def test_create_test_without_description(self, test_service: TestService, mock_repository: AsyncMock):
        """Test creating a test without description."""
        # Setup
        request = TestCreateRequest(title="Python Quiz")
        user_id = 1
        
        sample_test = MagicMock(spec=Test)
        sample_test.id = 1
        sample_test.title = "Python Quiz"
        sample_test.description = None
        sample_test.user_id = 1
        sample_test.created_at = datetime(2024, 1, 8, 10, 0, 0)
        sample_test.updated_at = datetime(2024, 1, 8, 10, 0, 0)
        
        mock_repository.create.return_value = sample_test
        
        # Execute
        result = await test_service.create_test(request, user_id)
        
        # Verify
        mock_repository.create.assert_called_once_with(
            title="Python Quiz",
            description=None,
            user_id=1
        )
        assert isinstance(result, TestResponse)
        assert result.description is None
    
    @pytest.mark.asyncio
    async def test_get_test(self, test_service: TestService, mock_repository: AsyncMock, sample_test: Test):
        """Test getting a test by ID."""
        # Setup
        test_id = 1
        user_id = 1
        mock_repository.get_by_id.return_value = sample_test
        
        # Execute
        result = await test_service.get_test(test_id, user_id)
        
        # Verify
        mock_repository.get_by_id.assert_called_once_with(1, 1)
        assert isinstance(result, TestResponse)
        assert result.id == 1
        assert result.title == "Python Quiz"
    
    @pytest.mark.asyncio
    async def test_get_test_not_found(self, test_service: TestService, mock_repository: AsyncMock):
        """Test getting a test that doesn't exist."""
        # Setup
        test_id = 999
        user_id = 1
        mock_repository.get_by_id.return_value = None
        
        # Execute
        result = await test_service.get_test(test_id, user_id)
        
        # Verify
        mock_repository.get_by_id.assert_called_once_with(999, 1)
        assert result is None
    
    @pytest.mark.asyncio
    async def test_get_user_tests(self, test_service: TestService, mock_repository: AsyncMock):
        """Test getting all tests for a user."""
        # Setup
        user_id = 1
        
        test1 = MagicMock(spec=Test)
        test1.id = 1
        test1.title = "Quiz 1"
        test1.description = "Description 1"
        test1.user_id = 1
        test1.created_at = datetime(2024, 1, 8, 10, 0, 0)
        test1.updated_at = datetime(2024, 1, 8, 10, 0, 0)
        
        test2 = MagicMock(spec=Test)
        test2.id = 2
        test2.title = "Quiz 2"
        test2.description = "Description 2"
        test2.user_id = 1
        test2.created_at = datetime(2024, 1, 8, 11, 0, 0)
        test2.updated_at = datetime(2024, 1, 8, 11, 0, 0)
        
        mock_repository.get_all_by_user.return_value = [test1, test2]
        mock_repository.count_by_user.return_value = 2
        
        # Execute
        result = await test_service.get_user_tests(user_id)
        
        # Verify
        mock_repository.get_all_by_user.assert_called_once_with(1)
        mock_repository.count_by_user.assert_called_once_with(1)
        assert isinstance(result, TestListResponse)
        assert len(result.tests) == 2
        assert result.total == 2
        assert result.tests[0].id == 1
        assert result.tests[1].id == 2
    
    @pytest.mark.asyncio
    async def test_get_user_tests_empty(self, test_service: TestService, mock_repository: AsyncMock):
        """Test getting tests for a user with no tests."""
        # Setup
        user_id = 1
        mock_repository.get_all_by_user.return_value = []
        mock_repository.count_by_user.return_value = 0
        
        # Execute
        result = await test_service.get_user_tests(user_id)
        
        # Verify
        assert isinstance(result, TestListResponse)
        assert len(result.tests) == 0
        assert result.total == 0
    
    @pytest.mark.asyncio
    async def test_update_test(self, test_service: TestService, mock_repository: AsyncMock, sample_test: Test):
        """Test updating a test."""
        # Setup
        test_id = 1
        user_id = 1
        request = TestUpdateRequest(
            title="Updated Quiz",
            description="Updated description"
        )
        
        updated_test = MagicMock(spec=Test)
        updated_test.id = 1
        updated_test.title = "Updated Quiz"
        updated_test.description = "Updated description"
        updated_test.user_id = 1
        updated_test.created_at = datetime(2024, 1, 8, 10, 0, 0)
        updated_test.updated_at = datetime(2024, 1, 8, 12, 0, 0)
        
        mock_repository.exists.return_value = True
        mock_repository.update.return_value = updated_test
        
        # Execute
        result = await test_service.update_test(test_id, request, user_id)
        
        # Verify
        mock_repository.exists.assert_called_once_with(1, 1)
        mock_repository.update.assert_called_once_with(
            test_id=1,
            user_id=1,
            title="Updated Quiz",
            description="Updated description"
        )
        assert isinstance(result, TestResponse)
        assert result.title == "Updated Quiz"
        assert result.description == "Updated description"
    
    @pytest.mark.asyncio
    async def test_update_test_not_owned(self, test_service: TestService, mock_repository: AsyncMock):
        """Test updating a test not owned by the user."""
        # Setup
        test_id = 1
        user_id = 1
        request = TestUpdateRequest(title="Updated Quiz")
        
        mock_repository.exists.return_value = False
        
        # Execute
        result = await test_service.update_test(test_id, request, user_id)
        
        # Verify
        mock_repository.exists.assert_called_once_with(1, 1)
        mock_repository.update.assert_not_called()
        assert result is None
    
    @pytest.mark.asyncio
    async def test_update_test_repository_returns_none(self, test_service: TestService, mock_repository: AsyncMock):
        """Test updating a test when repository returns None."""
        # Setup
        test_id = 1
        user_id = 1
        request = TestUpdateRequest(title="Updated Quiz")
        
        mock_repository.exists.return_value = True
        mock_repository.update.return_value = None
        
        # Execute
        result = await test_service.update_test(test_id, request, user_id)
        
        # Verify
        mock_repository.exists.assert_called_once_with(1, 1)
        mock_repository.update.assert_called_once()
        assert result is None
    
    @pytest.mark.asyncio
    async def test_update_test_partial(self, test_service: TestService, mock_repository: AsyncMock):
        """Test partially updating a test."""
        # Setup
        test_id = 1
        user_id = 1
        request = TestUpdateRequest(title="Updated Quiz")  # Only title
        
        updated_test = MagicMock(spec=Test)
        updated_test.id = 1
        updated_test.title = "Updated Quiz"
        updated_test.description = "Original description"
        updated_test.user_id = 1
        updated_test.created_at = datetime(2024, 1, 8, 10, 0, 0)
        updated_test.updated_at = datetime(2024, 1, 8, 12, 0, 0)
        
        mock_repository.exists.return_value = True
        mock_repository.update.return_value = updated_test
        
        # Execute
        result = await test_service.update_test(test_id, request, user_id)
        
        # Verify
        mock_repository.update.assert_called_once_with(
            test_id=1,
            user_id=1,
            title="Updated Quiz",
            description=None
        )
        assert isinstance(result, TestResponse)
        assert result.title == "Updated Quiz"
    
    @pytest.mark.asyncio
    async def test_delete_test(self, test_service: TestService, mock_repository: AsyncMock):
        """Test deleting a test."""
        # Setup
        test_id = 1
        user_id = 1
        mock_repository.soft_delete.return_value = True
        
        # Execute
        result = await test_service.delete_test(test_id, user_id)
        
        # Verify
        mock_repository.soft_delete.assert_called_once_with(1, 1)
        assert result is True
    
    @pytest.mark.asyncio
    async def test_delete_test_not_found(self, test_service: TestService, mock_repository: AsyncMock):
        """Test deleting a test that doesn't exist."""
        # Setup
        test_id = 999
        user_id = 1
        mock_repository.soft_delete.return_value = False
        
        # Execute
        result = await test_service.delete_test(test_id, user_id)
        
        # Verify
        mock_repository.soft_delete.assert_called_once_with(999, 1)
        assert result is False
    
    @pytest.mark.asyncio
    async def test_user_owns_test(self, test_service: TestService, mock_repository: AsyncMock):
        """Test checking if user owns a test."""
        # Setup
        test_id = 1
        user_id = 1
        mock_repository.exists.return_value = True
        
        # Execute
        result = await test_service.user_owns_test(test_id, user_id)
        
        # Verify
        mock_repository.exists.assert_called_once_with(1, 1)
        assert result is True
    
    @pytest.mark.asyncio
    async def test_user_does_not_own_test(self, test_service: TestService, mock_repository: AsyncMock):
        """Test checking if user doesn't own a test."""
        # Setup
        test_id = 1
        user_id = 1
        mock_repository.exists.return_value = False
        
        # Execute
        result = await test_service.user_owns_test(test_id, user_id)
        
        # Verify
        mock_repository.exists.assert_called_once_with(1, 1)
        assert result is False