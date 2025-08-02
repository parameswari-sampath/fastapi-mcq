"""
Repository for test data access operations.
"""
from typing import List, Optional
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.test_management.models import Test


class TestRepository:
    """Repository for test data access operations."""
    
    def __init__(self, db_session: AsyncSession):
        """Initialize repository with database session."""
        self.db_session = db_session
    
    async def create(self, title: str, description: Optional[str], user_id: int) -> Test:
        """Create a new test."""
        test = Test(
            title=title,
            description=description,
            user_id=user_id
        )
        
        self.db_session.add(test)
        await self.db_session.commit()
        await self.db_session.refresh(test)
        
        return test
    
    async def get_by_id(self, test_id: int, user_id: int) -> Optional[Test]:
        """Get a test by ID for a specific user (only active tests)."""
        result = await self.db_session.execute(
            select(Test).where(
                Test.id == test_id,
                Test.user_id == user_id,
                Test.is_deleted == False
            )
        )
        return result.scalar_one_or_none()
    
    async def get_all_by_user(self, user_id: int) -> List[Test]:
        """Get all active tests for a specific user."""
        result = await self.db_session.execute(
            select(Test).where(
                Test.user_id == user_id,
                Test.is_deleted == False
            ).order_by(Test.created_at.desc())
        )
        return list(result.scalars().all())
    
    async def update(self, test_id: int, user_id: int, title: Optional[str] = None, 
                    description: Optional[str] = None) -> Optional[Test]:
        """Update a test for a specific user."""
        # First check if test exists and belongs to user
        test = await self.get_by_id(test_id, user_id)
        if not test:
            return None
        
        # Build update data
        update_data = {}
        if title is not None:
            update_data["title"] = title
        if description is not None:
            update_data["description"] = description
        
        # If no updates, return the existing test
        if not update_data:
            return test
        
        # Perform update
        await self.db_session.execute(
            update(Test).where(
                Test.id == test_id,
                Test.user_id == user_id,
                Test.is_deleted == False
            ).values(**update_data)
        )
        
        await self.db_session.commit()
        await self.db_session.refresh(test)
        
        return test
    
    async def soft_delete(self, test_id: int, user_id: int) -> bool:
        """Soft delete a test for a specific user."""
        # First check if test exists and belongs to user
        test = await self.get_by_id(test_id, user_id)
        if not test:
            return False
        
        # Perform soft delete
        await self.db_session.execute(
            update(Test).where(
                Test.id == test_id,
                Test.user_id == user_id,
                Test.is_deleted == False
            ).values(is_deleted=True)
        )
        
        await self.db_session.commit()
        return True
    
    async def count_by_user(self, user_id: int) -> int:
        """Count active tests for a specific user."""
        result = await self.db_session.execute(
            select(Test).where(
                Test.user_id == user_id,
                Test.is_deleted == False
            )
        )
        return len(list(result.scalars().all()))
    
    async def exists(self, test_id: int, user_id: int) -> bool:
        """Check if a test exists for a specific user."""
        test = await self.get_by_id(test_id, user_id)
        return test is not None