"""
Unit tests for MCQ schemas.
"""
import pytest
from datetime import datetime
from pydantic import ValidationError
from app.mcq.schemas import (
    MCQCreateRequest,
    MCQUpdateRequest,
    MCQResponse,
    MCQListResponse,
    MCQPublicResponse
)


class TestMCQCreateRequest:
    """Test cases for MCQCreateRequest schema."""
    
    def test_valid_mcq_create_request(self):
        """Test creating a valid MCQ create request."""
        data = {
            "title": "What is the capital of France?",
            "description": "A geography question about European capitals",
            "option_1": "London",
            "option_2": "Berlin",
            "option_3": "Paris",
            "option_4": "Madrid",
            "correct_answer": 3
        }
        
        request = MCQCreateRequest(**data)
        
        assert request.title == "What is the capital of France?"
        assert request.description == "A geography question about European capitals"
        assert request.option_1 == "London"
        assert request.option_2 == "Berlin"
        assert request.option_3 == "Paris"
        assert request.option_4 == "Madrid"
        assert request.correct_answer == 3
    
    def test_mcq_create_request_without_description(self):
        """Test creating an MCQ create request without description."""
        data = {
            "title": "What is 2+2?",
            "option_1": "3",
            "option_2": "4",
            "option_3": "5",
            "option_4": "6",
            "correct_answer": 2
        }
        
        request = MCQCreateRequest(**data)
        
        assert request.title == "What is 2+2?"
        assert request.description is None
        assert request.option_1 == "3"
        assert request.option_2 == "4"
        assert request.option_3 == "5"
        assert request.option_4 == "6"
        assert request.correct_answer == 2
    
    def test_mcq_create_request_missing_title_fails(self):
        """Test that missing title fails validation."""
        data = {
            "option_1": "A",
            "option_2": "B",
            "option_3": "C",
            "option_4": "D",
            "correct_answer": 1
        }
        
        with pytest.raises(ValidationError) as exc_info:
            MCQCreateRequest(**data)
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["type"] == "missing"
        assert "title" in errors[0]["loc"]
    
    def test_mcq_create_request_empty_title_fails(self):
        """Test that empty title fails validation."""
        data = {
            "title": "",
            "option_1": "A",
            "option_2": "B",
            "option_3": "C",
            "option_4": "D",
            "correct_answer": 1
        }
        
        with pytest.raises(ValidationError) as exc_info:
            MCQCreateRequest(**data)
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["type"] == "string_too_short"
        assert "title" in errors[0]["loc"]
    
    def test_mcq_create_request_missing_options_fail(self):
        """Test that missing options fail validation."""
        data = {
            "title": "Question",
            "option_1": "A",
            "option_2": "B",
            # Missing option_3 and option_4
            "correct_answer": 1
        }
        
        with pytest.raises(ValidationError) as exc_info:
            MCQCreateRequest(**data)
        
        errors = exc_info.value.errors()
        assert len(errors) == 2
        error_fields = {error["loc"][0] for error in errors}
        assert "option_3" in error_fields
        assert "option_4" in error_fields
    
    def test_mcq_create_request_empty_options_fail(self):
        """Test that empty options fail validation."""
        data = {
            "title": "Question",
            "option_1": "",
            "option_2": "B",
            "option_3": "C",
            "option_4": "D",
            "correct_answer": 1
        }
        
        with pytest.raises(ValidationError) as exc_info:
            MCQCreateRequest(**data)
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["type"] == "string_too_short"
        assert "option_1" in errors[0]["loc"]
    
    def test_mcq_create_request_missing_correct_answer_fails(self):
        """Test that missing correct_answer fails validation."""
        data = {
            "title": "Question",
            "option_1": "A",
            "option_2": "B",
            "option_3": "C",
            "option_4": "D"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            MCQCreateRequest(**data)
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["type"] == "missing"
        assert "correct_answer" in errors[0]["loc"]
    
    def test_mcq_create_request_valid_correct_answer_values(self):
        """Test that valid correct_answer values (1, 2, 3, 4) are accepted."""
        base_data = {
            "title": "Question",
            "option_1": "A",
            "option_2": "B",
            "option_3": "C",
            "option_4": "D"
        }
        
        for correct_answer in [1, 2, 3, 4]:
            data = {**base_data, "correct_answer": correct_answer}
            request = MCQCreateRequest(**data)
            assert request.correct_answer == correct_answer
    
    def test_mcq_create_request_invalid_correct_answer_values_fail(self):
        """Test that invalid correct_answer values fail validation."""
        base_data = {
            "title": "Question",
            "option_1": "A",
            "option_2": "B",
            "option_3": "C",
            "option_4": "D"
        }
        
        invalid_values = [0, 5, -1, 10]
        
        for invalid_value in invalid_values:
            data = {**base_data, "correct_answer": invalid_value}
            with pytest.raises(ValidationError) as exc_info:
                MCQCreateRequest(**data)
            
            errors = exc_info.value.errors()
            # Should have validation error for correct_answer
            correct_answer_errors = [e for e in errors if "correct_answer" in e["loc"]]
            assert len(correct_answer_errors) > 0
    
    def test_mcq_create_request_title_too_long_fails(self):
        """Test that title longer than 500 characters fails validation."""
        data = {
            "title": "A" * 501,  # 501 characters
            "option_1": "A",
            "option_2": "B",
            "option_3": "C",
            "option_4": "D",
            "correct_answer": 1
        }
        
        with pytest.raises(ValidationError) as exc_info:
            MCQCreateRequest(**data)
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["type"] == "string_too_long"
        assert "title" in errors[0]["loc"]
    
    def test_mcq_create_request_option_too_long_fails(self):
        """Test that option longer than 500 characters fails validation."""
        data = {
            "title": "Question",
            "option_1": "A" * 501,  # 501 characters
            "option_2": "B",
            "option_3": "C",
            "option_4": "D",
            "correct_answer": 1
        }
        
        with pytest.raises(ValidationError) as exc_info:
            MCQCreateRequest(**data)
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["type"] == "string_too_long"
        assert "option_1" in errors[0]["loc"]
    
    def test_mcq_create_request_strips_whitespace(self):
        """Test that whitespace is stripped from strings."""
        data = {
            "title": "  What is the capital?  ",
            "description": "  A geography question  ",
            "option_1": "  London  ",
            "option_2": "  Berlin  ",
            "option_3": "  Paris  ",
            "option_4": "  Madrid  ",
            "correct_answer": 3
        }
        
        request = MCQCreateRequest(**data)
        
        assert request.title == "What is the capital?"
        assert request.description == "A geography question"
        assert request.option_1 == "London"
        assert request.option_2 == "Berlin"
        assert request.option_3 == "Paris"
        assert request.option_4 == "Madrid"


class TestMCQUpdateRequest:
    """Test cases for MCQUpdateRequest schema."""
    
    def test_valid_mcq_update_request(self):
        """Test creating a valid MCQ update request."""
        data = {
            "title": "Updated question",
            "description": "Updated description",
            "option_1": "Updated A",
            "option_2": "Updated B",
            "option_3": "Updated C",
            "option_4": "Updated D",
            "correct_answer": 2
        }
        
        request = MCQUpdateRequest(**data)
        
        assert request.title == "Updated question"
        assert request.description == "Updated description"
        assert request.option_1 == "Updated A"
        assert request.option_2 == "Updated B"
        assert request.option_3 == "Updated C"
        assert request.option_4 == "Updated D"
        assert request.correct_answer == 2
    
    def test_mcq_update_request_partial_update(self):
        """Test updating only some fields."""
        data = {
            "title": "Updated question",
            "correct_answer": 3
        }
        
        request = MCQUpdateRequest(**data)
        
        assert request.title == "Updated question"
        assert request.description is None
        assert request.option_1 is None
        assert request.option_2 is None
        assert request.option_3 is None
        assert request.option_4 is None
        assert request.correct_answer == 3
    
    def test_mcq_update_request_empty_data(self):
        """Test update request with no data."""
        data = {}
        
        request = MCQUpdateRequest(**data)
        
        assert request.title is None
        assert request.description is None
        assert request.option_1 is None
        assert request.option_2 is None
        assert request.option_3 is None
        assert request.option_4 is None
        assert request.correct_answer is None
    
    def test_mcq_update_request_invalid_correct_answer_fails(self):
        """Test that invalid correct_answer values fail validation."""
        invalid_values = [0, 5, -1, 10]
        
        for invalid_value in invalid_values:
            data = {"correct_answer": invalid_value}
            with pytest.raises(ValidationError) as exc_info:
                MCQUpdateRequest(**data)
            
            errors = exc_info.value.errors()
            correct_answer_errors = [e for e in errors if "correct_answer" in e["loc"]]
            assert len(correct_answer_errors) > 0
    
    def test_mcq_update_request_valid_correct_answer_values(self):
        """Test that valid correct_answer values are accepted."""
        for correct_answer in [1, 2, 3, 4]:
            data = {"correct_answer": correct_answer}
            request = MCQUpdateRequest(**data)
            assert request.correct_answer == correct_answer
    
    def test_mcq_update_request_strips_whitespace(self):
        """Test that whitespace is stripped from strings."""
        data = {
            "title": "  Updated question  ",
            "option_1": "  Updated A  "
        }
        
        request = MCQUpdateRequest(**data)
        
        assert request.title == "Updated question"
        assert request.option_1 == "Updated A"


class TestMCQResponse:
    """Test cases for MCQResponse schema."""
    
    def test_valid_mcq_response(self):
        """Test creating a valid MCQ response."""
        data = {
            "id": 1,
            "title": "What is the capital of France?",
            "description": "A geography question",
            "option_1": "London",
            "option_2": "Berlin",
            "option_3": "Paris",
            "option_4": "Madrid",
            "correct_answer": 3,
            "test_id": 1,
            "created_at": datetime(2024, 1, 8, 10, 0, 0),
            "updated_at": datetime(2024, 1, 8, 10, 0, 0)
        }
        
        response = MCQResponse(**data)
        
        assert response.id == 1
        assert response.title == "What is the capital of France?"
        assert response.description == "A geography question"
        assert response.option_1 == "London"
        assert response.option_2 == "Berlin"
        assert response.option_3 == "Paris"
        assert response.option_4 == "Madrid"
        assert response.correct_answer == 3
        assert response.test_id == 1
        assert response.created_at == datetime(2024, 1, 8, 10, 0, 0)
        assert response.updated_at == datetime(2024, 1, 8, 10, 0, 0)
    
    def test_mcq_response_without_description(self):
        """Test MCQ response without description."""
        data = {
            "id": 1,
            "title": "What is 2+2?",
            "description": None,
            "option_1": "3",
            "option_2": "4",
            "option_3": "5",
            "option_4": "6",
            "correct_answer": 2,
            "test_id": 1,
            "created_at": datetime(2024, 1, 8, 10, 0, 0),
            "updated_at": datetime(2024, 1, 8, 10, 0, 0)
        }
        
        response = MCQResponse(**data)
        
        assert response.id == 1
        assert response.title == "What is 2+2?"
        assert response.description is None
        assert response.correct_answer == 2
    
    def test_mcq_response_missing_required_fields_fails(self):
        """Test that missing required fields fail validation."""
        data = {
            "title": "Question"
            # Missing many required fields
        }
        
        with pytest.raises(ValidationError) as exc_info:
            MCQResponse(**data)
        
        errors = exc_info.value.errors()
        required_fields = {
            "id", "option_1", "option_2", "option_3", "option_4", 
            "correct_answer", "test_id", "created_at", "updated_at"
        }
        error_fields = {error["loc"][0] for error in errors}
        
        assert required_fields.issubset(error_fields)
    
    def test_mcq_response_from_model_object(self):
        """Test creating response from model-like object."""
        class MockMCQ:
            def __init__(self):
                self.id = 1
                self.title = "What is the capital of France?"
                self.description = "A geography question"
                self.option_1 = "London"
                self.option_2 = "Berlin"
                self.option_3 = "Paris"
                self.option_4 = "Madrid"
                self.correct_answer = 3
                self.test_id = 1
                self.created_at = datetime(2024, 1, 8, 10, 0, 0)
                self.updated_at = datetime(2024, 1, 8, 10, 0, 0)
        
        mock_mcq = MockMCQ()
        response = MCQResponse.model_validate(mock_mcq)
        
        assert response.id == 1
        assert response.title == "What is the capital of France?"
        assert response.correct_answer == 3
        assert response.test_id == 1


class TestMCQPublicResponse:
    """Test cases for MCQPublicResponse schema."""
    
    def test_valid_mcq_public_response(self):
        """Test creating a valid MCQ public response."""
        data = {
            "id": 1,
            "title": "What is the capital of France?",
            "description": "A geography question",
            "option_1": "London",
            "option_2": "Berlin",
            "option_3": "Paris",
            "option_4": "Madrid",
            "test_id": 1,
            "created_at": datetime(2024, 1, 8, 10, 0, 0),
            "updated_at": datetime(2024, 1, 8, 10, 0, 0)
        }
        
        response = MCQPublicResponse(**data)
        
        assert response.id == 1
        assert response.title == "What is the capital of France?"
        assert response.description == "A geography question"
        assert response.option_1 == "London"
        assert response.option_2 == "Berlin"
        assert response.option_3 == "Paris"
        assert response.option_4 == "Madrid"
        assert response.test_id == 1
        # Note: correct_answer should not be present in public response
        assert not hasattr(response, 'correct_answer')
    
    def test_mcq_public_response_from_model_object(self):
        """Test creating public response from model-like object."""
        class MockMCQ:
            def __init__(self):
                self.id = 1
                self.title = "What is the capital of France?"
                self.description = "A geography question"
                self.option_1 = "London"
                self.option_2 = "Berlin"
                self.option_3 = "Paris"
                self.option_4 = "Madrid"
                self.correct_answer = 3  # This should be excluded
                self.test_id = 1
                self.created_at = datetime(2024, 1, 8, 10, 0, 0)
                self.updated_at = datetime(2024, 1, 8, 10, 0, 0)
        
        mock_mcq = MockMCQ()
        response = MCQPublicResponse.model_validate(mock_mcq)
        
        assert response.id == 1
        assert response.title == "What is the capital of France?"
        assert response.test_id == 1
        # Verify correct_answer is not included
        assert not hasattr(response, 'correct_answer')


class TestMCQListResponse:
    """Test cases for MCQListResponse schema."""
    
    def test_valid_mcq_list_response(self):
        """Test creating a valid MCQ list response."""
        mcq_data = {
            "id": 1,
            "title": "What is the capital of France?",
            "description": "A geography question",
            "option_1": "London",
            "option_2": "Berlin",
            "option_3": "Paris",
            "option_4": "Madrid",
            "correct_answer": 3,
            "test_id": 1,
            "created_at": datetime(2024, 1, 8, 10, 0, 0),
            "updated_at": datetime(2024, 1, 8, 10, 0, 0)
        }
        
        data = {
            "questions": [mcq_data],
            "total": 1
        }
        
        response = MCQListResponse(**data)
        
        assert len(response.questions) == 1
        assert response.total == 1
        assert response.questions[0].id == 1
        assert response.questions[0].title == "What is the capital of France?"
        assert response.questions[0].correct_answer == 3
    
    def test_empty_mcq_list_response(self):
        """Test creating an empty MCQ list response."""
        data = {
            "questions": [],
            "total": 0
        }
        
        response = MCQListResponse(**data)
        
        assert len(response.questions) == 0
        assert response.total == 0
    
    def test_mcq_list_response_missing_fields_fails(self):
        """Test that missing required fields fail validation."""
        data = {
            "questions": []
            # Missing total
        }
        
        with pytest.raises(ValidationError) as exc_info:
            MCQListResponse(**data)
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["type"] == "missing"
        assert "total" in errors[0]["loc"]