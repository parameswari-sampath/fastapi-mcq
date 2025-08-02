"""
Unit tests for MCQ repository.
"""
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.core.database import Base
from app.auth.models import User
from app.test_management.models import Test
from app.mcq.models import MCQ
from app.mcq.repository import MCQRepository


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
async def test_user_and_test(db_session: AsyncSession):
    """Create a test user and test."""
    # Create user
    user = User(
        email="test@example.com",
        password_hash="hashed_password"
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    # Create test
    test = Test(
        title="Sample Test",
        description="A test for MCQ questions",
        user_id=user.id
    )
    db_session.add(test)
    await db_session.commit()
    await db_session.refresh(test)
    
    return user, test


@pytest_asyncio.fixture
async def mcq_repository(db_session: AsyncSession):
    """Create an MCQ repository."""
    return MCQRepository(db_session)


class TestMCQRepository:
    """Test cases for MCQRepository."""
    
    @pytest.mark.asyncio
    async def test_create_mcq(self, mcq_repository: MCQRepository, test_user_and_test):
        """Test creating a new MCQ question."""
        user, test = test_user_and_test
        
        mcq = await mcq_repository.create(
            title="What is the capital of France?",
            description="A geography question",
            option_1="London",
            option_2="Berlin",
            option_3="Paris",
            option_4="Madrid",
            correct_answer=3,
            test_id=test.id
        )
        
        assert mcq.id is not None
        assert mcq.title == "What is the capital of France?"
        assert mcq.description == "A geography question"
        assert mcq.option_1 == "London"
        assert mcq.option_2 == "Berlin"
        assert mcq.option_3 == "Paris"
        assert mcq.option_4 == "Madrid"
        assert mcq.correct_answer == 3
        assert mcq.test_id == test.id
        assert mcq.is_deleted is False
    
    @pytest.mark.asyncio
    async def test_create_mcq_without_description(self, mcq_repository: MCQRepository, test_user_and_test):
        """Test creating an MCQ without description."""
        user, test = test_user_and_test
        
        mcq = await mcq_repository.create(
            title="What is 2+2?",
            description=None,
            option_1="3",
            option_2="4",
            option_3="5",
            option_4="6",
            correct_answer=2,
            test_id=test.id
        )
        
        assert mcq.id is not None
        assert mcq.title == "What is 2+2?"
        assert mcq.description is None
        assert mcq.option_1 == "3"
        assert mcq.option_2 == "4"
        assert mcq.option_3 == "5"
        assert mcq.option_4 == "6"
        assert mcq.correct_answer == 2
        assert mcq.test_id == test.id
        assert mcq.is_deleted is False
    
    @pytest.mark.asyncio
    async def test_get_by_id(self, mcq_repository: MCQRepository, test_user_and_test):
        """Test getting an MCQ by ID."""
        user, test = test_user_and_test
        
        # Create an MCQ
        created_mcq = await mcq_repository.create(
            title="What is the capital of France?",
            description="A geography question",
            option_1="London",
            option_2="Berlin",
            option_3="Paris",
            option_4="Madrid",
            correct_answer=3,
            test_id=test.id
        )
        
        # Get the MCQ
        retrieved_mcq = await mcq_repository.get_by_id(created_mcq.id)
        
        assert retrieved_mcq is not None
        assert retrieved_mcq.id == created_mcq.id
        assert retrieved_mcq.title == "What is the capital of France?"
        assert retrieved_mcq.description == "A geography question"
        assert retrieved_mcq.option_1 == "London"
        assert retrieved_mcq.option_2 == "Berlin"
        assert retrieved_mcq.option_3 == "Paris"
        assert retrieved_mcq.option_4 == "Madrid"
        assert retrieved_mcq.correct_answer == 3
        assert retrieved_mcq.test_id == test.id
    
    @pytest.mark.asyncio
    async def test_get_by_id_nonexistent(self, mcq_repository: MCQRepository):
        """Test getting a non-existent MCQ by ID."""
        retrieved_mcq = await mcq_repository.get_by_id(999999)
        assert retrieved_mcq is None
    
    @pytest.mark.asyncio
    async def test_get_by_id_soft_deleted(self, mcq_repository: MCQRepository, test_user_and_test):
        """Test that soft deleted MCQs are not returned by get_by_id."""
        user, test = test_user_and_test
        
        # Create an MCQ
        created_mcq = await mcq_repository.create(
            title="Question",
            description=None,
            option_1="A",
            option_2="B",
            option_3="C",
            option_4="D",
            correct_answer=1,
            test_id=test.id
        )
        
        # Soft delete the MCQ
        await mcq_repository.soft_delete(created_mcq.id)
        
        # Try to get the MCQ
        retrieved_mcq = await mcq_repository.get_by_id(created_mcq.id)
        assert retrieved_mcq is None
    
    @pytest.mark.asyncio
    async def test_get_all_by_test(self, mcq_repository: MCQRepository, test_user_and_test):
        """Test getting all MCQs for a test."""
        user, test = test_user_and_test
        
        # Create multiple MCQs
        mcq1 = await mcq_repository.create(
            title="Question 1",
            description=None,
            option_1="A1", option_2="B1", option_3="C1", option_4="D1",
            correct_answer=1, test_id=test.id
        )
        mcq2 = await mcq_repository.create(
            title="Question 2",
            description=None,
            option_1="A2", option_2="B2", option_3="C2", option_4="D2",
            correct_answer=2, test_id=test.id
        )
        mcq3 = await mcq_repository.create(
            title="Question 3",
            description=None,
            option_1="A3", option_2="B3", option_3="C3", option_4="D3",
            correct_answer=3, test_id=test.id
        )
        
        # Get all MCQs for the test
        mcqs = await mcq_repository.get_all_by_test(test.id)
        
        assert len(mcqs) == 3
        mcq_titles = [mcq.title for mcq in mcqs]
        assert "Question 1" in mcq_titles
        assert "Question 2" in mcq_titles
        assert "Question 3" in mcq_titles
        
        # Verify they are ordered by created_at (ascending)
        assert mcqs[0].title == "Question 1"
        assert mcqs[1].title == "Question 2"
        assert mcqs[2].title == "Question 3"
    
    @pytest.mark.asyncio
    async def test_get_all_by_test_excludes_soft_deleted(self, mcq_repository: MCQRepository, test_user_and_test):
        """Test that get_all_by_test excludes soft deleted MCQs."""
        user, test = test_user_and_test
        
        # Create multiple MCQs
        mcq1 = await mcq_repository.create(
            title="Question 1",
            description=None,
            option_1="A1", option_2="B1", option_3="C1", option_4="D1",
            correct_answer=1, test_id=test.id
        )
        mcq2 = await mcq_repository.create(
            title="Question 2",
            description=None,
            option_1="A2", option_2="B2", option_3="C2", option_4="D2",
            correct_answer=2, test_id=test.id
        )
        
        # Soft delete one MCQ
        await mcq_repository.soft_delete(mcq1.id)
        
        # Get all MCQs for the test
        mcqs = await mcq_repository.get_all_by_test(test.id)
        
        assert len(mcqs) == 1
        assert mcqs[0].title == "Question 2"
    
    @pytest.mark.asyncio
    async def test_get_all_by_test_empty(self, mcq_repository: MCQRepository, test_user_and_test):
        """Test getting MCQs for a test with no questions."""
        user, test = test_user_and_test
        
        mcqs = await mcq_repository.get_all_by_test(test.id)
        assert len(mcqs) == 0
    
    @pytest.mark.asyncio
    async def test_update_mcq_all_fields(self, mcq_repository: MCQRepository, test_user_and_test):
        """Test updating all fields of an MCQ."""
        user, test = test_user_and_test
        
        # Create an MCQ
        created_mcq = await mcq_repository.create(
            title="Original Question",
            description="Original description",
            option_1="A", option_2="B", option_3="C", option_4="D",
            correct_answer=1, test_id=test.id
        )
        
        # Update the MCQ
        updated_mcq = await mcq_repository.update(
            mcq_id=created_mcq.id,
            title="Updated Question",
            description="Updated description",
            option_1="Updated A",
            option_2="Updated B",
            option_3="Updated C",
            option_4="Updated D",
            correct_answer=2
        )
        
        assert updated_mcq is not None
        assert updated_mcq.id == created_mcq.id
        assert updated_mcq.title == "Updated Question"
        assert updated_mcq.description == "Updated description"
        assert updated_mcq.option_1 == "Updated A"
        assert updated_mcq.option_2 == "Updated B"
        assert updated_mcq.option_3 == "Updated C"
        assert updated_mcq.option_4 == "Updated D"
        assert updated_mcq.correct_answer == 2
        assert updated_mcq.test_id == test.id
    
    @pytest.mark.asyncio
    async def test_update_mcq_partial_fields(self, mcq_repository: MCQRepository, test_user_and_test):
        """Test updating only some fields of an MCQ."""
        user, test = test_user_and_test
        
        # Create an MCQ
        created_mcq = await mcq_repository.create(
            title="Original Question",
            description="Original description",
            option_1="A", option_2="B", option_3="C", option_4="D",
            correct_answer=1, test_id=test.id
        )
        
        # Update only title and correct_answer
        updated_mcq = await mcq_repository.update(
            mcq_id=created_mcq.id,
            title="Updated Question",
            correct_answer=3
        )
        
        assert updated_mcq is not None
        assert updated_mcq.id == created_mcq.id
        assert updated_mcq.title == "Updated Question"
        assert updated_mcq.description == "Original description"  # Unchanged
        assert updated_mcq.option_1 == "A"  # Unchanged
        assert updated_mcq.option_2 == "B"  # Unchanged
        assert updated_mcq.option_3 == "C"  # Unchanged
        assert updated_mcq.option_4 == "D"  # Unchanged
        assert updated_mcq.correct_answer == 3
    
    @pytest.mark.asyncio
    async def test_update_mcq_no_changes(self, mcq_repository: MCQRepository, test_user_and_test):
        """Test updating an MCQ with no changes."""
        user, test = test_user_and_test
        
        # Create an MCQ
        created_mcq = await mcq_repository.create(
            title="Question",
            description="Description",
            option_1="A", option_2="B", option_3="C", option_4="D",
            correct_answer=1, test_id=test.id
        )
        
        # Update with no changes
        updated_mcq = await mcq_repository.update(mcq_id=created_mcq.id)
        
        assert updated_mcq is not None
        assert updated_mcq.id == created_mcq.id
        assert updated_mcq.title == "Question"
        assert updated_mcq.description == "Description"
        assert updated_mcq.correct_answer == 1
    
    @pytest.mark.asyncio
    async def test_update_mcq_nonexistent(self, mcq_repository: MCQRepository):
        """Test updating a non-existent MCQ."""
        updated_mcq = await mcq_repository.update(
            mcq_id=999999,
            title="Updated Question"
        )
        assert updated_mcq is None
    
    @pytest.mark.asyncio
    async def test_update_mcq_soft_deleted(self, mcq_repository: MCQRepository, test_user_and_test):
        """Test updating a soft deleted MCQ."""
        user, test = test_user_and_test
        
        # Create an MCQ
        created_mcq = await mcq_repository.create(
            title="Question",
            description=None,
            option_1="A", option_2="B", option_3="C", option_4="D",
            correct_answer=1, test_id=test.id
        )
        
        # Soft delete the MCQ
        await mcq_repository.soft_delete(created_mcq.id)
        
        # Try to update the soft deleted MCQ
        updated_mcq = await mcq_repository.update(
            mcq_id=created_mcq.id,
            title="Updated Question"
        )
        assert updated_mcq is None
    
    @pytest.mark.asyncio
    async def test_soft_delete_mcq(self, mcq_repository: MCQRepository, test_user_and_test):
        """Test soft deleting an MCQ."""
        user, test = test_user_and_test
        
        # Create an MCQ
        created_mcq = await mcq_repository.create(
            title="Question",
            description=None,
            option_1="A", option_2="B", option_3="C", option_4="D",
            correct_answer=1, test_id=test.id
        )
        
        # Soft delete the MCQ
        result = await mcq_repository.soft_delete(created_mcq.id)
        assert result is True
        
        # Verify the MCQ is soft deleted
        retrieved_mcq = await mcq_repository.get_by_id(created_mcq.id)
        assert retrieved_mcq is None
    
    @pytest.mark.asyncio
    async def test_soft_delete_mcq_nonexistent(self, mcq_repository: MCQRepository):
        """Test soft deleting a non-existent MCQ."""
        result = await mcq_repository.soft_delete(999999)
        assert result is False
    
    @pytest.mark.asyncio
    async def test_soft_delete_mcq_already_deleted(self, mcq_repository: MCQRepository, test_user_and_test):
        """Test soft deleting an already soft deleted MCQ."""
        user, test = test_user_and_test
        
        # Create an MCQ
        created_mcq = await mcq_repository.create(
            title="Question",
            description=None,
            option_1="A", option_2="B", option_3="C", option_4="D",
            correct_answer=1, test_id=test.id
        )
        
        # Soft delete the MCQ
        result1 = await mcq_repository.soft_delete(created_mcq.id)
        assert result1 is True
        
        # Try to soft delete again
        result2 = await mcq_repository.soft_delete(created_mcq.id)
        assert result2 is False
    
    @pytest.mark.asyncio
    async def test_count_by_test(self, mcq_repository: MCQRepository, test_user_and_test):
        """Test counting MCQs for a test."""
        user, test = test_user_and_test
        
        # Initially no MCQs
        count = await mcq_repository.count_by_test(test.id)
        assert count == 0
        
        # Create some MCQs
        await mcq_repository.create(
            title="Q1", description=None,
            option_1="A", option_2="B", option_3="C", option_4="D",
            correct_answer=1, test_id=test.id
        )
        await mcq_repository.create(
            title="Q2", description=None,
            option_1="A", option_2="B", option_3="C", option_4="D",
            correct_answer=2, test_id=test.id
        )
        
        count = await mcq_repository.count_by_test(test.id)
        assert count == 2
    
    @pytest.mark.asyncio
    async def test_count_by_test_excludes_soft_deleted(self, mcq_repository: MCQRepository, test_user_and_test):
        """Test that count_by_test excludes soft deleted MCQs."""
        user, test = test_user_and_test
        
        # Create MCQs
        mcq1 = await mcq_repository.create(
            title="Q1", description=None,
            option_1="A", option_2="B", option_3="C", option_4="D",
            correct_answer=1, test_id=test.id
        )
        mcq2 = await mcq_repository.create(
            title="Q2", description=None,
            option_1="A", option_2="B", option_3="C", option_4="D",
            correct_answer=2, test_id=test.id
        )
        
        # Soft delete one
        await mcq_repository.soft_delete(mcq1.id)
        
        count = await mcq_repository.count_by_test(test.id)
        assert count == 1
    
    @pytest.mark.asyncio
    async def test_exists(self, mcq_repository: MCQRepository, test_user_and_test):
        """Test checking if an MCQ exists."""
        user, test = test_user_and_test
        
        # Non-existent MCQ
        exists = await mcq_repository.exists(999999)
        assert exists is False
        
        # Create an MCQ
        created_mcq = await mcq_repository.create(
            title="Question",
            description=None,
            option_1="A", option_2="B", option_3="C", option_4="D",
            correct_answer=1, test_id=test.id
        )
        
        # MCQ exists
        exists = await mcq_repository.exists(created_mcq.id)
        assert exists is True
        
        # Soft delete the MCQ
        await mcq_repository.soft_delete(created_mcq.id)
        
        # MCQ no longer exists
        exists = await mcq_repository.exists(created_mcq.id)
        assert exists is False
    
    @pytest.mark.asyncio
    async def test_get_by_id_and_test(self, mcq_repository: MCQRepository, test_user_and_test, db_session: AsyncSession):
        """Test getting an MCQ by ID and test ID."""
        user, test = test_user_and_test
        
        # Create another test
        test2 = Test(
            title="Another Test",
            description=None,
            user_id=user.id
        )
        db_session.add(test2)
        await db_session.commit()
        await db_session.refresh(test2)
        
        # Create MCQs in different tests
        mcq1 = await mcq_repository.create(
            title="Question 1",
            description=None,
            option_1="A", option_2="B", option_3="C", option_4="D",
            correct_answer=1, test_id=test.id
        )
        mcq2 = await mcq_repository.create(
            title="Question 2",
            description=None,
            option_1="A", option_2="B", option_3="C", option_4="D",
            correct_answer=2, test_id=test2.id
        )
        
        # Get MCQ1 from test1
        retrieved_mcq = await mcq_repository.get_by_id_and_test(mcq1.id, test.id)
        assert retrieved_mcq is not None
        assert retrieved_mcq.id == mcq1.id
        assert retrieved_mcq.test_id == test.id
        
        # Try to get MCQ1 from test2 (should fail)
        retrieved_mcq = await mcq_repository.get_by_id_and_test(mcq1.id, test2.id)
        assert retrieved_mcq is None
        
        # Get MCQ2 from test2
        retrieved_mcq = await mcq_repository.get_by_id_and_test(mcq2.id, test2.id)
        assert retrieved_mcq is not None
        assert retrieved_mcq.id == mcq2.id
        assert retrieved_mcq.test_id == test2.id
    
    @pytest.mark.asyncio
    async def test_soft_delete_all_by_test(self, mcq_repository: MCQRepository, test_user_and_test, db_session: AsyncSession):
        """Test soft deleting all MCQs for a test."""
        user, test = test_user_and_test
        
        # Create another test
        test2 = Test(
            title="Another Test",
            description=None,
            user_id=user.id
        )
        db_session.add(test2)
        await db_session.commit()
        await db_session.refresh(test2)
        
        # Create MCQs in both tests
        mcq1 = await mcq_repository.create(
            title="Q1", description=None,
            option_1="A", option_2="B", option_3="C", option_4="D",
            correct_answer=1, test_id=test.id
        )
        mcq2 = await mcq_repository.create(
            title="Q2", description=None,
            option_1="A", option_2="B", option_3="C", option_4="D",
            correct_answer=2, test_id=test.id
        )
        mcq3 = await mcq_repository.create(
            title="Q3", description=None,
            option_1="A", option_2="B", option_3="C", option_4="D",
            correct_answer=3, test_id=test2.id
        )
        
        # Soft delete all MCQs for test1
        deleted_count = await mcq_repository.soft_delete_all_by_test(test.id)
        assert deleted_count == 2
        
        # Verify test1 MCQs are deleted
        test1_mcqs = await mcq_repository.get_all_by_test(test.id)
        assert len(test1_mcqs) == 0
        
        # Verify test2 MCQs are not affected
        test2_mcqs = await mcq_repository.get_all_by_test(test2.id)
        assert len(test2_mcqs) == 1
        assert test2_mcqs[0].id == mcq3.id
    
    @pytest.mark.asyncio
    async def test_soft_delete_all_by_test_empty(self, mcq_repository: MCQRepository, test_user_and_test):
        """Test soft deleting all MCQs for a test with no questions."""
        user, test = test_user_and_test
        
        deleted_count = await mcq_repository.soft_delete_all_by_test(test.id)
        assert deleted_count == 0