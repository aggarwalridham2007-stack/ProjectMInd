"""Unit tests for LocalFileStorageService."""

import hashlib
import logging
from io import BytesIO
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

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
from app.infrastructure.storage.local_file_storage_service import (
    ALLOWED_MIME_TYPES,
    MAX_FILE_SIZE_BYTES,
    LocalFileStorageService,
)


@pytest.fixture
def temp_storage_dir(tmp_path):
    """Create temporary storage directory for tests."""
    storage_dir = tmp_path / "storage" / "papers"
    storage_dir.mkdir(parents=True, exist_ok=True)
    return storage_dir


@pytest.fixture
def storage_service(temp_storage_dir):
    """Create storage service with temp directory."""
    return LocalFileStorageService(root_path=temp_storage_dir)


@pytest.fixture
def valid_pdf_stream():
    """Create valid PDF file stream."""
    content = b"%PDF-1.4\nTest PDF content"
    return BytesIO(content)


# Successful Upload Tests


class TestSuccessfulUpload:
    """Tests for successful file uploads."""
    
    def test_save_valid_pdf_file(self, storage_service, valid_pdf_stream):
        """Test saving a valid PDF file.
        
        Args:
            storage_service: Storage service instance.
            valid_pdf_stream: Valid PDF file stream.
        """
        # Arrange
        original_filename = "research_paper.pdf"
        mime_type = "application/pdf"
        file_size = len(b"%PDF-1.4\nTest PDF content")
        
        # Act
        storage_location = storage_service.save(
            file_stream=valid_pdf_stream,
            original_filename=original_filename,
            mime_type=mime_type,
            file_size=file_size,
        )
        
        # Assert
        assert isinstance(storage_location, StorageLocation)
        assert storage_location.stored_filename.endswith(".pdf")
        assert storage_location.storage_path is not None
        assert "/" in storage_location.storage_path  # YYYY/MM/DD format
    
    def test_save_file_creates_date_directory(self, storage_service, valid_pdf_stream):
        """Test that save creates date-based directory structure.
        
        Args:
            storage_service: Storage service instance.
            valid_pdf_stream: Valid PDF file stream.
        """
        # Arrange
        original_filename = "paper.pdf"
        mime_type = "application/pdf"
        file_size = len(b"%PDF-1.4\nTest PDF content")
        
        # Act
        storage_location = storage_service.save(
            file_stream=valid_pdf_stream,
            original_filename=original_filename,
            mime_type=mime_type,
            file_size=file_size,
        )
        
        # Assert
        file_path = storage_service._root_path / storage_location.full_path
        assert file_path.exists()
        assert file_path.is_file()
    
    def test_save_file_preserves_extension(self, storage_service, valid_pdf_stream):
        """Test that saved file has .pdf extension.
        
        Args:
            storage_service: Storage service instance.
            valid_pdf_stream: Valid PDF file stream.
        """
        # Arrange
        original_filename = "document.pdf"
        mime_type = "application/pdf"
        file_size = len(b"%PDF-1.4\nTest PDF content")
        
        # Act
        storage_location = storage_service.save(
            file_stream=valid_pdf_stream,
            original_filename=original_filename,
            mime_type=mime_type,
            file_size=file_size,
        )
        
        # Assert
        assert storage_location.stored_filename.endswith(".pdf")
    
    def test_save_returns_storage_location_object(self, storage_service, valid_pdf_stream):
        """Test that save returns StorageLocation domain object.
        
        Args:
            storage_service: Storage service instance.
            valid_pdf_stream: Valid PDF file stream.
        """
        # Arrange
        original_filename = "paper.pdf"
        mime_type = "application/pdf"
        file_size = len(b"%PDF-1.4\nTest PDF content")
        
        # Act
        result = storage_service.save(
            file_stream=valid_pdf_stream,
            original_filename=original_filename,
            mime_type=mime_type,
            file_size=file_size,
        )
        
        # Assert
        assert isinstance(result, StorageLocation)
        assert not isinstance(result, dict)
        assert not isinstance(result, str)


# Validation Tests


