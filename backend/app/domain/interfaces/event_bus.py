"""Event bus interface for domain-driven design."""

from abc import ABC, abstractmethod
from typing import Any, Awaitable, Callable


class DomainEvent(ABC):
    """Base domain event interface."""
    
    @property
    @abstractmethod
    def event_type(self) -> str:
        """Event type identifier."""
    
    @property
    @abstractmethod
    def aggregate_id(self) -> Any:
        """Associated aggregate ID."""


class EventHandler(ABC):
    """Base event handler interface."""
    
    @abstractmethod
    async def handle(self, event: DomainEvent) -> None:
        """Handle domain event.
        
        Args:
            event: Domain event to handle.
        """
    
    @property
    @abstractmethod
    def event_type(self) -> str:
        """Event type this handler can process."""


class IEventBus(ABC):
    """Event bus interface - manages domain events."""
    
    @abstractmethod
    async def publish(self, event: DomainEvent) -> None:
        """Publish domain event.
        
        Args:
            event: Domain event to publish.
        """
    
    @abstractmethod
    async def subscribe(
        self,
        event_type: str,
        handler: Callable[[DomainEvent], Awaitable[None]],
    ) -> None:
        """Subscribe to domain events.
        
        Args:
            event_type: Event type to subscribe to.
            handler: Async handler function.
        """
    
    @abstractmethod
    async def unsubscribe(
        self,
        event_type: str,
        handler: Callable[[DomainEvent], Awaitable[None]],
    ) -> None:
        """Unsubscribe from domain events.
        
        Args:
            event_type: Event type to unsubscribe from.
            handler: Handler function to remove.
        """
