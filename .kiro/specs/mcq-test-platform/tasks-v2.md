# Implementation Plan - Version 2 (Role-Based Enhancement)

- [x] 1. Update User model and database schema for role support
  - [x] 1.1 Add UserRole enum and update User model with role field
    - Create UserRole enum with STUDENT and TEACHER values
    - Update User SQLAlchemy model to include role field with validation
    - Write unit tests for User model with role validation
    - _Requirements: 1.1, 1.3_

  - [x] 1.2 Create database migration for role field
    - Generate Alembic migration to add role column to user table
    - Set default role as TEACHER for backward compatibility
    - Add database constraints for valid role values
    - Test migration up and down operations
    - _Requirements: 1.1, 4.3_

- [ ] 2. Update authentication schemas and validation
  - [ ] 2.1 Update registration schemas to include role selection
    - Modify UserRegisterRequest schema to include required role field
    - Add role validation to ensure only STUDENT or TEACHER values
    - Update registration response schemas if needed
    - Write unit tests for schema validation with role field
    - _Requirements: 1.1, 1.3_

  - [ ] 2.2 Update login response schemas to include role information
    - Modify AuthResponse schema to include role field
    - Ensure role information is returned in login response
    - Write unit tests for login response schema validation
    - _Requirements: 2.1_

- [ ] 3. Update JWT token handling for role information
  - [ ] 3.1 Modify JWT token generation to include role in payload
    - Update token creation functions to include user role in JWT payload
    - Ensure role information is properly encoded in tokens
    - Write unit tests for JWT token generation with role
    - _Requirements: 2.1, 4.4_

  - [ ] 3.2 Update JWT token validation to extract role information
    - Modify token validation functions to extract role from JWT payload
    - Update get_current_user dependency to include role information
    - Handle backward compatibility for existing tokens without role
    - Write unit tests for JWT token validation with role extraction
    - _Requirements: 2.1, 2.2, 4.4_

- [ ] 4. Implement role-based authorization middleware
  - [ ] 4.1 Create teacher role authorization dependency
    - Implement require_teacher_role dependency function
    - Add proper error handling for unauthorized role access
    - Return HTTP 403 Forbidden for non-teacher users
    - Write unit tests for role authorization dependency
    - _Requirements: 2.3, 3.1, 3.2, 4.1_

  - [ ] 4.2 Update error handling for role-based authorization
    - Create specific error responses for role authorization failures
    - Implement proper HTTP status codes and error messages
    - Add detailed error information for debugging
    - Write unit tests for role-based error handling
    - _Requirements: 2.3, 4.2_

- [ ] 5. Update user repository and service for role support
  - [ ] 5.1 Update user repository methods for role handling
    - Modify user creation methods to handle role field
    - Update user retrieval methods to include role information
    - Ensure all user database operations support role field
    - Write unit tests for repository methods with role support
    - _Requirements: 1.1, 1.4_

  - [ ] 5.2 Update authentication service for role-based operations
    - Modify user registration service to handle role selection
    - Update login service to include role in response
    - Add role validation in service layer
    - Write unit tests for authentication service with role support
    - _Requirements: 1.1, 1.4, 2.1, 2.4_

- [ ] 6. Add role-based authorization to existing test management APIs
  - [ ] 6.1 Update test router endpoints with teacher role requirement
    - Add require_teacher_role dependency to all test management endpoints
    - Ensure POST, GET, PATCH endpoints require TEACHER role
    - Test that STUDENT role users receive 403 Forbidden errors
    - Write integration tests for role-based test API authorization
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

  - [ ] 6.2 Update test service layer for role-based operations
    - Ensure test service methods work with role-authorized users
    - Maintain all existing functionality for teacher users
    - Add any necessary role-based business logic
    - Write unit tests for test service with role authorization
    - _Requirements: 3.4, 3.5_

- [ ] 7. Add role-based authorization to existing MCQ management APIs
  - [ ] 7.1 Update MCQ router endpoints with teacher role requirement
    - Add require_teacher_role dependency to all MCQ management endpoints
    - Ensure POST, GET, PATCH endpoints require TEACHER role
    - Test that STUDENT role users receive 403 Forbidden errors
    - Write integration tests for role-based MCQ API authorization
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

  - [ ] 7.2 Update MCQ service layer for role-based operations
    - Ensure MCQ service methods work with role-authorized users
    - Maintain all existing functionality for teacher users
    - Add any necessary role-based business logic
    - Write unit tests for MCQ service with role authorization
    - _Requirements: 3.4, 3.5_

- [ ] 8. Update authentication router for role-based registration and login
  - [ ] 8.1 Update registration endpoint to handle role selection
    - Modify POST /auth/register to accept and validate role field
    - Ensure proper error handling for invalid role values
    - Test registration with both STUDENT and TEACHER roles
    - Write integration tests for role-based registration
    - _Requirements: 1.1, 1.2, 1.3_

  - [ ] 8.2 Update login endpoint to return role information
    - Modify POST /auth/login to include role in response
    - Ensure JWT token contains role information
    - Test login response includes correct role data
    - Write integration tests for role-based login
    - _Requirements: 2.1, 2.4_

- [ ] 9. Implement comprehensive testing for role-based functionality
  - [ ] 9.1 Create integration tests for complete role-based workflows
    - Test complete registration flow with STUDENT and TEACHER roles
    - Test login flow with role information in JWT tokens
    - Test all existing APIs with teacher role authorization
    - Test student role users receiving proper 403 errors on existing APIs
    - _Requirements: 1.1, 1.2, 1.3, 2.1, 2.2, 2.3, 3.1, 3.2, 3.3, 3.4, 3.5, 4.1, 4.2, 4.3, 4.4_

  - [ ] 9.2 Test backward compatibility with existing users
    - Test that existing users without roles default to TEACHER
    - Test that existing teacher functionality remains unchanged
    - Test migration process with existing user data
    - Verify all existing tests still pass with role-based changes
    - _Requirements: 2.4, 3.4, 4.3_

- [ ] 10. Update main application configuration for role-based system
  - [ ] 10.1 Update FastAPI application with role-based middleware
    - Ensure all routers are properly configured with role dependencies
    - Update global exception handlers for role-based errors
    - Test complete application startup with role-based configuration
    - _Requirements: 4.1, 4.2, 4.4_

  - [ ] 10.2 Update documentation and API specifications
    - Update API documentation to reflect role-based authorization
    - Document new registration and login schemas with role fields
    - Add examples of role-based error responses
    - Update any existing API documentation for teacher-only access
    - _Requirements: 4.2, 4.4_