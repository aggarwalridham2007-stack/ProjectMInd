"""ChromaDB vector database client."""

import logging

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# ChromaDB client - will be initialized in ServiceRegistry
_client = None


async def initialize_chromadb() -> None:
    """Initialize ChromaDB connection.
    
    This is called during application startup.
    """
    global _client
    
    logger.info(
        f"Initializing ChromaDB connection: {settings.chromadb_host}:{settings.chromadb_port}"
    )
    
    try:
        # Import here to avoid dependency if not used
        import chromadb
        
        # Initialize ChromaDB client
        _client = chromadb.HttpClient(
            host=settings.chromadb_host,
            port=settings.chromadb_port,
        )
        
        # Verify connection
        _client.heartbeat()
        
        logger.info("ChromaDB connection established successfully")
    except Exception as e:
        logger.error(f"Failed to initialize ChromaDB: {e}")
        raise


async def cleanup_chromadb() -> None:
    """Clean up ChromaDB connection.
    
    This is called during application shutdown.
    """
    global _client
    
    if _client:
        logger.info("Closing ChromaDB connection...")
        # ChromaDB doesn't require explicit cleanup, but we log it
        logger.info("ChromaDB connection closed")


def get_chromadb_client():
    """Get ChromaDB client.
    
    Returns:
        ChromaDB client instance.
        
    Raises:
        RuntimeError: If ChromaDB not initialized.
    """
    if not _client:
        raise RuntimeError("ChromaDB not initialized. Call initialize_chromadb() first.")
    return _client
