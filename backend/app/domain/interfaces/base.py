"""Base interfaces for domain layer."""

from abc import ABC, abstractmethod
from typing import Any, Generic, Optional, TypeVar

T = TypeVar("T")


class Entity(ABC):
    """Base entity interface."""
    
    @property
    @abstractmethod
    def id(self) -> Any:
        """Entity unique identifier."""


class ValueObject(ABC):
    """Base value object interface."""
    
    @abstractmethod
    def __eq__(self, other: object) -> bool:
        """Value object equality."""


class AggregateRoot(Entity):
    """Base aggregate root interface."""
    
    @abstractmethod
    def get_uncommitted_events(self) -> list[Any]:
        """Get uncommitted domain events."""
    
    @abstractmethod
    def clear_uncommitted_events(self) -> None:
        """Clear uncommitted domain events."""
