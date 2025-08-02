"""
Integration tests for test management endpoints.
"""
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from fastapi import FastAPI
from app.core.database import Base, get_db
from app.auth.router import router as auth_router
from app.test_management.router import router as test_router
from app.auth.models import User
from app.test_management.models import Test


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
    test_app.include_router(test_router)
    
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


@pytest_asyncio.fixture
async def authenticated_user(client: AsyncClient):
    """Create and authenticate a test user."""
    # Register user
    response = await client.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "password": "password123"
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    
    return {
        "user_id": data["user_id"],
        "access_token": data["access_token"],
        "email": data["email"]
    }


@pytest_asyncio.fixture
async def auth_headers(authenticated_user):
    """Get authentication headers."""
    return {"Authorization": f"Bearer {authenticated_user['access_token']}"}


class TestTestEndpoints:
    """Integration tests for test management endpoints."""
    
    @pytest.mark.asyncio
    async def test_create_test_success(self, client: AsyncClient, auth_headers: dict):
        """Test successful test creation."""
        response = await client.post(
            "/tests/",
            json={
                "title": "Python Basics Quiz",
                "description": "A comprehensive quiz covering Python fundamentals"
            },
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        
        assert data["title"] == "Python Basics Quiz"
        assert data["description"] == "A comprehensive quiz covering Python fundamentals"
        assert "id" in data
        assert "user_id" in data
        assert "created_at" in data
        assert "updated_at" in data
    
    @pytest.mark.asyncio
    async def test_create_test_without_description(self, client: AsyncClient, auth_headers: dict):
        """Test creating a test without description."""
        response = await client.post(
            "/tests/",
            json={
                "title": "Python Basics Quiz"
            },
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        
        assert data["title"] == "Python Basics Quiz"
        assert data["description"] is None
    
    @pytest.mark.asyncio
    async def test_create_test_unauthorized(self, client: AsyncClient):
        """Test creating a test without authentication."""
        response = await client.post(
            "/tests/",
            json={
                "title": "Python Basics Quiz",
                "description": "A quiz"
            }
        )
        
        assert response.status_code == 403
    
    @pytest.mark.asyncio
    async def test_create_test_invalid_data(self, client: AsyncClient, auth_headers: dict):
        """Test creating a test with invalid data."""
        response = await client.post(
            "/tests/",
            json={
                "title": "",  # Empty title
                "description": "A quiz"
            },
            headers=auth_headers
        )
        
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_get_user_tests_empty(self, client: AsyncClient, auth_headers: dict):
        """Test getting tests for user with no tests."""
        response = await client.get("/tests/", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["tests"] == []
        assert data["total"] == 0
    
    @pytest.mark.asyncio
    async def test_get_user_tests_with_data(self, client: AsyncClient, auth_headers: dict):
        """Test getting tests for user with tests."""
        # Create some tests
        test1_response = await client.post(
            "/tests/",
            json={"title": "Quiz 1", "description": "First quiz"},
            headers=auth_headers
        )
        test2_response = await client.post(
            "/tests/",
            json={"title": "Quiz 2"},
            headers=auth_headers
        )
        
        assert test1_response.status_code == 201
        assert test2_response.status_code == 201
        
        # Get all tests
        response = await client.get("/tests/", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["tests"]) == 2
        assert data["total"] == 2
        
        # Tests should be ordered by creation time (newest first)
        titles = [test["title"] for test in data["tests"]]
        assert "Quiz 1" in titles
        assert "Quiz 2" in titles
    
    @pytest.mark.asyncio
    async def test_get_user_tests_unauthorized(self, client: AsyncClient):
        """Test getting tests without authentication."""
        response = await client.get("/tests/")
        
        assert response.status_code == 403
    
    @pytest.mark.asyncio
    async def test_get_test_by_id_success(self, client: AsyncClient, auth_headers: dict):
        """Test getting a specific test by ID."""
        # Create a test
        create_response = await client.post(
            "/tests/",
            json={"title": "Python Quiz", "description": "A Python quiz"},
            headers=auth_headers
        )
        
        assert create_response.status_code == 201
        test_data = create_response.json()
        test_id = test_data["id"]
        
        # Get the test
        response = await client.get(f"/tests/{test_id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["id"] == test_id
        assert data["title"] == "Python Quiz"
        assert data["description"] == "A Python quiz"
    
    @pytest.mark.asyncio
    async def test_get_test_by_id_not_found(self, client: AsyncClient, auth_headers: dict):
        """Test getting a nonexistent test."""
        response = await client.get("/tests/999999", headers=auth_headers)
        
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Test not found"
    
    @pytest.mark.asyncio
    async def test_get_test_by_id_unauthorized(self, client: AsyncClient):
        """Test getting a test without authentication."""
        response = await client.get("/tests/1")
        
        assert response.status_code == 403
    
    @pytest.mark.asyncio
    async def test_get_test_by_id_different_user(self, client: AsyncClient, auth_headers: dict):
        """Test getting a test that belongs to another user."""
        # Create another user
        other_user_response = await client.post(
            "/auth/register",
            json={
                "email": "other@example.com",
                "password": "password123"
            }
        )
        
        assert other_user_response.status_code == 201
        other_user_data = other_user_response.json()
        other_auth_headers = {"Authorization": f"Bearer {other_user_data['access_token']}"}
        
        # Create a test with the other user
        create_response = await client.post(
            "/tests/",
            json={"title": "Other User's Quiz"},
            headers=other_auth_headers
        )
        
        assert create_response.status_code == 201
        test_data = create_response.json()
        test_id = test_data["id"]
        
        # Try to get the test with the first user
        response = await client.get(f"/tests/{test_id}", headers=auth_headers)
        
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Test not found"
    
    @pytest.mark.asyncio
    async def test_update_test_success(self, client: AsyncClient, auth_headers: dict):
        """Test successfully updating a test."""
        # Create a test
        create_response = await client.post(
            "/tests/",
            json={"title": "Original Title", "description": "Original description"},
            headers=auth_headers
        )
        
        assert create_response.status_code == 201
        test_data = create_response.json()
        test_id = test_data["id"]
        
        # Update the test
        response = await client.patch(
            f"/tests/{test_id}",
            json={"title": "Updated Title", "description": "Updated description"},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["id"] == test_id
        assert data["title"] == "Updated Title"
        assert data["description"] == "Updated description"
    
    @pytest.mark.asyncio
    async def test_update_test_partial(self, client: AsyncClient, auth_headers: dict):
        """Test partially updating a test."""
        # Create a test
        create_response = await client.post(
            "/tests/",
            json={"title": "Original Title", "description": "Original description"},
            headers=auth_headers
        )
        
        assert create_response.status_code == 201
        test_data = create_response.json()
        test_id = test_data["id"]
        
        # Update only the title
        response = await client.patch(
            f"/tests/{test_id}",
            json={"title": "Updated Title"},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["title"] == "Updated Title"
        assert data["description"] == "Original description"
    
    @pytest.mark.asyncio
    async def test_update_test_not_found(self, client: AsyncClient, auth_headers: dict):
        """Test updating a nonexistent test."""
        response = await client.patch(
            "/tests/999999",
            json={"title": "Updated Title"},
            headers=auth_headers
        )
        
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Test not found"
    
    @pytest.mark.asyncio
    async def test_update_test_unauthorized(self, client: AsyncClient):
        """Test updating a test without authentication."""
        response = await client.patch(
            "/tests/1",
            json={"title": "Updated Title"}
        )
        
        assert response.status_code == 403
    
    @pytest.mark.asyncio
    async def test_update_test_invalid_data(self, client: AsyncClient, auth_headers: dict):
        """Test updating a test with invalid data."""
        # Create a test
        create_response = await client.post(
            "/tests/",
            json={"title": "Original Title"},
            headers=auth_headers
        )
        
        assert create_response.status_code == 201
        test_data = create_response.json()
        test_id = test_data["id"]
        
        # Try to update with invalid data
        response = await client.patch(
            f"/tests/{test_id}",
            json={"title": ""},  # Empty title
            headers=auth_headers
        )
        
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_delete_test_success(self, client: AsyncClient, auth_headers: dict):
        """Test successfully deleting a test."""
        # Create a test
        create_response = await client.post(
            "/tests/",
            json={"title": "Test to Delete", "description": "This will be deleted"},
            headers=auth_headers
        )
        
        assert create_response.status_code == 201
        test_data = create_response.json()
        test_id = test_data["id"]
        
        # Delete the test
        response = await client.patch(f"/tests/{test_id}/delete", headers=auth_headers)
        
        assert response.status_code == 204
        
        # Verify the test is no longer accessible
        get_response = await client.get(f"/tests/{test_id}", headers=auth_headers)
        assert get_response.status_code == 404
        
        # Verify it's not in the user's test list
        list_response = await client.get("/tests/", headers=auth_headers)
        assert list_response.status_code == 200
        data = list_response.json()
        test_ids = [test["id"] for test in data["tests"]]
        assert test_id not in test_ids
    
    @pytest.mark.asyncio
    async def test_delete_test_not_found(self, client: AsyncClient, auth_headers: dict):
        """Test deleting a nonexistent test."""
        response = await client.patch("/tests/999999/delete", headers=auth_headers)
        
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Test not found"
    
    @pytest.mark.asyncio
    async def test_delete_test_unauthorized(self, client: AsyncClient):
        """Test deleting a test without authentication."""
        response = await client.patch("/tests/1/delete")
        
        assert response.status_code == 403
    
    @pytest.mark.asyncio
    async def test_complete_test_workflow(self, client: AsyncClient, auth_headers: dict):
        """Test complete workflow: create, read, update, delete."""
        # Create a test
        create_response = await client.post(
            "/tests/",
            json={"title": "Workflow Test", "description": "Testing complete workflow"},
            headers=auth_headers
        )
        
        assert create_response.status_code == 201
        test_data = create_response.json()
        test_id = test_data["id"]
        
        # Read the test
        get_response = await client.get(f"/tests/{test_id}", headers=auth_headers)
        assert get_response.status_code == 200
        
        # Update the test
        update_response = await client.patch(
            f"/tests/{test_id}",
            json={"title": "Updated Workflow Test"},
            headers=auth_headers
        )
        assert update_response.status_code == 200
        assert update_response.json()["title"] == "Updated Workflow Test"
        
        # Delete the test
        delete_response = await client.patch(f"/tests/{test_id}/delete", headers=auth_headers)
        assert delete_response.status_code == 204
        
        # Verify deletion
        final_get_response = await client.get(f"/tests/{test_id}", headers=auth_headers)
        assert final_get_response.status_code == 404