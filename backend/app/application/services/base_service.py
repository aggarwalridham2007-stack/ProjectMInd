"""Base application service."""

import logging
from abc import ABC
from typing import Generic, TypeVar

T = TypeVar("T")
ID = TypeVar("ID")


class BaseApplicationService(ABC, Generic[T, ID]):
    """Base application service for common service operations."""
    
    def __init__(self) -> None:
        """Initialize service."""
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def _log_info(self, message: str) -> None:
        """Log info message.
        
        Args:
            message: Message to log.
        """
        self.logger.info(message)
    
    def _log_error(self, message: str, exc: Exception | None = None) -> None:
        """Log error message.
        
        Args:
            message: Message to log.
            exc: Optional exception.
        """
        if exc:
            self.logger.error(message, exc_info=exc)
        else:
            self.logger.error(message)
    
    def _log_warning(self, message: str) -> None:
        """Log warning message.
        
        Args:
            message: Message to log.
        """
        self.logger.warning(message)
