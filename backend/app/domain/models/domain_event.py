"""Base domain event implementation."""

from datetime import datetime
from typing import Any
from uuid import uuid4

from app.domain.interfaces.event_bus import DomainEvent


class BaseDomainEvent(DomainEvent):
    """Base implementation of domain event."""
    
    def __init__(
        self,
        event_type: str,
        aggregate_id: Any,
        data: dict[str, Any] | None = None,
    ):
        """Initialize domain event.
        
        Args:
            event_type: Type of event.
            aggregate_id: Associated aggregate ID.
            data: Event data.
        """
        self._event_type = event_type
        self._aggregate_id = aggregate_id
        self.data = data or {}
        self.event_id = str(uuid4())
        self.timestamp = datetime.utcnow()
    
    @property
    def event_type(self) -> str:
        """Event type identifier."""
        return self._event_type
    
    @property
    def aggregate_id(self) -> Any:
        """Associated aggregate ID."""
        return self._aggregate_id
