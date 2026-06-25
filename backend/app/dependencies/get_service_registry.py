"""Dependency for getting service registry in FastAPI endpoints."""

from typing import Annotated

from fastapi import Depends, Request

from app.dependencies.service_registry import ServiceRegistry


async def get_service_registry(request: Request) -> ServiceRegistry:
    """Dependency injection for service registry.
    
    Args:
        request: FastAPI request object.
        
    Returns:
        ServiceRegistry instance from app state.
        
    Raises:
        RuntimeError: If service registry not available.
    """
    service_registry = getattr(request.app.state, "service_registry", None)
    
    if not service_registry:
        raise RuntimeError("Service registry not available in application state")
    
    return service_registry


# Type alias for dependency injection
ServiceRegistryDep = Annotated[ServiceRegistry, Depends(get_service_registry)]
