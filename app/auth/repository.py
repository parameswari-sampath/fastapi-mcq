"""
User repository for database operations.
"""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from .models import User


class UserRepository:
    """Repository for User database operations."""
    
    def __init__(self, session: AsyncSession):
        """Initialize repository with database session."""
        self.session = session
    
    async def create_user(self, email: str, password_hash: str) -> User:
        """
        Create a new user.
        
        Args:
            email: User email address
            password_hash: Hashed password
            
        Returns:
            User: Created user instance
            
        Raises:
            IntegrityError: If email already exists
        """
        user = User(
            email=email,
            password_hash=password_hash
        )
        
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        
        return user
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email address.
        
        Args:
            email: User email address
            
        Returns:
            User: User instance if found, None otherwise
        """
        stmt = select(User).where(
            User.email == email,
            User.is_deleted == False
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        Get user by ID.
        
        Args:
            user_id: User ID
            
        Returns:
            User: User instance if found, None otherwise
        """
        stmt = select(User).where(
            User.id == user_id,
            User.is_deleted == False
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def email_exists(self, email: str) -> bool:
        """
        Check if email already exists (including soft deleted users).
        
        Args:
            email: Email address to check
            
        Returns:
            bool: True if email exists, False otherwise
        """
        stmt = select(User.id).where(User.email == email)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None
    
    async def soft_delete_user(self, user_id: int) -> bool:
        """
        Soft delete a user by setting is_deleted to True.
        
        Args:
            user_id: User ID to delete
            
        Returns:
            bool: True if user was deleted, False if not found
        """
        user = await self.get_user_by_id(user_id)
        if user is None:
            return False
        
        user.is_deleted = True
        await self.session.commit()
        return True
    
    async def update_user_password(self, user_id: int, new_password_hash: str) -> bool:
        """
        Update user password.
        
        Args:
            user_id: User ID
            new_password_hash: New hashed password
            
        Returns:
            bool: True if password was updated, False if user not found
        """
        user = await self.get_user_by_id(user_id)
        if user is None:
            return False
        
        user.password_hash = new_password_hash
        await self.session.commit()
        return True