"""Repository pattern interfaces."""

from abc import ABC, abstractmethod
from typing import Generic, Optional, TypeVar

T = TypeVar("T")
ID = TypeVar("ID")


class IRepository(ABC, Generic[T, ID]):
    """Repository interface - abstraction for data access."""
    
    @abstractmethod
    async def get_by_id(self, id: ID) -> Optional[T]:
        """Get entity by ID.
        
        Args:
            id: Entity identifier.
            
        Returns:
            Entity or None if not found.
        """
    
    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 10) -> list[T]:
        """Get all entities with pagination.
        
        Args:
            skip: Number of items to skip.
            limit: Number of items to return.
            
        Returns:
            List of entities.
        """
    
    @abstractmethod
    async def add(self, entity: T) -> T:
        """Add new entity.
        
        Args:
            entity: Entity to add.
            
        Returns:
            Added entity.
        """
    
    @abstractmethod
    async def update(self, entity: T) -> T:
        """Update existing entity.
        
        Args:
            entity: Entity to update.
            
        Returns:
            Updated entity.
        """
    
    @abstractmethod
    async def delete(self, id: ID) -> bool:
        """Delete entity.
        
        Args:
            id: Entity identifier.
            
        Returns:
            True if deleted, False if not found.
        """
    
    @abstractmethod
    async def count(self) -> int:
        """Count total entities.
        
        Returns:
            Total count.
        """
