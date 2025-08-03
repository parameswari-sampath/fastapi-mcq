"""
Unit tests for User model role functionality.
"""
import pytest
from datetime import datetime
from enum import Enum
from app.auth.models import UserRole


class TestUserRoleModel:
    """Test cases for User model role functionality."""
    
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
    
