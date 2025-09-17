"""Local media operations for video uploads and playback."""
import logging
import os
import shutil
import uuid
from datetime import datetime
from pathlib import Path
from typing import BinaryIO, Optional

from fastapi import HTTPException

from app.config import settings

logger = logging.getLogger(__name__)


class LocalMediaManager:
    """Handles local file operations for video media."""

    def __init__(self):
        self.base_path = Path(settings.media_base_path)
        self.videos_path = self.base_path / "videos"
        self._ensure_directories()

    def _ensure_directories(self):
        """Ensure media directories exist."""
        try:
            self.videos_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"✅ Media directories ready: {self.videos_path}")
        except Exception as e:
            logger.error(f"❌ Failed to create media directories: {e}")
            raise HTTPException(
                status_code=500,
                detail="Failed to initialize media storage"
            )

    def generate_file_path(self, user_id: str, file_extension: str = "mp4") -> str:
        """Generate unique file path for video upload.

        Format: videos/YYYYMMDD/user_id/uuid.mp4
        """
        # Use UUID for uniqueness and user_id for organization
        unique_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().strftime("%Y%m%d")

        # Create relative path from media base
        relative_path = f"videos/{timestamp}/{user_id}/{unique_id}.{file_extension}"

        logger.info(f"Generated file path: {relative_path}")
        return relative_path

    def get_absolute_path(self, relative_path: str) -> Path:
        """Convert relative media path to absolute path."""
        return self.base_path / relative_path

    def get_url_path(self, relative_path: str) -> str:
        """Convert relative path to URL path for serving."""
        # This will be served at /media/{relative_path}
        return f"/media/{relative_path}"

    async def save_video(
        self,
        file_data: BinaryIO,
        relative_path: str,
        content_type: str = "video/mp4"
    ) -> dict:
        """Save video file to local storage.

        Args:
            file_data: File-like object with video data
            relative_path: Relative path from media base
            content_type: MIME type of the file

        Returns:
            Dict with upload details
        """
        try:
            absolute_path = self.get_absolute_path(relative_path)

            # Ensure parent directory exists
            absolute_path.parent.mkdir(parents=True, exist_ok=True)

            # Save file
            with open(absolute_path, "wb") as f:
                file_data.seek(0)  # Reset to beginning
                shutil.copyfileobj(file_data, f)

            # Get file info
            file_stat = absolute_path.stat()

            upload_info = {
                'path': relative_path,
                'absolute_path': str(absolute_path),
                'size': file_stat.st_size,
                'created_at': datetime.fromtimestamp(file_stat.st_ctime),
                'content_type': content_type,
                'url': self.get_url_path(relative_path)
            }

            logger.info(f"✅ Saved video to local storage: {relative_path} ({upload_info['size']} bytes)")
            return upload_info

        except Exception as e:
            logger.error(f"❌ Local save failed: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Video save failed: {str(e)}"
            )

    def delete_video(self, relative_path: str) -> bool:
        """Delete video from local storage.

        Args:
            relative_path: Relative path from media base

        Returns:
            True if successful
        """
        try:
            absolute_path = self.get_absolute_path(relative_path)

            if absolute_path.exists():
                absolute_path.unlink()
                logger.info(f"✅ Deleted video from local storage: {relative_path}")

                # Try to remove empty parent directories
                try:
                    absolute_path.parent.rmdir()  # Only removes if empty
                except OSError:
                    pass  # Directory not empty, that's fine

                return True
            else:
                logger.warning(f"Video not found for deletion: {relative_path}")
                return False

        except Exception as e:
            logger.error(f"❌ Failed to delete {relative_path}: {e}")
            return False

    def get_video_metadata(self, relative_path: str) -> Optional[dict]:
        """Get video metadata from local storage.

        Args:
            relative_path: Relative path from media base

        Returns:
            Metadata dict or None if not found
        """
        try:
            absolute_path = self.get_absolute_path(relative_path)

            if not absolute_path.exists():
                return None

            file_stat = absolute_path.stat()

            metadata = {
                'size': file_stat.st_size,
                'created_at': datetime.fromtimestamp(file_stat.st_ctime),
                'modified_at': datetime.fromtimestamp(file_stat.st_mtime),
                'path': relative_path,
                'absolute_path': str(absolute_path),
                'url': self.get_url_path(relative_path)
            }

            return metadata

        except Exception as e:
            logger.error(f"❌ Failed to get metadata for {relative_path}: {e}")
            return None

    def video_exists(self, relative_path: str) -> bool:
        """Check if video exists in local storage.

        Args:
            relative_path: Relative path from media base

        Returns:
            True if video exists
        """
        absolute_path = self.get_absolute_path(relative_path)
        return absolute_path.exists() and absolute_path.is_file()

    def list_videos(self, user_id: Optional[str] = None, date_prefix: Optional[str] = None) -> list[dict]:
        """List videos in local storage.

        Args:
            user_id: Filter by user ID
            date_prefix: Filter by date prefix (YYYYMMDD)

        Returns:
            List of video metadata dicts
        """
        try:
            videos = []

            # Build search pattern
            search_path = self.videos_path
            if date_prefix:
                search_path = search_path / date_prefix
            if user_id:
                search_path = search_path / user_id

            # Find all .mp4 files
            if search_path.exists():
                for video_file in search_path.rglob("*.mp4"):
                    # Convert to relative path
                    relative_path = video_file.relative_to(self.base_path)
                    metadata = self.get_video_metadata(str(relative_path))
                    if metadata:
                        videos.append(metadata)

            # Sort by creation time, newest first
            videos.sort(key=lambda x: x['created_at'], reverse=True)

            logger.info(f"Found {len(videos)} videos (user_id={user_id}, date={date_prefix})")
            return videos

        except Exception as e:
            logger.error(f"❌ Failed to list videos: {e}")
            return []

    def get_storage_stats(self) -> dict:
        """Get storage statistics.

        Returns:
            Dict with storage stats
        """
        try:
            total_size = 0
            total_files = 0

            if self.videos_path.exists():
                for video_file in self.videos_path.rglob("*.mp4"):
                    total_size += video_file.stat().st_size
                    total_files += 1

            return {
                'total_files': total_files,
                'total_size_bytes': total_size,
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'base_path': str(self.base_path),
                'videos_path': str(self.videos_path)
            }

        except Exception as e:
            logger.error(f"❌ Failed to get storage stats: {e}")
            return {
                'total_files': 0,
                'total_size_bytes': 0,
                'total_size_mb': 0,
                'base_path': str(self.base_path),
                'videos_path': str(self.videos_path)
            }


