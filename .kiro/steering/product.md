# Product Overview

## MCQ Test Platform

A FastAPI-based REST API platform for creating and managing multiple choice question tests. The platform provides secure user authentication and allows authenticated users to create tests, add MCQ questions with four options, and manage their assessments.

## Core Features

- **User Authentication**: Email/password registration and JWT-based authentication
- **Test Management**: Create, update, retrieve, and soft-delete tests with titles and descriptions
- **MCQ Questions**: Add multiple choice questions to tests with four options and correct answer tracking
- **Soft Delete Pattern**: All entities use soft delete to maintain data integrity
- **RESTful API**: Clean REST endpoints with proper HTTP status codes and error handling

## Target Users

- Educators creating assessments
- Training organizations building quizzes
- Anyone needing a structured MCQ testing platform

## Key Business Rules

- Users can only access their own tests and questions
- All data uses soft delete (is_deleted flag) rather than hard deletion
- MCQ questions must have exactly 4 options with correct answer being 1, 2, 3, or 4
- Tests act as containers for organizing related MCQ questions