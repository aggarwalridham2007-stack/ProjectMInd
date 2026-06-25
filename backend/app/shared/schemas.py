"""Shared Pydantic schemas."""

from datetime import datetime
from typing import Any, Generic, Optional, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class BaseSchema(BaseModel):
    """Base schema with common configuration."""
    
    model_config = {"from_attributes": True}


class PaginationParams(BaseSchema):
    """Pagination parameters."""
    
    skip: int = Field(default=0, ge=0, description="Number of items to skip")
    limit: int = Field(default=10, ge=1, le=100, description="Number of items to return")


class PaginatedResponse(BaseSchema, Generic[T]):
    """Paginated response wrapper."""
    
    items: list[T]
    total: int
    skip: int
    limit: int
    
    @property
    def total_pages(self) -> int:
        """Calculate total pages."""
        return (self.total + self.limit - 1) // self.limit
    
    @property
    def current_page(self) -> int:
        """Calculate current page number."""
        return (self.skip // self.limit) + 1


class HealthResponse(BaseSchema):
    """Health check response."""
    
    status: str = Field(default="healthy", description="Health status")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    version: str = Field(description="Application version")
    environment: str = Field(description="Application environment")
    services: dict[str, str] = Field(default_factory=dict, description="Service health status")


class ErrorResponse(BaseSchema):
    """Error response schema."""
    
    error_code: str = Field(description="Application error code")
    message: str = Field(description="Error message")
    details: dict[str, Any] = Field(default_factory=dict, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")
    path: Optional[str] = Field(default=None, description="Request path")
    method: Optional[str] = Field(default=None, description="Request method")
