"""File upload utilities and helpers."""
import tempfile
from pathlib import Path
from typing import BinaryIO

from fastapi import UploadFile, HTTPException


class UploadHandler:
    """Handles file uploads with validation and temporary storage."""

    ALLOWED_EXTENSIONS = {'.mp4', '.mov', '.avi', '.mkv', '.webm'}
    MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB

    @staticmethod
    def validate_file_extension(filename: str) -> bool:
        """Validate file extension.

        Args:
            filename: Name of uploaded file

        Returns:
            True if extension is allowed
        """
        if not filename:
            return False

        extension = Path(filename).suffix.lower()
        return extension in UploadHandler.ALLOWED_EXTENSIONS

    @staticmethod
    def validate_file_size(file_size: int) -> bool:
        """Validate file size.

        Args:
            file_size: Size of file in bytes

        Returns:
            True if size is acceptable
        """
        return 0 < file_size <= UploadHandler.MAX_FILE_SIZE

    @staticmethod
    async def save_temp_file(upload_file: UploadFile) -> str:
        """Save uploaded file to temporary location.

        Args:
            upload_file: FastAPI UploadFile object

        Returns:
            Path to temporary file

        Raises:
            HTTPException: If file validation fails
        """
        # Validate filename
        if not upload_file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")

        if not UploadHandler.validate_file_extension(upload_file.filename):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed: {', '.join(UploadHandler.ALLOWED_EXTENSIONS)}"
            )

        # Read file content
        file_content = await upload_file.read()

        # Validate file size
        if not UploadHandler.validate_file_size(len(file_content)):
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size: {UploadHandler.MAX_FILE_SIZE // (1024 * 1024)}MB"
            )

        # Save to temporary file
        suffix = Path(upload_file.filename).suffix
        temp_file = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)

        try:
            temp_file.write(file_content)
            temp_file.flush()
            return temp_file.name
        finally:
            temp_file.close()

    @staticmethod
    def cleanup_temp_file(file_path: str) -> bool:
        """Clean up temporary file.

        Args:
            file_path: Path to temporary file

        Returns:
            True if successful
        """
        try:
            Path(file_path).unlink(missing_ok=True)
            return True
        except Exception:
            return False

    @staticmethod
    def get_file_stream(file_path: str) -> BinaryIO:
        """Get file stream for uploading.

        Args:
            file_path: Path to file

        Returns:
            Binary file stream
        """
        return open(file_path, 'rb')


def get_upload_handler() -> UploadHandler:
    """Get upload handler instance."""
    return UploadHandler()