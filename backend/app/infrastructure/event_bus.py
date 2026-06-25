"""Event bus implementation."""

import asyncio
import logging
from typing import Awaitable, Callable

from app.domain.interfaces.event_bus import DomainEvent, IEventBus

logger = logging.getLogger(__name__)


class EventBus(IEventBus):
    """In-memory event bus implementation.
    
    For production use, consider using message queues like RabbitMQ or Kafka.
    """
    
    def __init__(self) -> None:
        """Initialize event bus."""
        self._handlers: dict[str, list[Callable[[DomainEvent], Awaitable[None]]]] = {}
        logger.info("EventBus initialized")
    
    async def publish(self, event: DomainEvent) -> None:
        """Publish domain event to all subscribers.
        
        Args:
            event: Domain event to publish.
        """
        event_type = event.event_type
        logger.info(f"Publishing event: {event_type}")
        
        handlers = self._handlers.get(event_type, [])
        
        if not handlers:
            logger.debug(f"No handlers registered for event: {event_type}")
            return
        
        # Execute all handlers concurrently
        tasks = [handler(event) for handler in handlers]
        await asyncio.gather(*tasks, return_exceptions=True)
        
        logger.info(f"Event published successfully: {event_type}")
    
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
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        
        self._handlers[event_type].append(handler)
        logger.info(f"Handler subscribed to event: {event_type}")
    
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
        if event_type in self._handlers:
            try:
                self._handlers[event_type].remove(handler)
                logger.info(f"Handler unsubscribed from event: {event_type}")
            except ValueError:
                logger.warning(f"Handler not found for event: {event_type}")
