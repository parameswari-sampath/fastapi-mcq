# Design Document

## Overview

The MCQ Test Platform is a FastAPI-based REST API that provides user authentication and multiple choice question management functionality. The system uses JWT tokens for authentication, async SQLAlchemy with PostgreSQL for database operations, and implements soft delete patterns for data persistence. The platform supports three main entities: Users (authentication), Tests (question containers), and MCQ Questions (individual questions with four options).

## Required Packages

The project will use `uv` as the package manager. Required packages:

```
fastapi
uvicorn[standard]
sqlalchemy[asyncio]
asyncpg
alembic
pydantic
python-jose[cryptography]
passlib[bcrypt]
python-multipart
pytest
pytest-asyncio
httpx
```

### Package Descriptions
- **fastapi**: Modern web framework for building APIs
- **uvicorn**: ASGI server for running FastAPI applications
- **sqlalchemy[asyncio]**: Async ORM for database operations
- **asyncpg**: Async PostgreSQL driver
- **alembic**: Database migration tool for SQLAlchemy
- **pydantic**: Data validation and serialization
- **python-jose**: JWT token handling
- **passlib**: Password hashing utilities
- **python-multipart**: Form data parsing
- **pytest**: Testing framework
- **pytest-asyncio**: Async testing support
- **httpx**: Async HTTP client for testing

## Architecture

The application follows a modular architecture pattern with feature-based organization:

## Project Structure

```
app/
├── main.py                 # FastAPI application entry point
├── core/                   # Core configuration and utilities
│   ├── __init__.py
│   ├── config.py          # Application configuration
│   ├── database.py        # Database connection and session
│   └── security.py        # JWT and password utilities
├── auth/                   # Authentication module
│   ├── __init__.py
│   ├── models.py          # User model
│   ├── schemas.py         # Pydantic schemas
│   ├── service.py         # Authentication business logic
│   ├── repository.py      # User data access
│   └── router.py          # Authentication endpoints
├── tests/                  # Test management module
│   ├── __init__.py
│   ├── models.py          # Test model
│   ├── schemas.py         # Pydantic schemas
│   ├── service.py         # Test business logic
│   ├── repository.py      # Test data access
│   └── router.py          # Test endpoints
├── mcq/                    # MCQ questions module
│   ├── __init__.py
│   ├── models.py          # MCQ model
│   ├── schemas.py         # Pydantic schemas
│   ├── service.py         # MCQ business logic
│   ├── repository.py      # MCQ data access
│   └── router.py          # MCQ endpoints
└── migrations/             # Alembic database migrations
    └── versions/
```

## Module Architecture

Each module (auth, tests, mcq) follows the same internal structure:

```
┌─────────────────────────────────────┐
│           Router Layer              │
│  - FastAPI route definitions        │
│  - Request/response handling        │
│  - Dependency injection             │
└─────────────────────────────────────┘
                    │
┌─────────────────────────────────────┐
│         Service Layer               │
│  - Business logic                   │
│  - Data validation                  │
│  - Cross-module interactions        │
└─────────────────────────────────────┘
                    │
┌─────────────────────────────────────┐
│       Repository Layer              │
│  - Database operations              │
│  - Query building                   │
│  - Data persistence                 │
└─────────────────────────────────────┘
                    │
┌─────────────────────────────────────┐
│        Model Layer                  │
│  - SQLAlchemy models                │
│  - Database relationships           │
│  - Model validations                │
└─────────────────────────────────────┘
```

## Components and Interfaces

### Authentication Component
- **JWT Token Management**: Handles token generation, validation, and refresh
- **Password Hashing**: Uses bcrypt for secure password storage
- **Middleware**: Validates authentication for protected endpoints

### API Endpoints

#### Authentication Endpoints
- `POST /auth/register` - User registration
- `POST /auth/login` - User authentication

#### Test Management Endpoints
- `POST /tests` - Create new test
- `GET /tests` - Retrieve user's active tests
- `GET /tests/{test_id}` - Retrieve specific test
- `PATCH /tests/{test_id}` - Update test details
- `PATCH /tests/{test_id}/delete` - Soft delete test