class TestValidation:
    """Tests for file validation."""
    
    def test_reject_invalid_mime_type(self, storage_service):
        """Test that non-PDF MIME types are rejected.
        
        Args:
            storage_service: Storage service instance.
        """
        # Arrange
        file_stream = BytesIO(b"Not PDF")
        original_filename = "document.txt"
        mime_type = "text/plain"
        file_size = 7
        
        # Act & Assert
        with pytest.raises(InvalidMimeTypeError):
            storage_service.save(
                file_stream=file_stream,
                original_filename=original_filename,
                mime_type=mime_type,
                file_size=file_size,
            )
    
    def test_reject_empty_file(self, storage_service):
        """Test that empty files are rejected.
        
        Args:
            storage_service: Storage service instance.
        """
        # Arrange
        file_stream = BytesIO(b"")
        original_filename = "empty.pdf"
        mime_type = "application/pdf"
        file_size = 0
        
        # Act & Assert
        with pytest.raises(EmptyFileError):
            storage_service.save(
                file_stream=file_stream,
                original_filename=original_filename,
                mime_type=mime_type,
                file_size=file_size,
            )
    
    def test_reject_file_exceeding_size_limit(self, storage_service):
        """Test that files exceeding 50MB are rejected.
        
        Args:
            storage_service: Storage service instance.
        """
        # Arrange
        file_stream = BytesIO(b"x" * 100)  # Actual content
        original_filename = "huge.pdf"
        mime_type = "application/pdf"
        file_size = MAX_FILE_SIZE_BYTES + 1  # Just over limit
        
        # Act & Assert
        with pytest.raises(FileTooLargeError):
            storage_service.save(
                file_stream=file_stream,
                original_filename=original_filename,
                mime_type=mime_type,
                file_size=file_size,
            )
    
    def test_accept_file_at_max_size_limit(self, storage_service):
        """Test that files exactly at 50MB limit are accepted.
        
        Args:
            storage_service: Storage service instance.
        """
        # Arrange
        content = b"x" * MAX_FILE_SIZE_BYTES
        file_stream = BytesIO(content)
        original_filename = "maxsize.pdf"
        mime_type = "application/pdf"
        file_size = MAX_FILE_SIZE_BYTES
        
        # Act
        storage_location = storage_service.save(
            file_stream=file_stream,
            original_filename=original_filename,
            mime_type=mime_type,
            file_size=file_size,
        )
        
        # Assert
        assert storage_location is not None


# Hash Generation Tests


class TestHashGeneration:
    """Tests for SHA-256 hash calculation."""
    
    def test_hash_calculated_during_save(self, storage_service, valid_pdf_stream):
        """Test that SHA-256 hash is calculated during save.
        
        Args:
            storage_service: Storage service instance.
            valid_pdf_stream: Valid PDF file stream.
        """
        # Arrange
        content = b"%PDF-1.4\nTest PDF content"
        file_stream = BytesIO(content)
        expected_hash = hashlib.sha256(content).hexdigest()
        
        # Act
        storage_location = storage_service.save(
            file_stream=file_stream,
            original_filename="paper.pdf",
            mime_type="application/pdf",
            file_size=len(content),
        )
        
        # Assert
        actual_hash = storage_service.get_file_hash(storage_location.stored_filename)
        assert actual_hash == expected_hash
    
    def test_get_file_hash_returns_none_for_nonexistent_file(self, storage_service):
        """Test that get_file_hash returns None for unknown files.
        
        Args:
            storage_service: Storage service instance.
        """
        # Act
        hash_value = storage_service.get_file_hash("nonexistent.pdf")
        
        # Assert
        assert hash_value is None


# Delete Tests


class TestDelete:
    """Tests for file deletion."""
    
    def test_delete_existing_file(self, storage_service, valid_pdf_stream):
        """Test deleting an existing file.
        
        Args:
            storage_service: Storage service instance.
            valid_pdf_stream: Valid PDF file stream.
        """
        # Arrange
        storage_location = storage_service.save(
            file_stream=valid_pdf_stream,
            original_filename="paper.pdf",
            mime_type="application/pdf",
            file_size=len(b"%PDF-1.4\nTest PDF content"),
        )
        
        # Act
        deleted = storage_service.delete(storage_location)
        
        # Assert
        assert deleted is True
        assert not storage_service.exists(storage_location)
    
    def test_delete_nonexistent_file_returns_false(self, storage_service):
        """Test deleting a file that doesn't exist.
        
        Args:
            storage_service: Storage service instance.
        """
        # Arrange
        storage_location = StorageLocation(
            stored_filename="nonexistent.pdf",
            storage_path="2026/06/25",
        )
        
        # Act
        deleted = storage_service.delete(storage_location)
        
        # Assert
        assert deleted is False
    
    def test_delete_removes_empty_directories(self, storage_service, valid_pdf_stream):
        """Test that delete cleans up empty directories.
        
        Args:
            storage_service: Storage service instance.
            valid_pdf_stream: Valid PDF file stream.
        """
        # Arrange
        storage_location = storage_service.save(
            file_stream=valid_pdf_stream,
            original_filename="paper.pdf",
            mime_type="application/pdf",
            file_size=len(b"%PDF-1.4\nTest PDF content"),
        )
        file_path = storage_service._root_path / storage_location.full_path
        directory = file_path.parent
        
        # Act
        storage_service.delete(storage_location)
        
        # Assert - directory should be removed if empty
        assert not directory.exists()


# Exists Tests


