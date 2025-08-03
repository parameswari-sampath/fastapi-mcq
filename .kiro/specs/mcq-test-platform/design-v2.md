# Design Document - Version 2 (Role-Based Enhancement)

## Overview

The MCQ Test Platform v2 enhances the existing system by adding role-based access control with STUDENT and TEACHER roles. This design focuses on extending the current authentication system to support role selection during registration, including role information in JWT tokens, and implementing role-based authorization middleware to restrict all existing APIs to TEACHER role only. The existing functionality remains unchanged for teachers, while students will be able to register and login but cannot access any existing APIs until student-specific APIs are implemented in future versions.

## Architecture Changes

The role-based enhancement will modify the existing architecture in the following areas:

### Database Schema Changes
- Add `role` field to the existing User model
- Update authentication schemas to include role selection
- Maintain backward compatibility with existing user data

### Authentication System Changes
- Extend user registration to require role selection (STUDENT or TEACHER)
- Update JWT token generation to include role information
- Implement role-based authorization middleware
- Update login response to include role information

### API Authorization Changes
- Add role-based authorization to all existing endpoints
- Restrict all current test management APIs to TEACHER role
- Restrict all current MCQ management APIs to TEACHER role
- Maintain existing functionality for authorized teachers

## Components and Interfaces

### Enhanced User Model

The existing User model will be extended with a role field:

```python
class User:
    id: int (Primary Key, Auto-increment)
    email: str (Unique, Not Null)
    password_hash: str (Not Null)
    role: str (Not Null, Values: 'STUDENT' or 'TEACHER')  # NEW FIELD
    created_at: datetime
    updated_at: datetime
    is_deleted: bool (Default: False)
```

### Role Enumeration

```python
from enum import Enum

class UserRole(str, Enum):
    STUDENT = "STUDENT"
    TEACHER = "TEACHER"
```

### Updated Authentication Schemas

#### Registration Schema
```python
class UserRegisterRequest:
    email: str
    password: str
    role: UserRole  # NEW FIELD - Required role selection
```

#### Login Response Schema
```python
class AuthResponse:
    access_token: str
    token_type: str
    user_id: int
    role: str  # NEW FIELD - Include role in response
```

#### JWT Token Payload
```python
class TokenPayload:
    user_id: int
    email: str
    role: str  # NEW FIELD - Include role in JWT token
    exp: datetime
```

### Role-Based Authorization Middleware

```python
def require_teacher_role(current_user: User = Depends(get_current_user)):
    """
    Dependency that ensures the current user has TEACHER role
    Raises HTTPException(403) if user is not a teacher
    """
    if current_user.role != UserRole.TEACHER:
        raise HTTPException(
            status_code=403,
            detail="Access forbidden: Teacher role required"
        )
    return current_user
```

### Updated API Endpoints

All existing endpoints will be updated to require TEACHER role:

#### Test Management Endpoints (TEACHER only)
- `POST /tests` - Create new test (requires TEACHER role)
- `GET /tests` - Retrieve user's active tests (requires TEACHER role)
- `GET /tests/{test_id}` - Retrieve specific test (requires TEACHER role)
- `PATCH /tests/{test_id}` - Update test details (requires TEACHER role)
- `PATCH /tests/{test_id}/delete` - Soft delete test (requires TEACHER role)

#### MCQ Question Endpoints (TEACHER only)
- `POST /tests/{test_id}/questions` - Create new MCQ question (requires TEACHER role)
- `GET /tests/{test_id}/questions` - Retrieve test's active questions (requires TEACHER role)
- `GET /questions/{question_id}` - Retrieve specific question (requires TEACHER role)
- `PATCH /questions/{question_id}` - Update question details (requires TEACHER role)
- `PATCH /questions/{question_id}/delete` - Soft delete question (requires TEACHER role)

#### Authentication Endpoints (No role restriction)
- `POST /auth/register` - User registration with role selection
- `POST /auth/login` - User authentication with role information in response

## Data Models

### Database Migration

A new migration will be created to add the role field to the existing User table:

```sql
-- Add role column to user table
ALTER TABLE user ADD COLUMN role VARCHAR(10) NOT NULL DEFAULT 'TEACHER';

-- Add check constraint for valid roles
ALTER TABLE user ADD CONSTRAINT user_role_check 
CHECK (role IN ('STUDENT', 'TEACHER'));

-- Create index on role for performance
CREATE INDEX idx_user_role ON user(role);
```

### Backward Compatibility

- Existing users without a role will default to 'TEACHER' to maintain current functionality
- Existing JWT tokens without role information will be handled gracefully
- All existing API functionality remains unchanged for teachers

## Error Handling

### New HTTP Status Codes and Responses

#### Role-Based Authorization Errors
- `403 Forbidden` - When a student attempts to access teacher-only endpoints

```python
class RoleAuthorizationError:
    error: str = "forbidden"
    message: str = "Access forbidden: Teacher role required"
    details: Dict = {"required_role": "TEACHER", "user_role": "STUDENT"}
```

#### Registration Validation Errors
- `422 Unprocessable Entity` - When invalid role is provided during registration

```python
class RoleValidationError:
    error: str = "validation_error"
    message: str = "Invalid role specified"
    details: Dict = {"valid_roles": ["STUDENT", "TEACHER"]}
```

### Updated Validation Rules

- Role field is required during registration
- Role must be either 'STUDENT' or 'TEACHER'
- Role cannot be changed after registration (immutable)
- All existing validation rules remain unchanged

## Security Considerations

### JWT Token Security
- Role information is included in JWT payload but not sensitive
- Token expiration and refresh mechanisms remain unchanged
- Role validation occurs on every protected endpoint access

### Authorization Flow
1. User authenticates and receives JWT token with role information
2. Each protected endpoint validates the JWT token
3. Role-specific endpoints check user role before processing request
4. Unauthorized access returns 403 Forbidden with clear error message

### Role Immutability
- User roles cannot be changed after registration
- This prevents privilege escalation attacks
- Role changes would require administrative intervention (future feature)

## Testing Strategy

### Unit Tests
- Test role validation during user registration
- Test JWT token generation with role information
- Test role-based authorization middleware
- Test existing functionality with teacher role users

### Integration Tests
- Test complete registration flow with role selection
- Test login flow with role information in response
- Test all existing endpoints with teacher role authorization
- Test student role users receiving 403 errors on existing endpoints
- Test backward compatibility with existing teacher users

### Migration Tests
- Test database migration adds role field correctly
- Test default role assignment for existing users
- Test role constraints and validations

## Implementation Approach

### Phase 1: Database and Model Updates
1. Create database migration for role field
2. Update User model with role field
3. Create UserRole enum
4. Update user repository methods

### Phase 2: Authentication System Updates
1. Update registration schemas and validation
2. Update JWT token generation and validation
3. Update login response to include role
4. Create role-based authorization dependencies

### Phase 3: API Authorization Updates
1. Add teacher role requirement to all existing endpoints
2. Update error handling for role-based authorization
3. Test all existing functionality with role restrictions

### Phase 4: Testing and Validation
1. Run comprehensive test suite
2. Validate backward compatibility
3. Test role-based access control
4. Verify existing teacher functionality unchanged

This design ensures that the existing MCQ test platform functionality remains completely intact for teachers while adding the foundation for role-based access control and future student functionality.