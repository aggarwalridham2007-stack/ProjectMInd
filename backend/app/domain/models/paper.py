"""Paper aggregate root domain model.

Pure domain model with no infrastructure dependencies.
Follows Domain-Driven Design principles.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


@dataclass(frozen=True)
class PaperMetadata:
    """Immutable paper metadata value object.
    
    Encapsulates metadata that doesn't change after upload.
    """
    
    original_filename: str
    mime_type: str
    file_size: int
    
    def __post_init__(self) -> None:
        """Validate metadata values.
        
        Raises:
            ValueError: If validation fails.
        """
        if not self.original_filename:
            raise ValueError("original_filename cannot be empty")
        
        if len(self.original_filename) > 500:
            raise ValueError("original_filename exceeds maximum length of 500 characters")
        
        if not self.mime_type:
            raise ValueError("mime_type cannot be empty")
        
        if len(self.mime_type) > 100:
            raise ValueError("mime_type exceeds maximum length of 100 characters")
        
        if self.file_size <= 0:
            raise ValueError("file_size must be greater than 0")
        
        if self.file_size > 50 * 1024 * 1024:  # 50 MB
            raise ValueError(
                f"file_size exceeds maximum of 50 MB. Got {self.file_size / 1024 / 1024:.2f} MB"
            )


@dataclass(frozen=True)
class StorageLocation:
    """Immutable storage location value object.
    
    Encapsulates where and how file is stored.
    """
    
    stored_filename: str
    storage_path: str  # Date-based path: YYYY/MM/DD
    
    def __post_init__(self) -> None:
        """Validate storage location.
        
        Raises:
            ValueError: If validation fails.
        """
        if not self.stored_filename:
            raise ValueError("stored_filename cannot be empty")
        
        if len(self.stored_filename) > 500:
            raise ValueError("stored_filename exceeds maximum length of 500 characters")
        
        if not self.storage_path:
            raise ValueError("storage_path cannot be empty")
    
    @property
    def full_path(self) -> str:
        """Get full storage path.
        
        Returns:
            Full path including filename.
        """
        return f"{self.storage_path}/{self.stored_filename}"


@dataclass
class Paper:
    """Paper aggregate root.
    
    Represents a research paper in the domain.
    Manages paper identity, metadata, and lifecycle.
    
    This is a pure domain model with no infrastructure dependencies.
    """
    
    # Identity
    id: UUID = field(default_factory=uuid4)
    
    # Metadata
    metadata: PaperMetadata = field()
    
    # Storage
    storage_location: Optional[StorageLocation] = field(default=None)
    
    # Lifecycle
    uploaded_at: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self) -> None:
        """Validate paper state after initialization.
        
        Raises:
            ValueError: If validation fails.
        """
        if not isinstance(self.id, UUID):
            raise ValueError("id must be a UUID")
        
        if not isinstance(self.metadata, PaperMetadata):
            raise ValueError("metadata must be PaperMetadata instance")
        
        if self.storage_location is not None and not isinstance(
            self.storage_location, StorageLocation
        ):
            raise ValueError("storage_location must be StorageLocation instance or None")
        
        if not isinstance(self.uploaded_at, datetime):
            raise ValueError("uploaded_at must be datetime instance")
    
    def set_storage_location(self, storage_location: StorageLocation) -> "Paper":
        """Set storage location after file is saved.
        
        Returns new Paper instance with storage location set.
        
        Args:
            storage_location: Storage location value object.
            
        Returns:
            New Paper instance with storage location.
            
        Raises:
            ValueError: If storage location already set.
        """
        if self.storage_location is not None:
            raise ValueError("Storage location is already set")
        
        return Paper(
            id=self.id,
            metadata=self.metadata,
            storage_location=storage_location,
            uploaded_at=self.uploaded_at,
        )
    
    @property
    def is_stored(self) -> bool:
        """Check if paper has storage location set.
        
        Returns:
            True if storage location is set, False otherwise.
        """
        return self.storage_location is not None
    
    @property
    def original_filename(self) -> str:
        """Get original filename.
        
        Returns:
            Original filename from metadata.
        """
        return self.metadata.original_filename
    
    @property
    def stored_filename(self) -> Optional[str]:
        """Get stored filename.
        
        Returns:
            Stored filename or None if not yet stored.
        """
        return self.storage_location.stored_filename if self.storage_location else None
    
    @property
    def mime_type(self) -> str:
        """Get MIME type.
        
        Returns:
            MIME type from metadata.
        """
        return self.metadata.mime_type
    
    @property
    def file_size(self) -> int:
        """Get file size in bytes.
        
        Returns:
            File size from metadata.
        """
        return self.metadata.file_size
    
    def __eq__(self, other: object) -> bool:
        """Check equality based on ID.
        
        Two papers are equal if they have the same ID.
        
        Args:
            other: Object to compare.
            
        Returns:
            True if IDs match, False otherwise.
        """
        if not isinstance(other, Paper):
            return False
        return self.id == other.id
    
    def __hash__(self) -> int:
        """Get hash based on ID.
        
        Returns:
            Hash of paper ID.
        """
        return hash(self.id)
    
    def __repr__(self) -> str:
        """Get string representation.
        
        Returns:
            String representation of paper.
        """
        return (
            f"Paper(id={self.id}, original_filename={self.original_filename}, "
            f"size={self.file_size}, stored={self.is_stored}, "
            f"uploaded_at={self.uploaded_at})"
        )