class TestExists:
    """Tests for file existence checks."""
    
    def test_exists_returns_true_for_saved_file(self, storage_service, valid_pdf_stream):
        """Test that exists returns True for saved file.
        
        Args:
            storage_service: Storage service instance.
            valid_pdf_stream: Valid PDF file stream.
        """
        # Arrange
        storage_location = storage_service.save(
            file_stream=valid_pdf_stream,
            original_filename="paper.pdf",
            mime_type="application/pdf",
            file_size=len(b"%PDF-1.4\nTest PDF content"),
        )
        
        # Act
        exists = storage_service.exists(storage_location)
        
        # Assert
        assert exists is True
    
    def test_exists_returns_false_for_nonexistent_file(self, storage_service):
        """Test that exists returns False for nonexistent file.
        
        Args:
            storage_service: Storage service instance.
        """
        # Arrange
        storage_location = StorageLocation(
            stored_filename="nonexistent.pdf",
            storage_path="2026/06/25",
        )
        
        # Act
        exists = storage_service.exists(storage_location)
        
        # Assert
        assert exists is False
    
    def test_exists_returns_false_after_deletion(self, storage_service, valid_pdf_stream):
        """Test that exists returns False after file deletion.
        
        Args:
            storage_service: Storage service instance.
            valid_pdf_stream: Valid PDF file stream.
        """
        # Arrange
        storage_location = storage_service.save(
            file_stream=valid_pdf_stream,
            original_filename="paper.pdf",
            mime_type="application/pdf",
            file_size=len(b"%PDF-1.4\nTest PDF content"),
        )
        storage_service.delete(storage_location)
        
        # Act
        exists = storage_service.exists(storage_location)
        
        # Assert
        assert exists is False


# Permission and Error Tests


class TestErrorHandling:
    """Tests for error handling and edge cases."""
    
    def test_permission_error_on_init_raises_storage_permission_error(self, tmp_path):
        """Test that permission errors during init raise StoragePermissionError.
        
        Args:
            tmp_path: Temporary directory.
        """
        # Arrange
        storage_dir = tmp_path / "readonly"
        storage_dir.mkdir()
        storage_dir.chmod(0o444)  # Read-only
        
        try:
            # Act & Assert
            with pytest.raises(StoragePermissionError):
                LocalFileStorageService(root_path=storage_dir / "papers")
        finally:
            # Cleanup
            storage_dir.chmod(0o755)
    
    def test_write_error_raises_storage_write_error(self, temp_storage_dir):
        """Test that write errors raise StorageWriteError.
        
        Args:
            temp_storage_dir: Temporary storage directory.
        """
        # Arrange
        storage_service = LocalFileStorageService(root_path=temp_storage_dir)
        
        # Mock the _write_file_chunked to raise IOError
        with patch.object(
            storage_service,
            "_write_file_chunked",
            side_effect=IOError("Disk full"),
        ):
            file_stream = BytesIO(b"test")
            
            # Act & Assert
            with pytest.raises(StorageWriteError):
                storage_service.save(
                    file_stream=file_stream,
                    original_filename="paper.pdf",
                    mime_type="application/pdf",
                    file_size=4,
                )
    
    def test_delete_error_raises_storage_delete_error(self, storage_service, valid_pdf_stream):
        """Test that delete errors raise StorageDeleteError.
        
        Args:
            storage_service: Storage service instance.
            valid_pdf_stream: Valid PDF file stream.
        """
        # Arrange
        storage_location = storage_service.save(
            file_stream=valid_pdf_stream,
            original_filename="paper.pdf",
            mime_type="application/pdf",
            file_size=len(b"%PDF-1.4\nTest PDF content"),
        )
        
        # Mock unlink to raise PermissionError
        with patch.object(Path, "unlink", side_effect=PermissionError("Permission denied")):
            # Act & Assert
            with pytest.raises(StorageDeleteError):
                storage_service.delete(storage_location)
    
    def test_bytes_written_mismatch_raises_error(self, temp_storage_dir):
        """Test that size mismatch between declared and written bytes raises error.
        
        Args:
            temp_storage_dir: Temporary storage directory.
        """
        # Arrange
        storage_service = LocalFileStorageService(root_path=temp_storage_dir)
        file_stream = BytesIO(b"short")
        
        # Act & Assert - declare larger size than actual
        with pytest.raises(StorageWriteError):
            storage_service.save(
                file_stream=file_stream,
                original_filename="paper.pdf",
                mime_type="application/pdf",
                file_size=1000,  # More than actual 5 bytes
            )


# Chunked Writing Tests


class TestChunkedWriting:
    """Tests for chunked file writing."""
    
    def test_large_file_streamed_correctly(self, storage_service):
        """Test that large files are written correctly in chunks.
        
        Args:
            storage_service: Storage service instance.
        """
        # Arrange - Create a file larger than chunk size
        chunk_size = 64 * 1024  # 64 KB
        file_content = b"x" * (chunk_size * 3 + 1000)
        file_stream = BytesIO(file_content)
        
        # Act
        storage_location = storage_service.save(
            file_stream=file_stream,
            original_filename="large.pdf",
            mime_type="application/pdf",
            file_size=len(file_content),
        )
        
        # Assert
        file_path = storage_service._root_path / storage_location.full_path
        assert file_path.exists()
        assert file_path.stat().st_size == len(file_content)
        
        # Verify hash
        expected_hash = hashlib.sha256(file_content).hexdigest()
        actual_hash = storage_service.get_file_hash(storage_location.stored_filename)
        assert actual_hash == expected_hash
