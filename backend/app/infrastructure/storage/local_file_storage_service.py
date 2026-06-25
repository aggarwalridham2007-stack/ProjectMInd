"""Local file storage service.

Infrastructure service for managing PDF file storage on local disk.
Handles file validation, streaming writes, and path management.
"""

import hashlib
import logging
from datetime import datetime
from pathlib import Path
from typing import BinaryIO
from uuid import UUID, uuid4

from app.domain.models.paper import StorageLocation
from app.infrastructure.storage.exceptions import (
    EmptyFileError,
    FileTooLargeError,
    InvalidMimeTypeError,
    StorageDeleteError,
    StorageNotFoundError,
    StoragePermissionError,
    StorageWriteError,
)

logger = logging.getLogger(__name__)

# Storage configuration constants
STORAGE_ROOT = Path("backend/storage/papers")
MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024  # 50 MB
ALLOWED_MIME_TYPES = {"application/pdf"}
CHUNK_SIZE = 64 * 1024  # 64 KB
FILE_EXTENSION = ".pdf"


class LocalFileStorageService:
    """Local file storage service for PDFs.
    
    Manages safe storage of PDF files on local disk with validation,
    streaming writes, and organized directory structure.
    
    Responsibilities:
    - Validate file MIME type and size
    - Stream write files to avoid memory exhaustion
    - Organize files by upload date
    - Generate unique filenames
    - Calculate file hashes during write
    - Manage file deletion and existence checks
    """
    
    def __init__(self, root_path: Path | str | None = None):
        """Initialize storage service.
        
        Args:
            root_path: Root storage directory. Defaults to STORAGE_ROOT.
            
        Raises:
            StoragePermissionError: If root path cannot be created or accessed.
        """
        self._root_path = Path(root_path) if root_path else STORAGE_ROOT
        self._file_hashes: dict[str, str] = {}  # Map of stored_filename -> SHA-256 hash
        
        self._initialize_storage()
        logger.info(f"LocalFileStorageService initialized with root: {self._root_path}")
    
    def save(
        self,
        file_stream: BinaryIO,
        original_filename: str,
        mime_type: str,
        file_size: int,
    ) -> StorageLocation:
        """Save PDF file to storage.
        
        Validates file, streams to disk in chunks, calculates SHA-256 hash,
        and returns storage location.
        
        Args:
            file_stream: File-like object to read from.
            original_filename: Original filename from upload.
            mime_type: MIME type of the file.
            file_size: Total file size in bytes.
            
        Returns:
            StorageLocation domain object.
            
        Raises:
            InvalidMimeTypeError: If MIME type is not allowed.
            EmptyFileError: If file is empty.
            FileTooLargeError: If file exceeds size limit.
            StoragePermissionError: If storage directory cannot be created.
            StorageWriteError: If file write fails.
        """
        # Validate inputs
        self._validate_file(
            original_filename=original_filename,
            mime_type=mime_type,
            file_size=file_size,
        )
        
        # Generate storage filename and path
        stored_filename = self._generate_filename()
        storage_path = self._get_storage_path()
        file_directory = self._root_path / storage_path
        file_path = file_directory / stored_filename
        
        logger.info(
            f"Starting file storage: original={original_filename}, "
            f"stored={stored_filename}, size={file_size}"
        )
        
        try:
            # Create directory structure
            self._ensure_directory_exists(file_directory)
            
            # Write file and calculate hash
            bytes_written, file_hash = self._write_file_chunked(
                file_stream=file_stream,
                file_path=file_path,
            )
            
            # Verify bytes written matches declared size
            if bytes_written != file_size:
                logger.warning(
                    f"Bytes written mismatch: declared={file_size}, "
                    f"written={bytes_written}, file={stored_filename}"
                )
                try:
                    file_path.unlink()
                except Exception as cleanup_error:
                    logger.warning(f"Failed to clean up partial file: {cleanup_error}")
                raise StorageWriteError(
                    f"File size mismatch: expected {file_size} bytes, "
                    f"wrote {bytes_written} bytes"
                )
            
            # Store hash for future duplicate detection
            self._file_hashes[stored_filename] = file_hash
            
            logger.info(
                f"File storage completed: {stored_filename}, "
                f"hash={file_hash[:16]}..., size={bytes_written}"
            )
            
            # Return storage location
            return StorageLocation(
                stored_filename=stored_filename,
                storage_path=storage_path,
            )
        except StorageError:
            # Re-raise storage-specific errors
            raise
        except Exception as e:
            logger.error(f"Unexpected error during file storage: {e}", exc_info=e)
            # Clean up partial file
            try:
                file_path.unlink(missing_ok=True)
            except Exception as cleanup_error:
                logger.warning(f"Failed to clean up after error: {cleanup_error}")
            raise StorageWriteError(f"File storage failed: {str(e)[:100]}")
    
    def delete(self, storage_location: StorageLocation) -> bool:
        """Delete file from storage.
        
        Args:
            storage_location: StorageLocation object identifying file.
            
        Returns:
            True if file was deleted, False if not found.
            
        Raises:
            StorageDeleteError: If deletion fails.
        """
        file_path = self._root_path / storage_location.full_path
        
        logger.info(f"Deleting file: {storage_location.stored_filename}")
        
        if not file_path.exists():
            logger.warning(f"File not found for deletion: {file_path}")
            return False
        
        try:
            file_path.unlink()
            
            # Remove hash record
            self._file_hashes.pop(storage_location.stored_filename, None)
            
            # Clean up empty directories
            self._cleanup_empty_directories(file_path.parent)
            
            logger.info(f"File deleted: {storage_location.stored_filename}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete file: {e}", exc_info=e)
            raise StorageDeleteError(f"Failed to delete file: {str(e)[:100]}")
    
    def exists(self, storage_location: StorageLocation) -> bool:
        """Check if file exists in storage.
        
        Args:
            storage_location: StorageLocation object identifying file.
            
        Returns:
            True if file exists, False otherwise.
        """
        file_path = self._root_path / storage_location.full_path
        exists = file_path.exists() and file_path.is_file()
        
        logger.debug(f"File exists check: {storage_location.stored_filename} -> {exists}")
        
        return exists
    
    def get_file_hash(self, stored_filename: str) -> str | None:
        """Get SHA-256 hash of stored file if available.
        
        Hash is calculated during save operation.
        
        Args:
            stored_filename: The stored filename.
            
        Returns:
            SHA-256 hash hex string, or None if not found.
        """
        return self._file_hashes.get(stored_filename)
    
    # Private helper methods
    
    def _initialize_storage(self) -> None:
        """Initialize storage directory.
        
        Raises:
            StoragePermissionError: If directory cannot be created or is not writable.
        """
        try:
            self._root_path.mkdir(parents=True, exist_ok=True)
            
            # Verify writable by creating and removing a test file
            test_file = self._root_path / ".write_test"
            test_file.write_text("")
            test_file.unlink()
        except PermissionError as e:
            logger.error(f"Storage permission denied: {e}")
            raise StoragePermissionError(
                f"Cannot access storage directory: Permission denied"
            )
        except OSError as e:
            logger.error(f"Storage initialization failed: {e}")
            raise StoragePermissionError(
                f"Cannot initialize storage directory: {str(e)[:100]}"
            )
    
    def _validate_file(
        self,
        original_filename: str,
        mime_type: str,
        file_size: int,
    ) -> None:
        """Validate file before storage.
        
        Args:
            original_filename: Original filename from upload.
            mime_type: MIME type of the file.
            file_size: Total file size in bytes.
            
        Raises:
            InvalidMimeTypeError: If MIME type not allowed.
            EmptyFileError: If file is empty.
            FileTooLargeError: If file exceeds limit.
        """
        # Validate MIME type
        if mime_type not in ALLOWED_MIME_TYPES:
            logger.warning(f"Invalid MIME type: {mime_type} for {original_filename}")
            raise InvalidMimeTypeError(
                f"MIME type '{mime_type}' not allowed. Only PDF files are accepted."
            )
        
        # Validate file size - empty
        if file_size <= 0:
            logger.warning(f"Empty file rejected: {original_filename}")
            raise EmptyFileError("File is empty and cannot be stored")
        
        # Validate file size - too large
        if file_size > MAX_FILE_SIZE_BYTES:
            size_mb = file_size / 1024 / 1024
            max_mb = MAX_FILE_SIZE_BYTES / 1024 / 1024
            logger.warning(
                f"File too large: {original_filename} "
                f"({size_mb:.2f} MB > {max_mb:.0f} MB)"
            )
            raise FileTooLargeError(
                f"File size {size_mb:.2f} MB exceeds maximum of {max_mb:.0f} MB"
            )
    
    def _generate_filename(self) -> str:
        """Generate unique storage filename.
        
        Returns:
            Filename with UUID and PDF extension.
        """
        return f"{uuid4()}{FILE_EXTENSION}"
    
    def _get_storage_path(self) -> str:
        """Get date-based storage path.
        
        Returns:
            Path in format YYYY/MM/DD.
        """
        now = datetime.utcnow()
        return now.strftime("%Y/%m/%d")
    
    def _ensure_directory_exists(self, directory: Path) -> None:
        """Ensure directory exists with proper permissions.
        
        Args:
            directory: Directory path to create.
            
        Raises:
            StoragePermissionError: If directory cannot be created.
        """
        try:
            directory.mkdir(parents=True, exist_ok=True)
        except PermissionError as e:
            logger.error(f"Permission denied creating directory: {e}")
            raise StoragePermissionError(
                "Cannot create storage directory: Permission denied"
            )
        except OSError as e:
            logger.error(f"Failed to create directory: {e}")
            raise StoragePermissionError(
                f"Cannot create directory: {str(e)[:100]}"
            )
    
    def _write_file_chunked(
        self,
        file_stream: BinaryIO,
        file_path: Path,
    ) -> tuple[int, str]:
        """Write file in chunks and calculate SHA-256 hash.
        
        Streams file from input to disk without loading entire file in memory.
        Calculates SHA-256 hash during write.
        
        Args:
            file_stream: Input file stream.
            file_path: Target file path.
            
        Returns:
            Tuple of (bytes_written, sha256_hash_hex).
            
        Raises:
            StorageWriteError: If write operation fails.
        """
        sha256_hash = hashlib.sha256()
        bytes_written = 0
        
        try:
            with open(file_path, "wb") as dest_file:
                while True:
                    chunk = file_stream.read(CHUNK_SIZE)
                    if not chunk:
                        break
                    
                    dest_file.write(chunk)
                    sha256_hash.update(chunk)
                    bytes_written += len(chunk)
            
            return bytes_written, sha256_hash.hexdigest()
        except IOError as e:
            logger.error(f"IO error writing file: {e}")
            raise StorageWriteError(f"Failed to write file: {str(e)[:100]}")
        except Exception as e:
            logger.error(f"Unexpected error writing file: {e}", exc_info=e)
            raise StorageWriteError(f"File write failed: {str(e)[:100]}")
    
    def _cleanup_empty_directories(self, directory: Path) -> None:
        """Remove empty parent directories up to storage root.
        
        Args:
            directory: Starting directory for cleanup.
        """
        try:
            while directory != self._root_path and not list(directory.iterdir()):
                directory.rmdir()
                directory = directory.parent
        except OSError as e:
            logger.debug(f"Could not clean up empty directory: {e}")
