# Project Structure

## Root Directory Layout
```
app/                    # Main application package
├── main.py            # FastAPI application entry point
├── core/              # Core configuration and utilities
├── auth/              # User authentication module
├── tests/             # Test management module  
├── mcq/               # MCQ questions module
└── migrations/        # Alembic database migrations
```

## Module Organization Pattern

Each feature module (auth, tests, mcq) follows the same layered structure:

```
module_name/
├── __init__.py        # Module initialization
├── models.py          # SQLAlchemy database models
├── schemas.py         # Pydantic request/response schemas
├── repository.py      # Data access layer
├── service.py         # Business logic layer
└── router.py          # FastAPI route definitions
```

## Core Module Structure
```
core/
├── __init__.py
├── config.py          # Application configuration and environment variables
├── database.py        # Database connection and session management
└── security.py        # JWT authentication and password utilities
```

## Layer Responsibilities

### Router Layer (`router.py`)
- FastAPI route definitions and HTTP method handlers
- Request/response handling and validation
- Dependency injection for authentication and database sessions
- HTTP status code management

### Service Layer (`service.py`) 
- Business logic and validation rules
- Cross-module interactions and orchestration
- User authorization checks
- Data transformation between layers

### Repository Layer (`repository.py`)
- Database CRUD operations
- Query building and execution
- Data persistence and retrieval
- Soft delete implementation

### Model Layer (`models.py`)
- SQLAlchemy ORM model definitions
- Database table structure and relationships
- Model-level validations and constraints
- Timestamps and soft delete fields

### Schema Layer (`schemas.py`)
- Pydantic models for API request/response validation
- Data serialization and deserialization
- Input validation rules and constraints
- Type hints and documentation

## Naming Conventions

### Files and Modules
- Use snake_case for file and directory names
- Module names should be descriptive and singular (e.g., `auth`, not `auths`)

### Classes
- Models: Singular nouns (e.g., `User`, `Test`, `MCQ`)
- Repositories: `{Model}Repository` (e.g., `UserRepository`)
- Services: `{Module}Service` (e.g., `AuthService`)
- Schemas: Descriptive with suffix (e.g., `UserCreateRequest`, `TestResponse`)

### Database Tables
- Use snake_case for table names
- Singular nouns matching model names (e.g., `user`, `test`, `mcq`)

## Import Organization
```python
# Standard library imports
from datetime import datetime
from typing import Optional, List

# Third-party imports
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

# Local application imports
from app.core.database import get_db
from app.core.security import get_current_user
from .schemas import UserCreateRequest
from .service import AuthService
```

## Configuration Management
- Use environment variables for all configuration
- Store sensitive data (JWT secrets, database URLs) in environment variables
- Provide sensible defaults for development
- Use Pydantic Settings for configuration validation