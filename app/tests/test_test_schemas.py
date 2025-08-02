"""
Unit tests for Test schemas.
"""
import pytest
from datetime import datetime
from pydantic import ValidationError
from app.test_management.schemas import (
    TestCreateRequest,
    TestUpdateRequest,
    TestResponse,
    TestListResponse
)


class TestTestCreateRequest:
    """Test cases for TestCreateRequest schema."""
    
    def test_valid_test_create_request(self):
        """Test creating a valid test create request."""
        data = {
            "title": "Python Basics Quiz",
            "description": "A comprehensive quiz covering Python fundamentals"
        }
        
        request = TestCreateRequest(**data)
        
        assert request.title == "Python Basics Quiz"
        assert request.description == "A comprehensive quiz covering Python fundamentals"
    
    def test_test_create_request_without_description(self):
        """Test creating a test create request without description."""
        data = {
            "title": "Python Basics Quiz"
        }
        
        request = TestCreateRequest(**data)
        
        assert request.title == "Python Basics Quiz"
        assert request.description is None
    
    def test_test_create_request_empty_title_fails(self):
        """Test that empty title fails validation."""
        data = {
            "title": "",
            "description": "A quiz"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            TestCreateRequest(**data)
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["type"] == "string_too_short"
        assert "title" in errors[0]["loc"]
    
    def test_test_create_request_missing_title_fails(self):
        """Test that missing title fails validation."""
        data = {
            "description": "A quiz"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            TestCreateRequest(**data)
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["type"] == "missing"
        assert "title" in errors[0]["loc"]
    
    def test_test_create_request_title_too_long_fails(self):
        """Test that title longer than 200 characters fails validation."""
        data = {
            "title": "A" * 201,  # 201 characters
            "description": "A quiz"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            TestCreateRequest(**data)
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["type"] == "string_too_long"
        assert "title" in errors[0]["loc"]
    
    def test_test_create_request_description_too_long_fails(self):
        """Test that description longer than 1000 characters fails validation."""
        data = {
            "title": "Python Quiz",
            "description": "A" * 1001  # 1001 characters
        }
        
        with pytest.raises(ValidationError) as exc_info:
            TestCreateRequest(**data)
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["type"] == "string_too_long"
        assert "description" in errors[0]["loc"]
    
    def test_test_create_request_strips_whitespace(self):
        """Test that whitespace is stripped from strings."""
        data = {
            "title": "  Python Quiz  ",
            "description": "  A comprehensive quiz  "
        }
        
        request = TestCreateRequest(**data)
        
        assert request.title == "Python Quiz"
        assert request.description == "A comprehensive quiz"


class TestTestUpdateRequest:
    """Test cases for TestUpdateRequest schema."""
    
    def test_valid_test_update_request(self):
        """Test creating a valid test update request."""
        data = {
            "title": "Updated Python Quiz",
            "description": "An updated comprehensive quiz"
        }
        
        request = TestUpdateRequest(**data)
        
        assert request.title == "Updated Python Quiz"
        assert request.description == "An updated comprehensive quiz"
    
    def test_test_update_request_partial_update(self):
        """Test updating only title."""
        data = {
            "title": "Updated Python Quiz"
        }
        
        request = TestUpdateRequest(**data)
        
        assert request.title == "Updated Python Quiz"
        assert request.description is None
    
    def test_test_update_request_empty_data(self):
        """Test update request with no data."""
        data = {}
        
        request = TestUpdateRequest(**data)
        
        assert request.title is None
        assert request.description is None
    
    def test_test_update_request_empty_title_fails(self):
        """Test that empty title fails validation."""
        data = {
            "title": ""
        }
        
        with pytest.raises(ValidationError) as exc_info:
            TestUpdateRequest(**data)
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["type"] == "string_too_short"
        assert "title" in errors[0]["loc"]
    
    def test_test_update_request_title_too_long_fails(self):
        """Test that title longer than 200 characters fails validation."""
        data = {
            "title": "A" * 201  # 201 characters
        }
        
        with pytest.raises(ValidationError) as exc_info:
            TestUpdateRequest(**data)
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["type"] == "string_too_long"
        assert "title" in errors[0]["loc"]
    
    def test_test_update_request_strips_whitespace(self):
        """Test that whitespace is stripped from strings."""
        data = {
            "title": "  Updated Quiz  ",
            "description": "  Updated description  "
        }
        
        request = TestUpdateRequest(**data)
        
        assert request.title == "Updated Quiz"
        assert request.description == "Updated description"


class TestTestResponse:
    """Test cases for TestResponse schema."""
    
    def test_valid_test_response(self):
        """Test creating a valid test response."""
        data = {
            "id": 1,
            "title": "Python Quiz",
            "description": "A comprehensive quiz",
            "user_id": 1,
            "created_at": datetime(2024, 1, 8, 10, 0, 0),
            "updated_at": datetime(2024, 1, 8, 10, 0, 0)
        }
        
        response = TestResponse(**data)
        
        assert response.id == 1
        assert response.title == "Python Quiz"
        assert response.description == "A comprehensive quiz"
        assert response.user_id == 1
        assert response.created_at == datetime(2024, 1, 8, 10, 0, 0)
        assert response.updated_at == datetime(2024, 1, 8, 10, 0, 0)
    
    def test_test_response_without_description(self):
        """Test test response without description."""
        data = {
            "id": 1,
            "title": "Python Quiz",
            "description": None,
            "user_id": 1,
            "created_at": datetime(2024, 1, 8, 10, 0, 0),
            "updated_at": datetime(2024, 1, 8, 10, 0, 0)
        }
        
        response = TestResponse(**data)
        
        assert response.id == 1
        assert response.title == "Python Quiz"
        assert response.description is None
        assert response.user_id == 1
    
    def test_test_response_missing_required_fields_fails(self):
        """Test that missing required fields fail validation."""
        data = {
            "title": "Python Quiz"
            # Missing id, user_id, created_at, updated_at
        }
        
        with pytest.raises(ValidationError) as exc_info:
            TestResponse(**data)
        
        errors = exc_info.value.errors()
        required_fields = {"id", "user_id", "created_at", "updated_at"}
        error_fields = {error["loc"][0] for error in errors}
        
        assert required_fields.issubset(error_fields)
    
    def test_test_response_from_model_object(self):
        """Test creating response from model-like object."""
        class MockTest:
            def __init__(self):
                self.id = 1
                self.title = "Python Quiz"
                self.description = "A comprehensive quiz"
                self.user_id = 1
                self.created_at = datetime(2024, 1, 8, 10, 0, 0)
                self.updated_at = datetime(2024, 1, 8, 10, 0, 0)
        
        mock_test = MockTest()
        response = TestResponse.model_validate(mock_test)
        
        assert response.id == 1
        assert response.title == "Python Quiz"
        assert response.description == "A comprehensive quiz"
        assert response.user_id == 1


class TestTestListResponse:
    """Test cases for TestListResponse schema."""
    
    def test_valid_test_list_response(self):
        """Test creating a valid test list response."""
        test_data = {
            "id": 1,
            "title": "Python Quiz",
            "description": "A comprehensive quiz",
            "user_id": 1,
            "created_at": datetime(2024, 1, 8, 10, 0, 0),
            "updated_at": datetime(2024, 1, 8, 10, 0, 0)
        }
        
        data = {
            "tests": [test_data],
            "total": 1
        }
        
        response = TestListResponse(**data)
        
        assert len(response.tests) == 1
        assert response.total == 1
        assert response.tests[0].id == 1
        assert response.tests[0].title == "Python Quiz"
    
    def test_empty_test_list_response(self):
        """Test creating an empty test list response."""
        data = {
            "tests": [],
            "total": 0
        }
        
        response = TestListResponse(**data)
        
        assert len(response.tests) == 0
        assert response.total == 0
    
    def test_test_list_response_missing_fields_fails(self):
        """Test that missing required fields fail validation."""
        data = {
            "tests": []
            # Missing total
        }
        
        with pytest.raises(ValidationError) as exc_info:
            TestListResponse(**data)
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["type"] == "missing"
        assert "total" in errors[0]["loc"]