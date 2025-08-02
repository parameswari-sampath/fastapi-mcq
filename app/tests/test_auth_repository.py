"""
Unit tests for UserRepository.
"""
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.exc import IntegrityError
from app.core.database import Base
from app.auth.models import User
from app.auth.repository import UserRepository


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
async def user_repo(db_session: AsyncSession):
    """Create UserRepository instance."""
    return UserRepository(db_session)


class TestUserRepository:
    """Test cases for UserRepository."""
    
    @pytest.mark.asyncio
    async def test_create_user(self, user_repo: UserRepository):
        """Test creating a new user."""
        user = await user_repo.create_user(
            email="test@example.com",
            password_hash="hashed_password"
        )
        
        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.password_hash == "hashed_password"
        assert user.is_deleted is False
    
    @pytest.mark.asyncio
    async def test_create_user_duplicate_email(self, user_repo: UserRepository):
        """Test creating user with duplicate email raises IntegrityError."""
        # Create first user
        await user_repo.create_user(
            email="test@example.com",
            password_hash="hashed_password1"
        )
        
        # Try to create second user with same email
        with pytest.raises(IntegrityError):
            await user_repo.create_user(
                email="test@example.com",
                password_hash="hashed_password2"
            )
    
    @pytest.mark.asyncio
    async def test_get_user_by_email(self, user_repo: UserRepository):
        """Test retrieving user by email."""
        # Create user
        created_user = await user_repo.create_user(
            email="test@example.com",
            password_hash="hashed_password"
        )
        
        # Retrieve user by email
        retrieved_user = await user_repo.get_user_by_email("test@example.com")
        
        assert retrieved_user is not None
        assert retrieved_user.id == created_user.id
        assert retrieved_user.email == "test@example.com"
        assert retrieved_user.password_hash == "hashed_password"
    
    @pytest.mark.asyncio
    async def test_get_user_by_email_not_found(self, user_repo: UserRepository):
        """Test retrieving non-existent user by email."""
        user = await user_repo.get_user_by_email("nonexistent@example.com")
        assert user is None
    
    @pytest.mark.asyncio
    async def test_get_user_by_email_soft_deleted(self, user_repo: UserRepository, db_session: AsyncSession):
        """Test that soft deleted users are not returned."""
        # Create and soft delete user
        user = User(
            email="test@example.com",
            password_hash="hashed_password",
            is_deleted=True
        )
        db_session.add(user)
        await db_session.commit()
        
        # Try to retrieve soft deleted user
        retrieved_user = await user_repo.get_user_by_email("test@example.com")
        assert retrieved_user is None
    
    @pytest.mark.asyncio
    async def test_get_user_by_id(self, user_repo: UserRepository):
        """Test retrieving user by ID."""
        # Create user
        created_user = await user_repo.create_user(
            email="test@example.com",
            password_hash="hashed_password"
        )
        
        # Retrieve user by ID
        retrieved_user = await user_repo.get_user_by_id(created_user.id)
        
        assert retrieved_user is not None
        assert retrieved_user.id == created_user.id
        assert retrieved_user.email == "test@example.com"
    
    @pytest.mark.asyncio
    async def test_get_user_by_id_not_found(self, user_repo: UserRepository):
        """Test retrieving non-existent user by ID."""
        user = await user_repo.get_user_by_id(999)
        assert user is None
    
    @pytest.mark.asyncio
    async def test_get_user_by_id_soft_deleted(self, user_repo: UserRepository, db_session: AsyncSession):
        """Test that soft deleted users are not returned by ID."""
        # Create and soft delete user
        user = User(
            email="test@example.com",
            password_hash="hashed_password",
            is_deleted=True
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        
        # Try to retrieve soft deleted user
        retrieved_user = await user_repo.get_user_by_id(user.id)
        assert retrieved_user is None
    
    @pytest.mark.asyncio
    async def test_email_exists(self, user_repo: UserRepository):
        """Test checking if email exists."""
        # Email should not exist initially
        assert await user_repo.email_exists("test@example.com") is False
        
        # Create user
        await user_repo.create_user(
            email="test@example.com",
            password_hash="hashed_password"
        )
        
        # Email should now exist
        assert await user_repo.email_exists("test@example.com") is True
    
    @pytest.mark.asyncio
    async def test_email_exists_soft_deleted(self, user_repo: UserRepository, db_session: AsyncSession):
        """Test that email_exists returns True even for soft deleted users."""
        # Create and soft delete user
        user = User(
            email="test@example.com",
            password_hash="hashed_password",
            is_deleted=True
        )
        db_session.add(user)
        await db_session.commit()
        
        # Email should still exist (including soft deleted)
        assert await user_repo.email_exists("test@example.com") is True
    
    @pytest.mark.asyncio
    async def test_soft_delete_user(self, user_repo: UserRepository):
        """Test soft deleting a user."""
        # Create user
        user = await user_repo.create_user(
            email="test@example.com",
            password_hash="hashed_password"
        )
        
        # Soft delete user
        result = await user_repo.soft_delete_user(user.id)
        assert result is True
        
        # User should not be retrievable anymore
        retrieved_user = await user_repo.get_user_by_id(user.id)
        assert retrieved_user is None
    
    @pytest.mark.asyncio
    async def test_soft_delete_user_not_found(self, user_repo: UserRepository):
        """Test soft deleting non-existent user."""
        result = await user_repo.soft_delete_user(999)
        assert result is False
    
    @pytest.mark.asyncio
    async def test_update_user_password(self, user_repo: UserRepository):
        """Test updating user password."""
        # Create user
        user = await user_repo.create_user(
            email="test@example.com",
            password_hash="old_password_hash"
        )
        
        # Update password
        result = await user_repo.update_user_password(user.id, "new_password_hash")
        assert result is True
        
        # Verify password was updated
        updated_user = await user_repo.get_user_by_id(user.id)
        assert updated_user.password_hash == "new_password_hash"
    
    @pytest.mark.asyncio
    async def test_update_user_password_not_found(self, user_repo: UserRepository):
        """Test updating password for non-existent user."""
        result = await user_repo.update_user_password(999, "new_password_hash")
        assert result is False