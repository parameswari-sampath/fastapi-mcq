"""
Integration tests for authentication endpoints.
"""
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from fastapi import FastAPI
from app.core.database import Base, get_db
from app.auth.router import router as auth_router
from app.auth.models import User


# Test database URL (in-memory SQLite for testing)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Create test engine and session
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestAsyncSession = async_sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)


async def get_test_db():
    """Override database dependency for testing."""
    async with TestAsyncSession() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@pytest_asyncio.fixture
async def app():
    """Create test FastAPI application."""
    test_app = FastAPI()
    test_app.include_router(auth_router)
    
    # Override database dependency
    test_app.dependency_overrides[get_db] = get_test_db
    
    return test_app


@pytest_asyncio.fixture
async def client(app: FastAPI):
    """Create test HTTP client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture(autouse=True)
async def setup_database():
    """Set up test database before each test."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield
    
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


class TestAuthEndpoints:
    """Integration tests for authentication endpoints."""
    
    @pytest.mark.asyncio
    @pytest.mark.asyncio
    async def test_register_success(self, client: AsyncClient):
        """Test successful user registration."""
        response = await client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "password": "password123"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["email"] == "test@example.com"
        assert "user_id" in data
        assert isinstance(data["user_id"], int)
    
    @pytest.mark.asyncio
    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, client: AsyncClient):
        """Test registration with duplicate email."""
        # Register first user
        await client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "password": "password123"
            }
        )
        
        # Try to register with same email
        response = await client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "password": "password456"
            }
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "Email already registered" in data["detail"]
    
    @pytest.mark.asyncio
    async def test_register_invalid_email(self, client: AsyncClient):
        """Test registration with invalid email format."""
        response = await client.post(
            "/auth/register",
            json={
                "email": "invalid-email",
                "password": "password123"
            }
        )
        
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_register_weak_password(self, client: AsyncClient):
        """Test registration with weak password."""
        response = await client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "password": "weak"
            }
        )
        
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_register_password_without_letter(self, client: AsyncClient):
        """Test registration with password without letters."""
        response = await client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "password": "12345678"
            }
        )
        
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_register_password_without_number(self, client: AsyncClient):
        """Test registration with password without numbers."""
        response = await client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "password": "password"
            }
        )
        
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_login_success(self, client: AsyncClient):
        """Test successful user login."""
        # Register user first
        await client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "password": "password123"
            }
        )
        
        # Login
        response = await client.post(
            "/auth/login",
            json={
                "email": "test@example.com",
                "password": "password123"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["email"] == "test@example.com"
        assert "user_id" in data
    
    @pytest.mark.asyncio
    async def test_login_invalid_email(self, client: AsyncClient):
        """Test login with non-existent email."""
        response = await client.post(
            "/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "password123"
            }
        )
        
        assert response.status_code == 401
        data = response.json()
        assert "Invalid email or password" in data["detail"]
    
    @pytest.mark.asyncio
    async def test_login_wrong_password(self, client: AsyncClient):
        """Test login with wrong password."""
        # Register user first
        await client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "password": "password123"
            }
        )
        
        # Login with wrong password
        response = await client.post(
            "/auth/login",
            json={
                "email": "test@example.com",
                "password": "wrongpassword"
            }
        )
        
        assert response.status_code == 401
        data = response.json()
        assert "Invalid email or password" in data["detail"]
    
    @pytest.mark.asyncio
    async def test_login_soft_deleted_user(self, client: AsyncClient):
        """Test login with soft deleted user."""
        # Create and soft delete user directly in database
        async with TestAsyncSession() as session:
            user = User(
                email="deleted@example.com",
                password_hash="hashed_password",
                is_deleted=True
            )
            session.add(user)
            await session.commit()
        
        # Try to login
        response = await client.post(
            "/auth/login",
            json={
                "email": "deleted@example.com",
                "password": "password123"
            }
        )
        
        assert response.status_code == 401
        data = response.json()
        assert "Invalid email or password" in data["detail"]
    
    @pytest.mark.asyncio
    async def test_get_current_user_success(self, client: AsyncClient):
        """Test getting current user information."""
        # Register user
        register_response = await client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "password": "password123"
            }
        )
        token = register_response.json()["access_token"]
        
        # Get current user
        response = await client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["email"] == "test@example.com"
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data
    
    @pytest.mark.asyncio
    async def test_get_current_user_no_token(self, client: AsyncClient):
        """Test getting current user without token."""
        response = await client.get("/auth/me")
        
        assert response.status_code == 403
    
    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(self, client: AsyncClient):
        """Test getting current user with invalid token."""
        response = await client.get(
            "/auth/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_delete_current_user_success(self, client: AsyncClient):
        """Test deleting current user account."""
        # Register user
        register_response = await client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "password": "password123"
            }
        )
        token = register_response.json()["access_token"]
        
        # Delete user
        response = await client.delete(
            "/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 204
        
        # Verify user cannot login anymore
        login_response = await client.post(
            "/auth/login",
            json={
                "email": "test@example.com",
                "password": "password123"
            }
        )
        assert login_response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_delete_current_user_no_token(self, client: AsyncClient):
        """Test deleting user without token."""
        response = await client.delete("/auth/me")
        
        assert response.status_code == 403
    
    @pytest.mark.asyncio
    async def test_delete_current_user_invalid_token(self, client: AsyncClient):
        """Test deleting user with invalid token."""
        response = await client.delete(
            "/auth/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_authentication_flow(self, client: AsyncClient):
        """Test complete authentication flow."""
        # 1. Register user
        register_response = await client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "password": "password123"
            }
        )
        assert register_response.status_code == 201
        register_data = register_response.json()
        
        # 2. Login with same credentials
        login_response = await client.post(
            "/auth/login",
            json={
                "email": "test@example.com",
                "password": "password123"
            }
        )
        assert login_response.status_code == 200
        login_data = login_response.json()
        
        # Verify both responses have same user info
        assert register_data["user_id"] == login_data["user_id"]
        assert register_data["email"] == login_data["email"]
        
        # 3. Access protected endpoint
        token = login_data["access_token"]
        me_response = await client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert me_response.status_code == 200
        me_data = me_response.json()
        
        # Verify user data consistency
        assert me_data["id"] == login_data["user_id"]
        assert me_data["email"] == login_data["email"]