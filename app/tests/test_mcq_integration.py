"""
Integration tests for MCQ endpoints.
"""
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from fastapi import FastAPI
from app.core.database import Base, get_db
from app.auth.router import router as auth_router
from app.test_management.router import router as test_router
from app.mcq.router import router as mcq_router
from app.auth.models import User
from app.test_management.models import Test
from app.mcq.models import MCQ


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
    test_app.include_router(mcq_router)
    
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


@pytest_asyncio.fixture
async def test_with_user(client: AsyncClient, authenticated_user: dict, auth_headers: dict):
    """Create a test for the authenticated user."""
    response = await client.post(
        "/tests/",
        json={
            "title": "Sample Test",
            "description": "A test for MCQ questions"
        },
        headers=auth_headers
    )
    
    assert response.status_code == 201
    test_data = response.json()
    test_data["access_token"] = authenticated_user["access_token"]
    return test_data


@pytest_asyncio.fixture
async def another_authenticated_user(client: AsyncClient):
    """Create and authenticate another test user."""
    # Register user
    response = await client.post(
        "/auth/register",
        json={
            "email": "other@example.com",
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
async def other_auth_headers(another_authenticated_user):
    """Get authentication headers for another user."""
    return {"Authorization": f"Bearer {another_authenticated_user['access_token']}"}


class TestMCQEndpoints:
    """Integration tests for MCQ endpoints."""
    
    @pytest.mark.asyncio
    async def test_create_mcq_success(self, client: AsyncClient, auth_headers: dict, test_with_user: dict):
        """Test successful MCQ creation."""
        test_id = test_with_user["id"]
        
        response = await client.post(
            f"/tests/{test_id}/questions",
            json={
                "title": "What is the capital of France?",
                "description": "A geography question about European capitals",
                "option_1": "London",
                "option_2": "Berlin",
                "option_3": "Paris",
                "option_4": "Madrid",
                "correct_answer": 3
            },
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        
        assert data["title"] == "What is the capital of France?"
        assert data["description"] == "A geography question about European capitals"
        assert data["option_1"] == "London"
        assert data["option_2"] == "Berlin"
        assert data["option_3"] == "Paris"
        assert data["option_4"] == "Madrid"
        assert data["correct_answer"] == 3
        assert data["test_id"] == test_id
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data
    
    @pytest.mark.asyncio
    async def test_create_mcq_without_description(self, client: AsyncClient, auth_headers: dict, test_with_user: dict):
        """Test creating an MCQ without description."""
        test_id = test_with_user["id"]
        
        response = await client.post(
            f"/tests/{test_id}/questions",
            json={
                "title": "What is 2+2?",
                "option_1": "3",
                "option_2": "4",
                "option_3": "5",
                "option_4": "6",
                "correct_answer": 2
            },
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        
        assert data["title"] == "What is 2+2?"
        assert data["description"] is None
        assert data["correct_answer"] == 2
    
    @pytest.mark.asyncio
    async def test_create_mcq_unauthorized(self, client: AsyncClient, test_with_user: dict):
        """Test creating an MCQ without authentication."""
        test_id = test_with_user["id"]
        
        response = await client.post(
            f"/tests/{test_id}/questions",
            json={
                "title": "Question",
                "option_1": "A", "option_2": "B", "option_3": "C", "option_4": "D",
                "correct_answer": 1
            }
        )
        
        assert response.status_code == 403
    
    @pytest.mark.asyncio
    async def test_create_mcq_test_not_found(self, client: AsyncClient, auth_headers: dict):
        """Test creating an MCQ for a non-existent test."""
        response = await client.post(
            "/tests/999999/questions",
            json={
                "title": "Question",
                "option_1": "A", "option_2": "B", "option_3": "C", "option_4": "D",
                "correct_answer": 1
            },
            headers=auth_headers
        )
        
        assert response.status_code == 404
        assert "Test not found or access denied" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_create_mcq_access_denied(self, client: AsyncClient, other_auth_headers: dict, test_with_user: dict):
        """Test creating an MCQ for another user's test."""
        test_id = test_with_user["id"]
        
        response = await client.post(
            f"/tests/{test_id}/questions",
            json={
                "title": "Question",
                "option_1": "A", "option_2": "B", "option_3": "C", "option_4": "D",
                "correct_answer": 1
            },
            headers=other_auth_headers
        )
        
        assert response.status_code == 404
        assert "Test not found or access denied" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_create_mcq_invalid_correct_answer(self, client: AsyncClient, auth_headers: dict, test_with_user: dict):
        """Test creating an MCQ with invalid correct_answer."""
        test_id = test_with_user["id"]
        
        response = await client.post(
            f"/tests/{test_id}/questions",
            json={
                "title": "Question",
                "option_1": "A", "option_2": "B", "option_3": "C", "option_4": "D",
                "correct_answer": 5  # Invalid value
            },
            headers=auth_headers
        )
        
        assert response.status_code == 422  # Validation error
    
    @pytest.mark.asyncio
    async def test_get_test_questions_success(self, client: AsyncClient, auth_headers: dict, test_with_user: dict):
        """Test getting all MCQ questions for a test."""
        test_id = test_with_user["id"]
        
        # Create some MCQs
        mcq1_response = await client.post(
            f"/tests/{test_id}/questions",
            json={
                "title": "Question 1",
                "option_1": "A1", "option_2": "B1", "option_3": "C1", "option_4": "D1",
                "correct_answer": 1
            },
            headers=auth_headers
        )
        mcq2_response = await client.post(
            f"/tests/{test_id}/questions",
            json={
                "title": "Question 2",
                "option_1": "A2", "option_2": "B2", "option_3": "C2", "option_4": "D2",
                "correct_answer": 2
            },
            headers=auth_headers
        )
        
        assert mcq1_response.status_code == 201
        assert mcq2_response.status_code == 201
        
        # Get all questions
        response = await client.get(f"/tests/{test_id}/questions", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["total"] == 2
        assert len(data["questions"]) == 2
        
        question_titles = [q["title"] for q in data["questions"]]
        assert "Question 1" in question_titles
        assert "Question 2" in question_titles
    
    @pytest.mark.asyncio
    async def test_get_test_questions_empty(self, client: AsyncClient, auth_headers: dict, test_with_user: dict):
        """Test getting questions for a test with no questions."""
        test_id = test_with_user["id"]
        
        response = await client.get(f"/tests/{test_id}/questions", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["total"] == 0
        assert len(data["questions"]) == 0
    
    @pytest.mark.asyncio
    async def test_get_test_questions_unauthorized(self, client: AsyncClient, test_with_user: dict):
        """Test getting questions without authentication."""
        test_id = test_with_user["id"]
        
        response = await client.get(f"/tests/{test_id}/questions")
        
        assert response.status_code == 403
    
    @pytest.mark.asyncio
    async def test_get_test_questions_access_denied(self, client: AsyncClient, other_auth_headers: dict, test_with_user: dict):
        """Test getting questions for another user's test."""
        test_id = test_with_user["id"]
        
        response = await client.get(f"/tests/{test_id}/questions", headers=other_auth_headers)
        
        assert response.status_code == 404
        assert "Test not found or access denied" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_get_mcq_question_success(self, client: AsyncClient, auth_headers: dict, test_with_user: dict):
        """Test getting a specific MCQ question."""
        test_id = test_with_user["id"]
        
        # Create an MCQ
        create_response = await client.post(
            f"/tests/{test_id}/questions",
            json={
                "title": "What is the capital of France?",
                "description": "A geography question",
                "option_1": "London", "option_2": "Berlin", "option_3": "Paris", "option_4": "Madrid",
                "correct_answer": 3
            },
            headers=auth_headers
        )
        
        assert create_response.status_code == 201
        mcq_id = create_response.json()["id"]
        
        # Get the MCQ
        response = await client.get(f"/questions/{mcq_id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["id"] == mcq_id
        assert data["title"] == "What is the capital of France?"
        assert data["description"] == "A geography question"
        assert data["option_1"] == "London"
        assert data["option_2"] == "Berlin"
        assert data["option_3"] == "Paris"
        assert data["option_4"] == "Madrid"
        assert data["correct_answer"] == 3
        assert data["test_id"] == test_id
    
    @pytest.mark.asyncio
    async def test_get_mcq_question_not_found(self, client: AsyncClient, auth_headers: dict):
        """Test getting a non-existent MCQ question."""
        response = await client.get("/questions/999999", headers=auth_headers)
        
        assert response.status_code == 404
        assert "MCQ question not found or access denied" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_get_mcq_question_access_denied(self, client: AsyncClient, other_auth_headers: dict, test_with_user: dict):
        """Test getting an MCQ question from another user's test."""
        test_id = test_with_user["id"]
        
        # Create an MCQ as the first user
        create_response = await client.post(
            f"/tests/{test_id}/questions",
            json={
                "title": "Question",
                "option_1": "A", "option_2": "B", "option_3": "C", "option_4": "D",
                "correct_answer": 1
            },
            headers={"Authorization": f"Bearer {test_with_user['access_token']}"}
        )
        
        # Try to get it as another user
        response = await client.get(f"/questions/{create_response.json()['id']}", headers=other_auth_headers)
        
        assert response.status_code == 404
        assert "MCQ question not found or access denied" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_get_mcq_question_public_success(self, client: AsyncClient, auth_headers: dict, test_with_user: dict):
        """Test getting an MCQ question in public format (without correct answer)."""
        test_id = test_with_user["id"]
        
        # Create an MCQ
        create_response = await client.post(
            f"/tests/{test_id}/questions",
            json={
                "title": "What is the capital of France?",
                "option_1": "London", "option_2": "Berlin", "option_3": "Paris", "option_4": "Madrid",
                "correct_answer": 3
            },
            headers=auth_headers
        )
        
        assert create_response.status_code == 201
        mcq_id = create_response.json()["id"]
        
        # Get the MCQ in public format
        response = await client.get(f"/questions/{mcq_id}/public", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["id"] == mcq_id
        assert data["title"] == "What is the capital of France?"
        assert data["option_1"] == "London"
        assert data["option_2"] == "Berlin"
        assert data["option_3"] == "Paris"
        assert data["option_4"] == "Madrid"
        assert data["test_id"] == test_id
        # Verify correct_answer is not included
        assert "correct_answer" not in data
    
    @pytest.mark.asyncio
    async def test_get_mcq_question_by_test_success(self, client: AsyncClient, auth_headers: dict, test_with_user: dict):
        """Test getting an MCQ question by test and question ID."""
        test_id = test_with_user["id"]
        
        # Create an MCQ
        create_response = await client.post(
            f"/tests/{test_id}/questions",
            json={
                "title": "Question",
                "option_1": "A", "option_2": "B", "option_3": "C", "option_4": "D",
                "correct_answer": 1
            },
            headers=auth_headers
        )
        
        assert create_response.status_code == 201
        mcq_id = create_response.json()["id"]
        
        # Get the MCQ by test and question ID
        response = await client.get(f"/tests/{test_id}/questions/{mcq_id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["id"] == mcq_id
        assert data["title"] == "Question"
        assert data["test_id"] == test_id
    
    @pytest.mark.asyncio
    async def test_update_mcq_question_success(self, client: AsyncClient, auth_headers: dict, test_with_user: dict):
        """Test updating an MCQ question."""
        test_id = test_with_user["id"]
        
        # Create an MCQ
        create_response = await client.post(
            f"/tests/{test_id}/questions",
            json={
                "title": "Original Question",
                "description": "Original description",
                "option_1": "A", "option_2": "B", "option_3": "C", "option_4": "D",
                "correct_answer": 1
            },
            headers=auth_headers
        )
        
        assert create_response.status_code == 201
        mcq_id = create_response.json()["id"]
        
        # Update the MCQ
        response = await client.patch(
            f"/questions/{mcq_id}",
            json={
                "title": "Updated Question",
                "description": "Updated description",
                "correct_answer": 2
            },
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["id"] == mcq_id
        assert data["title"] == "Updated Question"
        assert data["description"] == "Updated description"
        assert data["option_1"] == "A"  # Unchanged
        assert data["option_2"] == "B"  # Unchanged
        assert data["option_3"] == "C"  # Unchanged
        assert data["option_4"] == "D"  # Unchanged
        assert data["correct_answer"] == 2
        assert data["test_id"] == test_id
    
    @pytest.mark.asyncio
    async def test_update_mcq_question_not_found(self, client: AsyncClient, auth_headers: dict):
        """Test updating a non-existent MCQ question."""
        response = await client.patch(
            "/questions/999999",
            json={"title": "Updated Question"},
            headers=auth_headers
        )
        
        assert response.status_code == 404
        assert "MCQ question not found or access denied" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_update_mcq_question_access_denied(self, client: AsyncClient, other_auth_headers: dict, test_with_user: dict):
        """Test updating an MCQ question from another user's test."""
        test_id = test_with_user["id"]
        
        # Create an MCQ as the first user
        create_response = await client.post(
            f"/tests/{test_id}/questions",
            json={
                "title": "Question",
                "option_1": "A", "option_2": "B", "option_3": "C", "option_4": "D",
                "correct_answer": 1
            },
            headers={"Authorization": f"Bearer {test_with_user['access_token']}"}
        )
        
        # Try to update it as another user
        response = await client.patch(
            f"/questions/{create_response.json()['id']}",
            json={"title": "Updated Question"},
            headers=other_auth_headers
        )
        
        assert response.status_code == 404
        assert "MCQ question not found or access denied" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_delete_mcq_question_success(self, client: AsyncClient, auth_headers: dict, test_with_user: dict):
        """Test deleting an MCQ question."""
        test_id = test_with_user["id"]
        
        # Create an MCQ
        create_response = await client.post(
            f"/tests/{test_id}/questions",
            json={
                "title": "Question to delete",
                "option_1": "A", "option_2": "B", "option_3": "C", "option_4": "D",
                "correct_answer": 1
            },
            headers=auth_headers
        )
        
        assert create_response.status_code == 201
        mcq_id = create_response.json()["id"]
        
        # Delete the MCQ
        response = await client.patch(f"/questions/{mcq_id}/delete", headers=auth_headers)
        
        assert response.status_code == 204
        
        # Verify the MCQ is deleted (should not be found)
        get_response = await client.get(f"/questions/{mcq_id}", headers=auth_headers)
        assert get_response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_delete_mcq_question_not_found(self, client: AsyncClient, auth_headers: dict):
        """Test deleting a non-existent MCQ question."""
        response = await client.patch("/questions/999999/delete", headers=auth_headers)
        
        assert response.status_code == 404
        assert "MCQ question not found or access denied" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_delete_mcq_question_access_denied(self, client: AsyncClient, other_auth_headers: dict, test_with_user: dict):
        """Test deleting an MCQ question from another user's test."""
        test_id = test_with_user["id"]
        
        # Create an MCQ as the first user
        create_response = await client.post(
            f"/tests/{test_id}/questions",
            json={
                "title": "Question",
                "option_1": "A", "option_2": "B", "option_3": "C", "option_4": "D",
                "correct_answer": 1
            },
            headers={"Authorization": f"Bearer {test_with_user['access_token']}"}
        )
        
        # Try to delete it as another user
        response = await client.patch(
            f"/questions/{create_response.json()['id']}/delete",
            headers=other_auth_headers
        )
        
        assert response.status_code == 404
        assert "MCQ question not found or access denied" in response.json()["detail"]