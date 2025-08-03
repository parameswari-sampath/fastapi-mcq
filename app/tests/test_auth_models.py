"""
Unit tests for User model.
"""
import pytest
import pytest_asyncio
from datetime import datetime
from enum import Enum
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.exc import IntegrityError
from app.core.database import Base
from app.auth.models import User, UserRole
# Import models to ensure they're registered with SQLAlchemy
try:
    from app.test_management.models import Test
    from app.mcq.models import MCQ
except ImportError:
    # Models might not exist in some test scenarios
    pass


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


class TestUserModel:
    """Test cases for User model."""
    
    @pytest.mark.asyncio
    async def test_create_user(self, db_session: AsyncSession):
        """Test creating a new user."""
        user = User(
            email="test@example.com",
            password_hash="hashed_password"
        )
        
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        
        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.password_hash == "hashed_password"
        assert user.role == UserRole.TEACHER  # Default role
        assert user.is_deleted is False
        assert isinstance(user.created_at, datetime)
        assert isinstance(user.updated_at, datetime)
    
    @pytest.mark.asyncio
    async def test_user_email_unique_constraint(self, db_session: AsyncSession):
        """Test that email must be unique."""
        # Create first user
        user1 = User(
            email="test@example.com",
            password_hash="hashed_password1"
        )
        db_session.add(user1)
        await db_session.commit()
        
        # Try to create second user with same email
        user2 = User(
            email="test@example.com",
            password_hash="hashed_password2"
        )
        db_session.add(user2)
        
        with pytest.raises(IntegrityError):
            await db_session.commit()
    
    @pytest.mark.asyncio
    async def test_user_soft_delete_default(self, db_session: AsyncSession):
        """Test that is_deleted defaults to False."""
        user = User(
            email="test@example.com",
            password_hash="hashed_password"
        )
        
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        
        assert user.is_deleted is False
    
    @pytest.mark.asyncio
    async def test_user_soft_delete_flag(self, db_session: AsyncSession):
        """Test setting soft delete flag."""
        user = User(
            email="test@example.com",
            password_hash="hashed_password"
        )
        
        db_session.add(user)
        await db_session.commit()
        
        # Soft delete the user
        user.is_deleted = True
        await db_session.commit()
        await db_session.refresh(user)
        
        assert user.is_deleted is True
    
    @pytest.mark.asyncio
    async def test_user_timestamps(self, db_session: AsyncSession):
        """Test that timestamps are automatically set."""
        user = User(
            email="test@example.com",
            password_hash="hashed_password"
        )
        
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        
        assert user.created_at is not None
        assert user.updated_at is not None
        assert isinstance(user.created_at, datetime)
        assert isinstance(user.updated_at, datetime)
    
    def test_user_repr(self):
        """Test User string representation."""
        user = User(
            id=1,
            email="test@example.com",
            password_hash="hashed_password",
            role=UserRole.TEACHER,
            is_deleted=False
        )
        
        repr_str = repr(user)
        assert "User(id=1" in repr_str
        assert "email='test@example.com'" in repr_str
        assert "role=UserRole.TEACHER" in repr_str
        assert "is_deleted=False" in repr_str
    
    def test_user_str(self):
        """Test User human-readable string representation."""
        user = User(
            id=1,
            email="test@example.com",
            password_hash="hashed_password",
            role=UserRole.TEACHER
        )
        
        str_repr = str(user)
        assert str_repr == "User 1: test@example.com (UserRole.TEACHER)"
    
    @pytest.mark.asyncio
    async def test_user_required_fields(self, db_session: AsyncSession):
        """Test that required fields cannot be None."""
        # Test missing email
        with pytest.raises(IntegrityError):
            user = User(password_hash="hashed_password")
            db_session.add(user)
            await db_session.commit()
        
        await db_session.rollback()
        
        # Test missing password_hash
        with pytest.raises(IntegrityError):
            user = User(email="test@example.com")
            db_session.add(user)
            await db_session.commit()
    
    @pytest.mark.asyncio
    async def test_user_role_default(self, db_session: AsyncSession):
        """Test that role defaults to TEACHER."""
        user = User(
            email="test@example.com",
            password_hash="hashed_password"
        )
        
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        
        assert user.role == UserRole.TEACHER
    
    @pytest.mark.asyncio
    async def test_user_role_student(self, db_session: AsyncSession):
        """Test creating user with STUDENT role."""
        user = User(
            email="student@example.com",
            password_hash="hashed_password",
            role=UserRole.STUDENT
        )
        
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        
        assert user.role == UserRole.STUDENT
    
    @pytest.mark.asyncio
    async def test_user_role_teacher(self, db_session: AsyncSession):
        """Test creating user with TEACHER role."""
        user = User(
            email="teacher@example.com",
            password_hash="hashed_password",
            role=UserRole.TEACHER
        )
        
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        
        assert user.role == UserRole.TEACHER
    
    def test_user_role_enum_values(self):
        """Test UserRole enum values."""
        assert UserRole.STUDENT == "STUDENT"
        assert UserRole.TEACHER == "TEACHER"
        assert len(UserRole) == 2
    
    def test_user_role_enum_inheritance(self):
        """Test that UserRole inherits from str and Enum."""
        assert isinstance(UserRole.STUDENT, str)
        assert isinstance(UserRole.TEACHER, str)
        assert issubclass(UserRole, str)
        assert issubclass(UserRole, Enum)