class MockLocalMediaManager:
    """Mock local media manager for testing."""

    def __init__(self):
        self.mock_storage = {}  # In-memory "storage"
        logger.info("🎭 Using mock local media manager")

    def generate_file_path(self, user_id: str, file_extension: str = "mp4") -> str:
        """Generate mock file path."""
        unique_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().strftime("%Y%m%d")
        relative_path = f"videos/{timestamp}/{user_id}/{unique_id}.{file_extension}"
        logger.info(f"🎭 Generated mock file path: {relative_path}")
        return relative_path

    def get_url_path(self, relative_path: str) -> str:
        """Get mock URL path."""
        return f"/media/{relative_path}"

    async def save_video(
        self,
        file_data: BinaryIO,
        relative_path: str,
        content_type: str = "video/mp4"
    ) -> dict:
        """Mock video save."""
        # Read file size
        file_data.seek(0, 2)  # Seek to end
        file_size = file_data.tell()
        file_data.seek(0)  # Reset to beginning

        # Store in mock storage
        self.mock_storage[relative_path] = {
            'size': file_size,
            'content_type': content_type,
            'created_at': datetime.utcnow(),
            'data': file_data.read()
        }

        upload_info = {
            'path': relative_path,
            'absolute_path': f'/mock/{relative_path}',
            'size': file_size,
            'created_at': datetime.utcnow(),
            'content_type': content_type,
            'url': self.get_url_path(relative_path)
        }

        logger.info(f"🎭 Mock saved video: {relative_path} ({file_size} bytes)")
        return upload_info

    def delete_video(self, relative_path: str) -> bool:
        """Mock delete video."""
        if relative_path in self.mock_storage:
            del self.mock_storage[relative_path]
            logger.info(f"🎭 Mock deleted video: {relative_path}")
            return True
        return False

    def get_video_metadata(self, relative_path: str) -> Optional[dict]:
        """Get mock video metadata."""
        if relative_path in self.mock_storage:
            stored = self.mock_storage[relative_path]
            return {
                'size': stored['size'],
                'created_at': stored['created_at'],
                'modified_at': stored['created_at'],
                'path': relative_path,
                'absolute_path': f'/mock/{relative_path}',
                'url': self.get_url_path(relative_path)
            }
        return None

    def video_exists(self, relative_path: str) -> bool:
        """Check if mock video exists."""
        return relative_path in self.mock_storage

    def list_videos(self, user_id: Optional[str] = None, date_prefix: Optional[str] = None) -> list[dict]:
        """List mock videos."""
        videos = []
        for path, data in self.mock_storage.items():
            metadata = self.get_video_metadata(path)
            if metadata:
                # Apply filters
                if user_id and user_id not in path:
                    continue
                if date_prefix and date_prefix not in path:
                    continue
                videos.append(metadata)

        # Sort by creation time, newest first
        videos.sort(key=lambda x: x['created_at'], reverse=True)
        return videos

    def get_storage_stats(self) -> dict:
        """Get mock storage stats."""
        total_size = sum(data['size'] for data in self.mock_storage.values())
        return {
            'total_files': len(self.mock_storage),
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'base_path': '/mock/media',
            'videos_path': '/mock/media/videos'
        }


def get_media_manager() -> LocalMediaManager | MockLocalMediaManager:
    """Get media manager instance (real or mock based on configuration)."""
    # For now, always use real manager since it's just local files
    # Could add mock mode if needed for testing
    try:
        return LocalMediaManager()
    except Exception as e:
        logger.warning(f"⚠️  Local media manager failed to initialize: {e}")
        logger.info("🎭 Falling back to mock media manager")
        return MockLocalMediaManager()