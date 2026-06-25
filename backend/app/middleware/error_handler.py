"""Global error handling middleware."""

import json
import logging
from datetime import datetime

from fastapi import Request, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from starlette.types import ASGIApp

from app.shared.exceptions import ApplicationException

logger = logging.getLogger(__name__)


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """Middleware for handling exceptions and converting them to proper HTTP responses."""
    
    def __init__(self, app: ASGIApp) -> None:
        """Initialize middleware.
        
        Args:
            app: ASGI application.
        """
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next):
        """Process request and handle exceptions.
        
        Args:
            request: HTTP request.
            call_next: Next middleware/handler.
            
        Returns:
            HTTP response.
        """
        try:
            return await call_next(request)
        except ApplicationException as e:
            logger.warning(f"Application exception: {e.message}", exc_info=e)
            return JSONResponse(
                status_code=e.status_code,
                content={
                    "error_code": e.error_code,
                    "message": e.message,
                    "details": e.details,
                    "timestamp": datetime.utcnow().isoformat(),
                    "path": str(request.url.path),
                    "method": request.method,
                },
            )
        except Exception as e:
            logger.error(f"Unhandled exception: {e}", exc_info=e)
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "error_code": "INTERNAL_SERVER_ERROR",
                    "message": "An unexpected error occurred",
                    "details": {"type": type(e).__name__},
                    "timestamp": datetime.utcnow().isoformat(),
                    "path": str(request.url.path),
                    "method": request.method,
                },
            )
