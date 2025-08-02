"""
Repository for MCQ data access operations.
"""
from typing import List, Optional
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.mcq.models import MCQ


class MCQRepository:
    """Repository for MCQ data access operations."""
    
    def __init__(self, db_session: AsyncSession):
        """Initialize repository with database session."""
        self.db_session = db_session
    
    async def create(self, title: str, description: Optional[str], option_1: str, 
                    option_2: str, option_3: str, option_4: str, correct_answer: int, 
                    test_id: int) -> MCQ:
        """Create a new MCQ question."""
        mcq = MCQ(
            title=title,
            description=description,
            option_1=option_1,
            option_2=option_2,
            option_3=option_3,
            option_4=option_4,
            correct_answer=correct_answer,
            test_id=test_id
        )
        
        self.db_session.add(mcq)
        await self.db_session.commit()
        await self.db_session.refresh(mcq)
        
        return mcq
    
    async def get_by_id(self, mcq_id: int) -> Optional[MCQ]:
        """Get an MCQ by ID (only active questions)."""
        result = await self.db_session.execute(
            select(MCQ).where(
                MCQ.id == mcq_id,
                MCQ.is_deleted == False
            )
        )
        return result.scalar_one_or_none()
    
    async def get_all_by_test(self, test_id: int) -> List[MCQ]:
        """Get all active MCQ questions for a specific test."""
        result = await self.db_session.execute(
            select(MCQ).where(
                MCQ.test_id == test_id,
                MCQ.is_deleted == False
            ).order_by(MCQ.created_at.asc())
        )
        return list(result.scalars().all())
    
    async def update(self, mcq_id: int, title: Optional[str] = None, 
                    description: Optional[str] = None, option_1: Optional[str] = None,
                    option_2: Optional[str] = None, option_3: Optional[str] = None,
                    option_4: Optional[str] = None, correct_answer: Optional[int] = None) -> Optional[MCQ]:
        """Update an MCQ question."""
        # First check if MCQ exists
        mcq = await self.get_by_id(mcq_id)
        if not mcq:
            return None
        
        # Build update data
        update_data = {}
        if title is not None:
            update_data["title"] = title
        if description is not None:
            update_data["description"] = description
        if option_1 is not None:
            update_data["option_1"] = option_1
        if option_2 is not None:
            update_data["option_2"] = option_2
        if option_3 is not None:
            update_data["option_3"] = option_3
        if option_4 is not None:
            update_data["option_4"] = option_4
        if correct_answer is not None:
            update_data["correct_answer"] = correct_answer
        
        # If no updates, return the existing MCQ
        if not update_data:
            return mcq
        
        # Perform update
        await self.db_session.execute(
            update(MCQ).where(
                MCQ.id == mcq_id,
                MCQ.is_deleted == False
            ).values(**update_data)
        )
        
        await self.db_session.commit()
        await self.db_session.refresh(mcq)
        
        return mcq
    
    async def soft_delete(self, mcq_id: int) -> bool:
        """Soft delete an MCQ question."""
        # First check if MCQ exists
        mcq = await self.get_by_id(mcq_id)
        if not mcq:
            return False
        
        # Perform soft delete
        await self.db_session.execute(
            update(MCQ).where(
                MCQ.id == mcq_id,
                MCQ.is_deleted == False
            ).values(is_deleted=True)
        )
        
        await self.db_session.commit()
        return True
    
    async def count_by_test(self, test_id: int) -> int:
        """Count active MCQ questions for a specific test."""
        result = await self.db_session.execute(
            select(MCQ).where(
                MCQ.test_id == test_id,
                MCQ.is_deleted == False
            )
        )
        return len(list(result.scalars().all()))
    
    async def exists(self, mcq_id: int) -> bool:
        """Check if an MCQ question exists."""
        mcq = await self.get_by_id(mcq_id)
        return mcq is not None
    
    async def get_by_id_and_test(self, mcq_id: int, test_id: int) -> Optional[MCQ]:
        """Get an MCQ by ID that belongs to a specific test (only active questions)."""
        result = await self.db_session.execute(
            select(MCQ).where(
                MCQ.id == mcq_id,
                MCQ.test_id == test_id,
                MCQ.is_deleted == False
            )
        )
        return result.scalar_one_or_none()
    
    async def soft_delete_all_by_test(self, test_id: int) -> int:
        """Soft delete all MCQ questions for a specific test. Returns count of deleted questions."""
        # Get count of questions to be deleted
        questions = await self.get_all_by_test(test_id)
        count = len(questions)
        
        if count > 0:
            # Perform soft delete for all questions in the test
            await self.db_session.execute(
                update(MCQ).where(
                    MCQ.test_id == test_id,
                    MCQ.is_deleted == False
                ).values(is_deleted=True)
            )
            await self.db_session.commit()
        
        return count