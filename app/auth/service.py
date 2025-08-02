"""
Authentication service layer for business logic.
"""
from datetime import timedelta
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token
)
from .repository import UserRepository
from .schemas import UserRegisterRequest, UserLoginRequest, AuthResponse, UserResponse
from .models import User


class AuthService:
    """Service layer for authentication business logic."""
    
    def __init__(self, session: AsyncSession):
        """Initialize service with database session."""
        self.session = session
        self.user_repo = UserRepository(session)
    
    async def register_user(self, request: UserRegisterRequest) -> AuthResponse:
        """
        Register a new user.
        
        Args:
            request: User registration request data
            
        Returns:
            AuthResponse: Authentication response with token
            
        Raises:
            HTTPException: If email already exists or registration fails
        """
        # Check if email already exists
        if await self.user_repo.email_exists(request.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Hash the password
        password_hash = get_password_hash(request.password)
        
        try:
            # Create the user
            user = await self.user_repo.create_user(
                email=request.email,
                password_hash=password_hash
            )
            
            # Generate access token
            access_token = create_access_token(
                data={"sub": str(user.id), "email": user.email}
            )
            
            return AuthResponse(
                access_token=access_token,
                token_type="bearer",
                user_id=user.id,
                email=user.email
            )
            
        except IntegrityError:
            # Handle race condition where email was registered between check and creation
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Registration failed"
            )
    
    async def login_user(self, request: UserLoginRequest) -> AuthResponse:
        """
        Authenticate user login.
        
        Args:
            request: User login request data
            
        Returns:
            AuthResponse: Authentication response with token
            
        Raises:
            HTTPException: If credentials are invalid
        """
        # Get user by email
        user = await self.user_repo.get_user_by_email(request.email)
        
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Verify password
        if not verify_password(request.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Generate access token
        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email}
        )
        
        return AuthResponse(
            access_token=access_token,
            token_type="bearer",
            user_id=user.id,
            email=user.email
        )
    
    async def get_user_by_id(self, user_id: int) -> Optional[UserResponse]:
        """
        Get user information by ID.
        
        Args:
            user_id: User ID
            
        Returns:
            UserResponse: User information or None if not found
        """
        user = await self.user_repo.get_user_by_id(user_id)
        
        if user is None:
            return None
        
        return UserResponse(
            id=user.id,
            email=user.email,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
    
    async def change_password(self, user_id: int, current_password: str, new_password: str) -> bool:
        """
        Change user password.
        
        Args:
            user_id: User ID
            current_password: Current password for verification
            new_password: New password
            
        Returns:
            bool: True if password was changed successfully
            
        Raises:
            HTTPException: If current password is invalid or user not found
        """
        # Get user
        user = await self.user_repo.get_user_by_id(user_id)
        
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Verify current password
        if not verify_password(current_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Hash new password and update
        new_password_hash = get_password_hash(new_password)
        return await self.user_repo.update_user_password(user_id, new_password_hash)
    
    async def delete_user(self, user_id: int) -> bool:
        """
        Soft delete a user account.
        
        Args:
            user_id: User ID to delete
            
        Returns:
            bool: True if user was deleted successfully
        """
        return await self.user_repo.soft_delete_user(user_id)