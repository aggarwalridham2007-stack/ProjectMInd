"""Health check endpoint."""

from typing import Optional

from fastapi import APIRouter, Depends

from app.core.config import get_settings
from app.dependencies.get_service_registry import ServiceRegistryDep
from app.shared.schemas import HealthResponse

router = APIRouter()
settings = get_settings()


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health Check",
    description="Check application and service health status",
    tags=["health"],
)
async def health_check(
    service_registry: ServiceRegistryDep,
) -> HealthResponse:
    """Health check endpoint.
    
    Returns application health status and service availability.
    
    Args:
        service_registry: Service registry from dependency injection.
        
    Returns:
        HealthResponse with status and service information.
    """
    services_status: dict[str, str] = {}
    
    # Check PostgreSQL
    try:
        session_factory = service_registry.session_factory
        async with session_factory() as session:
            await session.execute("SELECT 1")
        services_status["postgresql"] = "healthy"
    except Exception as e:
        services_status["postgresql"] = f"unhealthy: {str(e)[:50]}"
    
    # Check Neo4j (optional)
    try:
        if service_registry.has_service("neo4j"):
            driver = service_registry.neo4j_driver
            async with driver.session(database="neo4j") as session:
                await session.run("RETURN 1")
            services_status["neo4j"] = "healthy"
    except Exception as e:
        services_status["neo4j"] = f"unhealthy: {str(e)[:50]}"
    
    # Check ChromaDB (optional)
    try:
        if service_registry.has_service("chromadb"):
            client = service_registry.chromadb_client
            client.heartbeat()
            services_status["chromadb"] = "healthy"
    except Exception as e:
        services_status["chromadb"] = f"unhealthy: {str(e)[:50]}"
    
    # Check Event Bus
    try:
        _ = service_registry.event_bus
        services_status["event_bus"] = "healthy"
    except Exception as e:
        services_status["event_bus"] = f"unhealthy: {str(e)[:50]}"
    
    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        environment=settings.app_env,
        services=services_status,
    )
