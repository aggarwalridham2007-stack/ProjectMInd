"""Service registry for dependency injection."""

import logging
from typing import Any

from app.infrastructure.event_bus import EventBus
from app.infrastructure.persistence.chromadb_client import (
    cleanup_chromadb,
    get_chromadb_client,
    initialize_chromadb,
)
from app.infrastructure.persistence.database import (
    cleanup_database,
    get_session_factory,
    initialize_database,
)
from app.infrastructure.persistence.neo4j_client import (
    cleanup_neo4j,
    get_neo4j_driver,
    initialize_neo4j,
)

logger = logging.getLogger(__name__)


class ServiceRegistry:
    """Service registry for dependency injection and service management.
    
    Manages initialization and cleanup of all application services.
    Follows the Service Locator pattern with lazy initialization.
    """
    
    def __init__(self) -> None:
        """Initialize service registry."""
        self._services: dict[str, Any] = {}
        self._initialized = False
        logger.info("ServiceRegistry created")
    
    async def initialize(self) -> None:
        """Initialize all services.
        
        Called during application startup in lifespan context.
        """
        if self._initialized:
            logger.warning("ServiceRegistry already initialized")
            return
        
        logger.info("Initializing services...")
        
        try:
            # Initialize persistence layer
            await initialize_database()
            
            # Initialize graph database
            try:
                await initialize_neo4j()
            except Exception as e:
                logger.warning(f"Neo4j initialization failed: {e}. Continuing without Neo4j.")
            
            # Initialize vector database
            try:
                await initialize_chromadb()
            except Exception as e:
                logger.warning(f"ChromaDB initialization failed: {e}. Continuing without ChromaDB.")
            
            # Register services
            self._services["event_bus"] = EventBus()
            
            self._initialized = True
            logger.info("All services initialized successfully")
        except Exception as e:
            logger.error(f"Service initialization failed: {e}")
            await self.cleanup()
            raise
    
    async def cleanup(self) -> None:
        """Clean up all services.
        
        Called during application shutdown in lifespan context.
        """
        if not self._initialized:
            return
        
        logger.info("Cleaning up services...")
        
        try:
            # Clean up in reverse order
            await cleanup_chromadb()
            await cleanup_neo4j()
            await cleanup_database()
            
            self._services.clear()
            self._initialized = False
            logger.info("All services cleaned up successfully")
        except Exception as e:
            logger.error(f"Service cleanup failed: {e}")
            raise
    
    def get(self, service_name: str) -> Any:
        """Get service instance by name.
        
        Args:
            service_name: Name of the service.
            
        Returns:
            Service instance.
            
        Raises:
            RuntimeError: If service not registered or not initialized.
        """
        if not self._initialized:
            raise RuntimeError("ServiceRegistry not initialized")
        
        if service_name not in self._services:
            raise RuntimeError(f"Service '{service_name}' not registered")
        
        return self._services[service_name]
    
    def register(self, name: str, service: Any) -> None:
        """Register service instance.
        
        Args:
            name: Service name.
            service: Service instance.
        """
        self._services[name] = service
        logger.info(f"Service registered: {name}")
    
    def has_service(self, service_name: str) -> bool:
        """Check if service is registered.
        
        Args:
            service_name: Name of the service.
            
        Returns:
            True if service exists, False otherwise.
        """
        return service_name in self._services
    
    @property
    def event_bus(self) -> EventBus:
        """Get event bus service."""
        return self.get("event_bus")
    
    @property
    def session_factory(self):
        """Get database session factory."""
        return get_session_factory()
    
    @property
    def neo4j_driver(self):
        """Get Neo4j driver."""
        return get_neo4j_driver()
    
    @property
    def chromadb_client(self):
        """Get ChromaDB client."""
        return get_chromadb_client()
