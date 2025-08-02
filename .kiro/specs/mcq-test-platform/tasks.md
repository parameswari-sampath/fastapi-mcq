# Implementation Plan

- [x] 1. Set up project structure and core configuration
  - Create the modular directory structure with auth, tests, mcq, and core modules
  - Initialize uv project with pyproject.toml and required dependencies
  - Set up core configuration files for database, security, and application settings
  - _Requirements: 4.4, 4.5_

- [x] 2. Implement core database and security utilities
  - [x] 2.1 Create async database connection and session management
    - Implement PostgreSQL async connection using SQLAlchemy and asyncpg
    - Create database session dependency for FastAPI
    - Set up database configuration with environment variables
    - _Requirements: 4.4_

  - [x] 2.2 Implement JWT authentication and password hashing utilities
    - Create JWT token generation and validation functions
    - Implement password hashing using bcrypt
    - Create authentication dependency for protected endpoints
    - _Requirements: 1.3, 1.4, 1.5, 4.5_

- [x] 3. Implement User authentication module
  - [x] 3.1 Create User model with SQLAlchemy
    - Define User model with id, email, password_hash, timestamps, and soft delete
    - Set up database relationships and constraints
    - Create unit tests for User model validation
    - _Requirements: 1.1, 1.2_

  - [x] 3.2 Create authentication schemas and validation
    - Implement Pydantic schemas for user registration and login requests
    - Create response schemas for authentication tokens
    - Add email format and password strength validation
    - _Requirements: 1.1, 1.2, 4.2_

  - [x] 3.3 Implement user repository for database operations
    - Create UserRepository with async methods for user CRUD operations
    - Implement user creation, retrieval by email, and authentication queries
    - Write unit tests for repository methods
    - _Requirements: 1.1, 1.3_

  - [x] 3.4 Create authentication service layer
    - Implement AuthService with user registration and login logic
    - Add duplicate email checking and password verification
    - Create unit tests for authentication business logic
    - _Requirements: 1.1, 1.2, 1.3, 1.4_

  - [x] 3.5 Implement authentication API endpoints
    - Create FastAPI router with POST /auth/register and POST /auth/login endpoints
    - Implement request validation and error handling
    - Write integration tests for authentication endpoints
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 4.1, 4.2, 4.3_

- [x] 4. Implement Test management module
  - [x] 4.1 Create Test model with relationships
    - Define Test model with id, title, description, user_id, timestamps, and soft delete
    - Set up foreign key relationship to User model
    - Create unit tests for Test model validation and relationships
    - _Requirements: 2.1, 2.2, 2.3, 2.6_

  - [x] 4.2 Create test schemas for API operations
    - Implement Pydantic schemas for test creation, update, and response
    - Add validation for required fields and optional description
    - Create unit tests for schema validation
    - _Requirements: 2.1, 2.2, 2.3, 4.2_

  - [x] 4.3 Implement test repository with soft delete
    - Create TestRepository with async methods for CRUD operations
    - Implement methods for creating, retrieving active tests, updating, and soft delete
    - Add user-specific test filtering
    - Write unit tests for repository methods including soft delete behavior
    - _Requirements: 2.1, 2.4, 2.5, 2.6_

  - [x] 4.4 Create test service layer
    - Implement TestService with business logic for test management
    - Add user authorization checks for test operations
    - Create unit tests for service layer logic
    - _Requirements: 2.1, 2.4, 2.5, 2.6_

  - [x] 4.5 Implement test API endpoints
    - Create FastAPI router with POST, GET, and PATCH endpoints for tests
    - Implement authentication middleware and user authorization
    - Add proper error handling and HTTP status codes
    - Write integration tests for all test endpoints
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 4.1, 4.2, 4.3_

- [x] 5. Implement MCQ questions module
  - [x] 5.1 Create MCQ model with test relationship
    - Define MCQ model with id, title, description, four options, correct_answer, test_id, timestamps, and soft delete
    - Set up foreign key relationship to Test model
    - Add validation for correct_answer field (1-4)
    - Create unit tests for MCQ model validation and relationships
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

  - [x] 5.2 Create MCQ schemas with validation
    - Implement Pydantic schemas for MCQ creation, update, and response
    - Add validation for required options and correct_answer range (1-4)
    - Create unit tests for schema validation including correct_answer constraints
    - _Requirements: 3.2, 3.3, 3.4, 4.2_

  - [x] 5.3 Implement MCQ repository with soft delete
    - Create MCQRepository with async methods for CRUD operations
    - Implement methods for creating, retrieving active questions by test, updating, and soft delete
    - Add test-specific question filtering
    - Write unit tests for repository methods including soft delete behavior
    - _Requirements: 3.1, 3.5, 3.6, 3.7, 3.8_

  - [x] 5.4 Create MCQ service layer
    - Implement MCQService with business logic for question management
    - Add user authorization checks for question operations (via test ownership)
    - Create unit tests for service layer logic
    - _Requirements: 3.1, 3.5, 3.6, 3.7, 3.8_

  - [x] 5.5 Implement MCQ API endpoints
    - Create FastAPI router with POST, GET, and PATCH endpoints for MCQ questions
    - Implement authentication middleware and test ownership authorization
    - Add proper error handling and HTTP status codes
    - Write integration tests for all MCQ endpoints
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 4.1, 4.2, 4.3_

- [ ] 6. Set up database migrations and main application
  - [ ] 6.1 Create Alembic migrations for all models
    - Initialize Alembic configuration for database migrations
    - Generate initial migration for User, Test, and MCQ models
    - Test migration up and down operations
    - _Requirements: 4.4_

  - [ ] 6.2 Create main FastAPI application
    - Set up main.py with FastAPI app initialization
    - Register all module routers (auth, tests, mcq)
    - Configure CORS and middleware
    - Add global exception handlers
    - _Requirements: 4.1, 4.3_

- [ ] 7. Implement comprehensive testing suite
  - [ ] 7.1 Set up test database and fixtures
    - Configure test database connection with async support
    - Create database fixtures for consistent test data
    - Set up test client for API integration tests
    - _Requirements: 4.4_

  - [ ] 7.2 Create end-to-end integration tests
    - Write integration tests covering complete user workflows
    - Test authentication flow with test and question creation
    - Test soft delete behavior across all modules
    - Verify authorization and error handling scenarios
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 4.1, 4.2, 4.3, 4.4, 4.5_