#### MCQ Question Endpoints
- `POST /tests/{test_id}/questions` - Create new MCQ question
- `GET /tests/{test_id}/questions` - Retrieve test's active questions
- `GET /questions/{question_id}` - Retrieve specific question
- `PATCH /questions/{question_id}` - Update question details
- `PATCH /questions/{question_id}/delete` - Soft delete question

## Data Models

### User Model
```python
class User:
    id: int (Primary Key, Auto-increment)
    email: str (Unique, Not Null)
    password_hash: str (Not Null)
    created_at: datetime
    updated_at: datetime
    is_deleted: bool (Default: False)
```

### Test Model
```python
class Test:
    id: int (Primary Key, Auto-increment)
    title: str (Not Null)
    description: str (Nullable, Default: None)
    user_id: int (Foreign Key to User)
    created_at: datetime
    updated_at: datetime
    is_deleted: bool (Default: False)
    
    # Relationships
    questions: List[MCQ] (One-to-Many)
    user: User (Many-to-One)
```

### MCQ Model
```python
class MCQ:
    id: int (Primary Key, Auto-increment)
    title: str (Not Null)
    description: str (Nullable)
    option_1: str (Not Null)
    option_2: str (Not Null)
    option_3: str (Not Null)
    option_4: str (Not Null)
    correct_answer: int (Not Null, Values: 1-4)
    test_id: int (Foreign Key to Test)
    created_at: datetime
    updated_at: datetime
    is_deleted: bool (Default: False)
    
    # Relationships
    test: Test (Many-to-One)
```

### Request/Response Schemas

#### Authentication Schemas
```python
class UserRegisterRequest:
    email: str
    password: str

class UserLoginRequest:
    email: str
    password: str

class AuthResponse:
    access_token: str
    token_type: str
    user_id: int
```

#### Test Schemas
```python
class TestCreateRequest:
    title: str
    description: Optional[str] = None

class TestUpdateRequest:
    title: Optional[str] = None
    description: Optional[str] = None

class TestResponse:
    id: int
    title: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime
```

#### MCQ Schemas
```python
class MCQCreateRequest:
    title: str
    description: Optional[str] = None
    option_1: str
    option_2: str
    option_3: str
    option_4: str
    correct_answer: int  # 1-4

class MCQUpdateRequest:
    title: Optional[str] = None
    description: Optional[str] = None
    option_1: Optional[str] = None
    option_2: Optional[str] = None
    option_3: Optional[str] = None
    option_4: Optional[str] = None
    correct_answer: Optional[int] = None  # 1-4

class MCQResponse:
    id: int
    title: str
    description: Optional[str]
    option_1: str
    option_2: str
    option_3: str
    option_4: str
    correct_answer: int
    test_id: int
    created_at: datetime
    updated_at: datetime
```

## Error Handling

### HTTP Status Codes
- `200 OK` - Successful GET/PATCH operations
- `201 Created` - Successful POST operations
- `400 Bad Request` - Invalid request data/validation errors
- `401 Unauthorized` - Authentication required/invalid token
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found or soft deleted
- `422 Unprocessable Entity` - Validation errors
- `500 Internal Server Error` - Server errors

### Error Response Format
```python
class ErrorResponse:
    error: str
    message: str
    details: Optional[Dict] = None
```

### Validation Rules
- Email format validation for user registration
- Password minimum length (8 characters)
- Test title required and max length (200 characters)
- MCQ correct_answer must be 1, 2, 3, or 4
- All MCQ options required and max length (500 characters each)

## Testing Strategy

### Unit Tests
- Model validation and relationships
- Service layer business logic
- Repository CRUD operations
- Authentication token handling

### Integration Tests
- API endpoint functionality
- Database operations with test database
- Authentication middleware
- Soft delete behavior

### Test Database
- Use PostgreSQL test database for testing
- Separate test configuration with async database session
- Database fixtures for consistent test data
- Async test client for API testing

### Test Coverage Areas
- User registration and authentication flows
- Test CRUD operations with soft delete
- MCQ CRUD operations with soft delete
- Authorization checks for protected endpoints
- Input validation and error handling
- Database relationship integrity