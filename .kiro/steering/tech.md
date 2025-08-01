# Technology Stack

## Package Manager
- **uv**: Modern Python package manager for dependency management and virtual environments

## Core Framework & Server
- **FastAPI**: Modern async web framework for building APIs
- **uvicorn[standard]**: ASGI server for running FastAPI applications

## Database & ORM
- **PostgreSQL**: Primary database (via asyncpg driver)
- **SQLAlchemy[asyncio]**: Async ORM for database operations
- **asyncpg**: Async PostgreSQL driver
- **alembic**: Database migration management

## Authentication & Security
- **python-jose[cryptography]**: JWT token handling
- **passlib[bcrypt]**: Password hashing with bcrypt

## Data Validation
- **pydantic**: Request/response validation and serialization
- **python-multipart**: Form data parsing support

## Testing
- **pytest**: Primary testing framework
- **pytest-asyncio**: Async testing support
- **httpx**: Async HTTP client for API testing

## Common Commands

### Project Setup
```bash
# Initialize project with uv
uv init
uv add fastapi uvicorn[standard] sqlalchemy[asyncio] asyncpg alembic pydantic python-jose[cryptography] passlib[bcrypt] python-multipart

# Development dependencies
uv add --dev pytest pytest-asyncio httpx
```

### Development
```bash
# Run development server
uv run uvicorn app.main:app --reload

# Run with specific host/port
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Database Operations
```bash
# Initialize Alembic
uv run alembic init migrations

# Create new migration
uv run alembic revision --autogenerate -m "migration description"

# Apply migrations
uv run alembic upgrade head

# Rollback migration
uv run alembic downgrade -1
```

### Testing
```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=app

# Run specific test file
uv run pytest tests/test_auth.py

# Run with verbose output
uv run pytest -v
```

## Architecture Patterns
- **Async/Await**: All database operations and API endpoints use async patterns
- **Dependency Injection**: FastAPI's dependency system for database sessions and authentication
- **Repository Pattern**: Separate data access layer for each module
- **Service Layer**: Business logic separated from API endpoints
- **Soft Delete**: Use `is_deleted` boolean flag instead of hard deletion