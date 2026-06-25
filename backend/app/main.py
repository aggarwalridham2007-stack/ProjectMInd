"""FastAPI application factory and entry point."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import health
from app.core.config import get_settings
from app.core.logging import setup_logging
from app.dependencies.service_registry import ServiceRegistry
from app.middleware.error_handler import ErrorHandlerMiddleware
from app.middleware.logging_middleware import LoggingMiddleware

logger = logging.getLogger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events (startup and shutdown)."""
    # Startup
    logger.info(
        f"Starting {settings.app_name} v{settings.app_version} "
        f"in {settings.app_env} environment"
    )
    
    service_registry = ServiceRegistry()
    await service_registry.initialize()
    app.state.service_registry = service_registry
    
    logger.info("Service registry initialized")
    logger.info(f"Application listening on {settings.server_host}:{settings.server_port}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    await service_registry.cleanup()
    logger.info("Application shutdown complete")


def create_app() -> FastAPI:
    """Create and configure FastAPI application.
    
    Returns:
        Configured FastAPI application instance.
    """
    # Setup logging
    setup_logging(settings.log_level, settings.log_format)
    logger.info("Logging configured")
    
    # Create FastAPI app
    app = FastAPI(
        title=settings.app_name,
        description="AI-Powered Scientific Research Intelligence Platform",
        version=settings.app_version,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )
    
    # Add middleware
    # Error handler must be first to catch all errors
    app.add_middleware(ErrorHandlerMiddleware)
    app.add_middleware(LoggingMiddleware)
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=settings.cors_allow_methods,
        allow_headers=settings.cors_allow_headers,
    )
    
    # Include routers
    app.include_router(health.router, prefix="", tags=["health"])
    
    logger.info("Application configured successfully")
    
    return app


# Create application instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        app,
        host=settings.server_host,
        port=settings.server_port,
        workers=settings.workers,
        reload=settings.reload,
        log_level=settings.log_level.lower(),
    )
