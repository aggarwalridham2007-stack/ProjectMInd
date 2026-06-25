"""Neo4j database client."""

import logging

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Neo4j driver - will be initialized in ServiceRegistry
_driver = None


async def initialize_neo4j() -> None:
    """Initialize Neo4j connection.
    
    This is called during application startup.
    """
    global _driver
    
    logger.info(f"Initializing Neo4j connection: {settings.neo4j_uri}")
    
    try:
        # Import here to avoid dependency if not used
        from neo4j import AsyncGraphDatabase
        
        _driver = AsyncGraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_user, settings.neo4j_password),
        )
        
        # Verify connection
        async with _driver.session(database=settings.neo4j_database) as session:
            result = await session.run("RETURN 1")
            await result.consume()
        
        logger.info("Neo4j connection established successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Neo4j: {e}")
        raise


async def cleanup_neo4j() -> None:
    """Clean up Neo4j connection.
    
    This is called during application shutdown.
    """
    global _driver
    
    if _driver:
        logger.info("Closing Neo4j connection...")
        await _driver.close()
        logger.info("Neo4j connection closed")


def get_neo4j_driver():
    """Get Neo4j driver.
    
    Returns:
        Neo4j driver instance.
        
    Raises:
        RuntimeError: If Neo4j not initialized.
    """
    if not _driver:
        raise RuntimeError("Neo4j not initialized. Call initialize_neo4j() first.")
    return _driver
