"""Custom application exceptions."""

from typing import Any, Optional


class ApplicationException(Exception):
    """Base application exception."""
    
    def __init__(
        self,
        message: str,
        error_code: str = "INTERNAL_SERVER_ERROR",
        status_code: int = 500,
        details: Optional[dict[str, Any]] = None,
    ):
        """Initialize exception.
        
        Args:
            message: Error message.
            error_code: Application error code.
            status_code: HTTP status code.
            details: Additional error details.
        """
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationException(ApplicationException):
    """Raised when validation fails."""
    
    def __init__(self, message: str, details: Optional[dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            status_code=422,
            details=details,
        )


class NotFoundException(ApplicationException):
    """Raised when resource is not found."""
    
    def __init__(self, message: str, details: Optional[dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="NOT_FOUND",
            status_code=404,
            details=details,
        )


class UnauthorizedException(ApplicationException):
    """Raised when authentication fails."""
    
    def __init__(self, message: str = "Unauthorized", details: Optional[dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="UNAUTHORIZED",
            status_code=401,
            details=details,
        )


class ForbiddenException(ApplicationException):
    """Raised when authorization fails."""
    
    def __init__(self, message: str = "Forbidden", details: Optional[dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="FORBIDDEN",
            status_code=403,
            details=details,
        )


class ConflictException(ApplicationException):
    """Raised when resource conflict occurs."""
    
    def __init__(self, message: str, details: Optional[dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="CONFLICT",
            status_code=409,
            details=details,
        )


class ServiceUnavailableException(ApplicationException):
    """Raised when service is unavailable."""
    
    def __init__(self, message: str = "Service unavailable", details: Optional[dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="SERVICE_UNAVAILABLE",
            status_code=503,
            details=details,
        )
