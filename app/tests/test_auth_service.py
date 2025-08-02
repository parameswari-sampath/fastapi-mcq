"""
Unit tests for AuthService.
"""
import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.exc import IntegrityError
from app.core.database import Base
from app.auth.models import User
from app.auth.service import AuthService
from app.auth.schemas import UserRegisterRequest, UserLoginRequest


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
async def auth_service(db_session: AsyncSession):
    """Create AuthService instance."""
    return AuthService(db_session)


class TestAuthService:
    """Test cases for AuthService."""
    
    @pytest.mark.asyncio
    @patch('app.auth.service.get_password_hash')
    @patch('app.auth.service.create_access_token')
    async def test_register_user_success(
        self, 
        mock_create_token, 
        mock_hash_password, 
        auth_service: AuthService
    ):
        """Test successful user registration."""
        # Mock dependencies
        mock_hash_password.return_value = "hashed_password"
        mock_create_token.return_value = "access_token"
        
        request = UserRegisterRequest(
            email="test@example.com",
            password="password123"
        )
        
        response = await auth_service.register_user(request)
        
        assert response.access_token == "access_token"
        assert response.token_type == "bearer"
        assert response.email == "test@example.com"
        assert response.user_id is not None
        
        # Verify mocks were called
        mock_hash_password.assert_called_once_with("password123")
        mock_create_token.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_register_user_duplicate_email(self, auth_service: AuthService):
        """Test registration with duplicate email."""
        # Create first user
        request1 = UserRegisterRequest(
            email="test@example.com",
            password="password123"
        )
        
        with patch('app.auth.service.get_password_hash', return_value="hashed_password"):
            with patch('app.auth.service.create_access_token', return_value="token"):
                await auth_service.register_user(request1)
        
        # Try to register with same email
        request2 = UserRegisterRequest(
            email="test@example.com",
            password="password456"
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await auth_service.register_user(request2)
        
        assert exc_info.value.status_code == 400
        assert "Email already registered" in exc_info.value.detail
    
    @pytest.mark.asyncio
    @patch('app.auth.service.get_password_hash')
    async def test_register_user_integrity_error(
        self, 
        mock_hash_password, 
        auth_service: AuthService
    ):
        """Test registration handling IntegrityError."""
        mock_hash_password.return_value = "hashed_password"
        
        # Mock repository to raise IntegrityError
        with patch.object(auth_service.user_repo, 'create_user', side_effect=IntegrityError("", "", "")):
            request = UserRegisterRequest(
                email="test@example.com",
                password="password123"
            )
            
            with pytest.raises(HTTPException) as exc_info:
                await auth_service.register_user(request)
            
            assert exc_info.value.status_code == 400
            assert "Email already registered" in exc_info.value.detail
    
    @pytest.mark.asyncio
    @patch('app.auth.service.verify_password')
    @patch('app.auth.service.create_access_token')
    async def test_login_user_success(
        self, 
        mock_create_token, 
        mock_verify_password, 
        auth_service: AuthService,
        db_session: AsyncSession
    ):
        """Test successful user login."""
        # Create user in database
        user = User(
            email="test@example.com",
            password_hash="hashed_password"
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        
        # Mock dependencies
        mock_verify_password.return_value = True
        mock_create_token.return_value = "access_token"
        
        request = UserLoginRequest(
            email="test@example.com",
            password="password123"
        )
        
        response = await auth_service.login_user(request)
        
        assert response.access_token == "access_token"
        assert response.token_type == "bearer"
        assert response.email == "test@example.com"
        assert response.user_id == user.id
        
        # Verify mocks were called
        mock_verify_password.assert_called_once_with("password123", "hashed_password")
        mock_create_token.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_login_user_not_found(self, auth_service: AuthService):
        """Test login with non-existent email."""
        request = UserLoginRequest(
            email="nonexistent@example.com",
            password="password123"
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await auth_service.login_user(request)
        
        assert exc_info.value.status_code == 401
        assert "Invalid email or password" in exc_info.value.detail
    
    @pytest.mark.asyncio
    @patch('app.auth.service.verify_password')
    async def test_login_user_wrong_password(
        self, 
        mock_verify_password, 
        auth_service: AuthService,
        db_session: AsyncSession
    ):
        """Test login with wrong password."""
        # Create user in database
        user = User(
            email="test@example.com",
            password_hash="hashed_password"
        )
        db_session.add(user)
        await db_session.commit()
        
        # Mock password verification to fail
        mock_verify_password.return_value = False
        
        request = UserLoginRequest(
            email="test@example.com",
            password="wrong_password"
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await auth_service.login_user(request)
        
        assert exc_info.value.status_code == 401
        assert "Invalid email or password" in exc_info.value.detail
    
    @pytest.mark.asyncio
    async def test_get_user_by_id_success(
        self, 
        auth_service: AuthService,
        db_session: AsyncSession
    ):
        """Test getting user by ID."""
        # Create user in database
        user = User(
            email="test@example.com",
            password_hash="hashed_password"
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        
        response = await auth_service.get_user_by_id(user.id)
        
        assert response is not None
        assert response.id == user.id
        assert response.email == "test@example.com"
        assert response.created_at == user.created_at
        assert response.updated_at == user.updated_at
    
    @pytest.mark.asyncio
    async def test_get_user_by_id_not_found(self, auth_service: AuthService):
        """Test getting non-existent user by ID."""
        response = await auth_service.get_user_by_id(999)
        assert response is None
    
    @pytest.mark.asyncio
    @patch('app.auth.service.verify_password')
    @patch('app.auth.service.get_password_hash')
    async def test_change_password_success(
        self, 
        mock_hash_password, 
        mock_verify_password, 
        auth_service: AuthService,
        db_session: AsyncSession
    ):
        """Test successful password change."""
        # Create user in database
        user = User(
            email="test@example.com",
            password_hash="old_hashed_password"
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        
        # Mock dependencies
        mock_verify_password.return_value = True
        mock_hash_password.return_value = "new_hashed_password"
        
        result = await auth_service.change_password(
            user.id, 
            "old_password", 
            "new_password"
        )
        
        assert result is True
        mock_verify_password.assert_called_once_with("old_password", "old_hashed_password")
        mock_hash_password.assert_called_once_with("new_password")
    
    @pytest.mark.asyncio
    async def test_change_password_user_not_found(self, auth_service: AuthService):
        """Test password change for non-existent user."""
        with pytest.raises(HTTPException) as exc_info:
            await auth_service.change_password(999, "old_password", "new_password")
        
        assert exc_info.value.status_code == 404
        assert "User not found" in exc_info.value.detail
    
    @pytest.mark.asyncio
    @patch('app.auth.service.verify_password')
    async def test_change_password_wrong_current_password(
        self, 
        mock_verify_password, 
        auth_service: AuthService,
        db_session: AsyncSession
    ):
        """Test password change with wrong current password."""
        # Create user in database
        user = User(
            email="test@example.com",
            password_hash="hashed_password"
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        
        # Mock password verification to fail
        mock_verify_password.return_value = False
        
        with pytest.raises(HTTPException) as exc_info:
            await auth_service.change_password(
                user.id, 
                "wrong_password", 
                "new_password"
            )
        
        assert exc_info.value.status_code == 400
        assert "Current password is incorrect" in exc_info.value.detail
    
    @pytest.mark.asyncio
    async def test_delete_user_success(
        self, 
        auth_service: AuthService,
        db_session: AsyncSession
    ):
        """Test successful user deletion."""
        # Create user in database
        user = User(
            email="test@example.com",
            password_hash="hashed_password"
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        
        result = await auth_service.delete_user(user.id)
        assert result is True
    
    @pytest.mark.asyncio
    async def test_delete_user_not_found(self, auth_service: AuthService):
        """Test deleting non-existent user."""
        result = await auth_service.delete_user(999)
        assert result is False