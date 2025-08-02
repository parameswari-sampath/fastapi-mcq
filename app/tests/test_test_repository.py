"""
Unit tests for Test repository.
"""
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.core.database import Base
from app.auth.models import User
from app.test_management.models import Test
from app.test_management.repository import TestRepository


# Test database URL (in-memory SQLite for testing)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Create test engine and session
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestAsyncSession = async_sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)


@pytest_asyncio.fixture
async def db_session():
    """Create test database session."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with TestAsyncSession() as session:
        yield session
        await session.rollback()
    
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession):
    """Create a test user."""
    user = User(
        email="test@example.com",
        password_hash="hashed_password"
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_repository(db_session: AsyncSession):
    """Create a test repository."""
    return TestRepository(db_session)


class TestTestRepository:
    """Test cases for TestRepository."""
    
    @pytest.mark.asyncio
    async def test_create_test(self, test_repository: TestRepository, test_user: User):
        """Test creating a new test."""
        test = await test_repository.create(
            title="Python Quiz",
            description="A comprehensive Python quiz",
            user_id=test_user.id
        )
        
        assert test.id is not None
        assert test.title == "Python Quiz"
        assert test.description == "A comprehensive Python quiz"
        assert test.user_id == test_user.id
        assert test.is_deleted is False
    
    @pytest.mark.asyncio
    async def test_create_test_without_description(self, test_repository: TestRepository, test_user: User):
        """Test creating a test without description."""
        test = await test_repository.create(
            title="Python Quiz",
            description=None,
            user_id=test_user.id
        )
        
        assert test.id is not None
        assert test.title == "Python Quiz"
        assert test.description is None
        assert test.user_id == test_user.id
        assert test.is_deleted is False
    
    @pytest.mark.asyncio
    async def test_get_by_id(self, test_repository: TestRepository, test_user: User):
        """Test getting a test by ID."""
        # Create a test
        created_test = await test_repository.create(
            title="Python Quiz",
            description="A quiz",
            user_id=test_user.id
        )
        
        # Get the test
        retrieved_test = await test_repository.get_by_id(created_test.id, test_user.id)
        
        assert retrieved_test is not None
        assert retrieved_test.id == created_test.id
        assert retrieved_test.title == "Python Quiz"
        assert retrieved_test.description == "A quiz"
        assert retrieved_test.user_id == test_user.id
    
    @pytest.mark.asyncio
    async def test_get_by_id_wrong_user(self, test_repository: TestRepository, test_user: User, db_session: AsyncSession):
        """Test getting a test by ID with wrong user."""
        # Create another user
        other_user = User(email="other@example.com", password_hash="hashed")
        db_session.add(other_user)
        await db_session.commit()
        await db_session.refresh(other_user)
        
        # Create a test for the first user
        created_test = await test_repository.create(
            title="Python Quiz",
            description="A quiz",
            user_id=test_user.id
        )
        
        # Try to get the test with the other user's ID
        retrieved_test = await test_repository.get_by_id(created_test.id, other_user.id)
        
        assert retrieved_test is None
    
    @pytest.mark.asyncio
    async def test_get_by_id_nonexistent(self, test_repository: TestRepository, test_user: User):
        """Test getting a nonexistent test."""
        retrieved_test = await test_repository.get_by_id(999999, test_user.id)
        assert retrieved_test is None
    
    @pytest.mark.asyncio
    async def test_get_by_id_soft_deleted(self, test_repository: TestRepository, test_user: User):
        """Test that soft deleted tests are not returned."""
        # Create a test
        created_test = await test_repository.create(
            title="Python Quiz",
            description="A quiz",
            user_id=test_user.id
        )
        
        # Soft delete the test
        await test_repository.soft_delete(created_test.id, test_user.id)
        
        # Try to get the test
        retrieved_test = await test_repository.get_by_id(created_test.id, test_user.id)
        
        assert retrieved_test is None
    
    @pytest.mark.asyncio
    async def test_get_all_by_user(self, test_repository: TestRepository, test_user: User):
        """Test getting all tests for a user."""
        # Create multiple tests
        test1 = await test_repository.create("Quiz 1", "Description 1", test_user.id)
        test2 = await test_repository.create("Quiz 2", "Description 2", test_user.id)
        test3 = await test_repository.create("Quiz 3", None, test_user.id)
        
        # Get all tests
        tests = await test_repository.get_all_by_user(test_user.id)
        
        assert len(tests) == 3
        test_ids = [test.id for test in tests]
        assert test1.id in test_ids
        assert test2.id in test_ids
        assert test3.id in test_ids
    
    @pytest.mark.asyncio
    async def test_get_all_by_user_excludes_soft_deleted(self, test_repository: TestRepository, test_user: User):
        """Test that get_all_by_user excludes soft deleted tests."""
        # Create multiple tests
        test1 = await test_repository.create("Quiz 1", "Description 1", test_user.id)
        test2 = await test_repository.create("Quiz 2", "Description 2", test_user.id)
        test3 = await test_repository.create("Quiz 3", None, test_user.id)
        
        # Soft delete one test
        await test_repository.soft_delete(test2.id, test_user.id)
        
        # Get all tests
        tests = await test_repository.get_all_by_user(test_user.id)
        
        assert len(tests) == 2
        test_ids = [test.id for test in tests]
        assert test1.id in test_ids
        assert test2.id not in test_ids
        assert test3.id in test_ids
    
    @pytest.mark.asyncio
    async def test_get_all_by_user_empty(self, test_repository: TestRepository, test_user: User):
        """Test getting all tests for a user with no tests."""
        tests = await test_repository.get_all_by_user(test_user.id)
        assert len(tests) == 0
    
    @pytest.mark.asyncio
    async def test_update_test(self, test_repository: TestRepository, test_user: User):
        """Test updating a test."""
        # Create a test
        created_test = await test_repository.create(
            title="Original Title",
            description="Original Description",
            user_id=test_user.id
        )
        
        # Update the test
        updated_test = await test_repository.update(
            test_id=created_test.id,
            user_id=test_user.id,
            title="Updated Title",
            description="Updated Description"
        )
        
        assert updated_test is not None
        assert updated_test.id == created_test.id
        assert updated_test.title == "Updated Title"
        assert updated_test.description == "Updated Description"
        assert updated_test.user_id == test_user.id
    
    @pytest.mark.asyncio
    async def test_update_test_partial(self, test_repository: TestRepository, test_user: User):
        """Test partially updating a test."""
        # Create a test
        created_test = await test_repository.create(
            title="Original Title",
            description="Original Description",
            user_id=test_user.id
        )
        
        # Update only the title
        updated_test = await test_repository.update(
            test_id=created_test.id,
            user_id=test_user.id,
            title="Updated Title"
        )
        
        assert updated_test is not None
        assert updated_test.title == "Updated Title"
        assert updated_test.description == "Original Description"
    
    @pytest.mark.asyncio
    async def test_update_test_nonexistent(self, test_repository: TestRepository, test_user: User):
        """Test updating a nonexistent test."""
        updated_test = await test_repository.update(
            test_id=999999,
            user_id=test_user.id,
            title="Updated Title"
        )
        
        assert updated_test is None
    
    @pytest.mark.asyncio
    async def test_update_test_wrong_user(self, test_repository: TestRepository, test_user: User, db_session: AsyncSession):
        """Test updating a test with wrong user."""
        # Create another user
        other_user = User(email="other@example.com", password_hash="hashed")
        db_session.add(other_user)
        await db_session.commit()
        await db_session.refresh(other_user)
        
        # Create a test for the first user
        created_test = await test_repository.create(
            title="Original Title",
            description="Original Description",
            user_id=test_user.id
        )
        
        # Try to update with the other user's ID
        updated_test = await test_repository.update(
            test_id=created_test.id,
            user_id=other_user.id,
            title="Updated Title"
        )
        
        assert updated_test is None
    
    @pytest.mark.asyncio
    async def test_update_test_no_changes(self, test_repository: TestRepository, test_user: User):
        """Test updating a test with no changes."""
        # Create a test
        created_test = await test_repository.create(
            title="Original Title",
            description="Original Description",
            user_id=test_user.id
        )
        
        # Update with no changes
        updated_test = await test_repository.update(
            test_id=created_test.id,
            user_id=test_user.id
        )
        
        assert updated_test is not None
        assert updated_test.title == "Original Title"
        assert updated_test.description == "Original Description"
    
    @pytest.mark.asyncio
    async def test_soft_delete_test(self, test_repository: TestRepository, test_user: User):
        """Test soft deleting a test."""
        # Create a test
        created_test = await test_repository.create(
            title="Test to Delete",
            description="This will be deleted",
            user_id=test_user.id
        )
        
        # Soft delete the test
        result = await test_repository.soft_delete(created_test.id, test_user.id)
        
        assert result is True
        
        # Verify the test is not returned by get_by_id
        retrieved_test = await test_repository.get_by_id(created_test.id, test_user.id)
        assert retrieved_test is None
    
    @pytest.mark.asyncio
    async def test_soft_delete_nonexistent(self, test_repository: TestRepository, test_user: User):
        """Test soft deleting a nonexistent test."""
        result = await test_repository.soft_delete(999999, test_user.id)
        assert result is False
    
    @pytest.mark.asyncio
    async def test_soft_delete_wrong_user(self, test_repository: TestRepository, test_user: User, db_session: AsyncSession):
        """Test soft deleting a test with wrong user."""
        # Create another user
        other_user = User(email="other@example.com", password_hash="hashed")
        db_session.add(other_user)
        await db_session.commit()
        await db_session.refresh(other_user)
        
        # Create a test for the first user
        created_test = await test_repository.create(
            title="Test to Delete",
            description="This will be deleted",
            user_id=test_user.id
        )
        
        # Try to soft delete with the other user's ID
        result = await test_repository.soft_delete(created_test.id, other_user.id)
        
        assert result is False
        
        # Verify the test still exists for the original user
        retrieved_test = await test_repository.get_by_id(created_test.id, test_user.id)
        assert retrieved_test is not None
    
    @pytest.mark.asyncio
    async def test_count_by_user(self, test_repository: TestRepository, test_user: User):
        """Test counting tests for a user."""
        # Initially no tests
        count = await test_repository.count_by_user(test_user.id)
        assert count == 0
        
        # Create some tests
        await test_repository.create("Quiz 1", "Description 1", test_user.id)
        await test_repository.create("Quiz 2", "Description 2", test_user.id)
        
        count = await test_repository.count_by_user(test_user.id)
        assert count == 2
    
    @pytest.mark.asyncio
    async def test_count_by_user_excludes_soft_deleted(self, test_repository: TestRepository, test_user: User):
        """Test that count excludes soft deleted tests."""
        # Create some tests
        test1 = await test_repository.create("Quiz 1", "Description 1", test_user.id)
        test2 = await test_repository.create("Quiz 2", "Description 2", test_user.id)
        
        # Soft delete one test
        await test_repository.soft_delete(test1.id, test_user.id)
        
        count = await test_repository.count_by_user(test_user.id)
        assert count == 1
    
    @pytest.mark.asyncio
    async def test_exists(self, test_repository: TestRepository, test_user: User):
        """Test checking if a test exists."""
        # Create a test
        created_test = await test_repository.create(
            title="Test Existence",
            description="Testing existence",
            user_id=test_user.id
        )
        
        # Check if it exists
        exists = await test_repository.exists(created_test.id, test_user.id)
        assert exists is True
        
        # Check nonexistent test
        exists = await test_repository.exists(999999, test_user.id)
        assert exists is False
    
    @pytest.mark.asyncio
    async def test_exists_soft_deleted(self, test_repository: TestRepository, test_user: User):
        """Test that exists returns False for soft deleted tests."""
        # Create a test
        created_test = await test_repository.create(
            title="Test Existence",
            description="Testing existence",
            user_id=test_user.id
        )
        
        # Soft delete the test
        await test_repository.soft_delete(created_test.id, test_user.id)
        
        # Check if it exists
        exists = await test_repository.exists(created_test.id, test_user.id)
        assert exists is False