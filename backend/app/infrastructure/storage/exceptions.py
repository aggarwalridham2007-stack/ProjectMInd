"""Custom exceptions for file storage service."""


class StorageError(Exception):
    """Base exception for storage operations."""
    
    pass


class InvalidMimeTypeError(StorageError):
    """Raised when file MIME type is not allowed."""
    
    pass


class FileTooLargeError(StorageError):
    """Raised when file size exceeds maximum limit."""
    
    pass


class EmptyFileError(StorageError):
    """Raised when file is empty."""
    
    pass


class StoragePermissionError(StorageError):
    """Raised when storage directory cannot be accessed or created."""
    
    pass


class StorageWriteError(StorageError):
    """Raised when file write operation fails."""
    
    pass


class StorageDeleteError(StorageError):
    """Raised when file deletion fails."""
    
    pass


class StorageNotFoundError(StorageError):
    """Raised when stored file is not found."""
    
    pass
