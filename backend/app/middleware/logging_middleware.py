"""Request/response logging middleware."""

import logging
from time import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging HTTP requests and responses."""
    
    def __init__(self, app: ASGIApp) -> None:
        """Initialize middleware.
        
        Args:
            app: ASGI application.
        """
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next):
        """Log request and response.
        
        Args:
            request: HTTP request.
            call_next: Next middleware/handler.
            
        Returns:
            HTTP response.
        """
        # Skip logging for health checks
        if request.url.path == "/health":
            return await call_next(request)
        
        start_time = time()
        
        logger.info(
            f"HTTP Request: {request.method} {request.url.path}",
            extra={
                "method": request.method,
                "path": request.url.path,
                "client": request.client.host if request.client else "unknown",
            },
        )
        
        response = await call_next(request)
        
        process_time = time() - start_time
        
        logger.info(
            f"HTTP Response: {request.method} {request.url.path} - {response.status_code}",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": round(process_time * 1000, 2),
                "client": request.client.host if request.client else "unknown",
            },
        )
        
        return response
