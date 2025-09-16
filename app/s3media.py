"""S3 media operations for video uploads and playback."""
import logging
import uuid
from datetime import datetime, timedelta
from typing import BinaryIO, Optional

import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from fastapi import HTTPException

from app.config import settings

logger = logging.getLogger(__name__)


class S3MediaManager:
    """Handles S3 operations for video media."""

    def __init__(self):
        self.bucket_name = settings.s3_bucket
        self.prefix = settings.s3_prefix
        self.region = settings.aws_region
        self.presign_expiry = settings.s3_presign_expiry_seconds
        self._client = None

    @property
    def client(self):
        """Get S3 client with lazy initialization."""
        if self._client is None:
            try:
                self._client = boto3.client('s3', region_name=self.region)
                # Test credentials by checking if bucket exists
                self._client.head_bucket(Bucket=self.bucket_name)
                logger.info(f"✅ S3 client connected to {self.bucket_name}")
            except NoCredentialsError:
                logger.error("❌ AWS credentials not found")
                raise HTTPException(
                    status_code=500,
                    detail="AWS credentials not configured"
                )
            except ClientError as e:
                error_code = e.response['Error']['Code']
                if error_code == '404':
                    logger.error(f"❌ S3 bucket '{self.bucket_name}' not found")
                    raise HTTPException(
                        status_code=500,
                        detail=f"S3 bucket '{self.bucket_name}' not found"
                    )
                else:
                    logger.error(f"❌ S3 error: {e}")
                    raise HTTPException(
                        status_code=500,
                        detail=f"S3 connection error: {error_code}"
                    )
        return self._client

    def generate_s3_key(self, user_id: str, file_extension: str = "mp4") -> str:
        """Generate unique S3 key for video upload."""
        # Use UUID for uniqueness and user_id for organization
        unique_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().strftime("%Y%m%d")

        # Format: uploads/20240916/user123/uuid.mp4
        key = f"{self.prefix}{timestamp}/{user_id}/{unique_id}.{file_extension}"

        logger.info(f"Generated S3 key: {key}")
        return key

    async def upload_video(
        self,
        file_data: BinaryIO,
        s3_key: str,
        content_type: str = "video/mp4"
    ) -> dict:
        """Upload video file to S3.

        Args:
            file_data: File-like object with video data
            s3_key: S3 object key for the upload
            content_type: MIME type of the file

        Returns:
            Dict with upload details
        """
        try:
            # Upload with server-side encryption
            extra_args = {
                'ContentType': content_type,
                'ServerSideEncryption': 'AES256',
                'Metadata': {
                    'uploaded_at': datetime.utcnow().isoformat(),
                    'application': 'citypulse-backend'
                }
            }

            self.client.upload_fileobj(
                file_data,
                self.bucket_name,
                s3_key,
                ExtraArgs=extra_args
            )

            # Get object info
            response = self.client.head_object(Bucket=self.bucket_name, Key=s3_key)

            upload_info = {
                'bucket': self.bucket_name,
                'key': s3_key,
                'size': response.get('ContentLength', 0),
                'etag': response.get('ETag', '').strip('"'),
                'last_modified': response.get('LastModified'),
                'content_type': response.get('ContentType', content_type)
            }

            logger.info(f"✅ Uploaded video to S3: {s3_key} ({upload_info['size']} bytes)")
            return upload_info

        except ClientError as e:
            error_code = e.response['Error']['Code']
            logger.error(f"❌ S3 upload failed: {error_code} - {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Video upload failed: {error_code}"
            )

    def generate_presigned_url(
        self,
        s3_key: str,
        expiry_seconds: Optional[int] = None
    ) -> str:
        """Generate presigned URL for video playback.

        Args:
            s3_key: S3 object key
            expiry_seconds: URL validity period (defaults to config value)

        Returns:
            Presigned URL for video access
        """
        if expiry_seconds is None:
            expiry_seconds = self.presign_expiry

        try:
            url = self.client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': s3_key
                },
                ExpiresIn=expiry_seconds
            )

            logger.info(f"Generated presigned URL for {s3_key} (expires in {expiry_seconds}s)")
            return url

        except ClientError as e:
            logger.error(f"❌ Failed to generate presigned URL: {e}")
            raise HTTPException(
                status_code=500,
                detail="Failed to generate video playback URL"
            )

    def generate_presigned_post(
        self,
        s3_key: str,
        expiry_seconds: int = 3600,
        max_file_size: int = 100 * 1024 * 1024  # 100MB
    ) -> dict:
        """Generate presigned POST for direct client uploads (optional feature).

        Args:
            s3_key: S3 object key
            expiry_seconds: Policy validity period
            max_file_size: Maximum allowed file size

        Returns:
            Presigned POST data with URL and fields
        """
        try:
            conditions = [
                {"bucket": self.bucket_name},
                {"key": s3_key},
                {"Content-Type": "video/mp4"},
                ["content-length-range", 1, max_file_size]
            ]

            presigned_post = self.client.generate_presigned_post(
                Bucket=self.bucket_name,
                Key=s3_key,
                Fields={
                    "Content-Type": "video/mp4",
                    "ServerSideEncryption": "AES256"
                },
                Conditions=conditions,
                ExpiresIn=expiry_seconds
            )

            logger.info(f"Generated presigned POST for {s3_key}")
            return presigned_post

        except ClientError as e:
            logger.error(f"❌ Failed to generate presigned POST: {e}")
            raise HTTPException(
                status_code=500,
                detail="Failed to generate upload URL"
            )

    def delete_video(self, s3_key: str) -> bool:
        """Delete video from S3.

        Args:
            s3_key: S3 object key to delete

        Returns:
            True if successful
        """
        try:
            self.client.delete_object(Bucket=self.bucket_name, Key=s3_key)
            logger.info(f"✅ Deleted video from S3: {s3_key}")
            return True

        except ClientError as e:
            logger.error(f"❌ Failed to delete {s3_key}: {e}")
            return False

    def get_video_metadata(self, s3_key: str) -> Optional[dict]:
        """Get video metadata from S3.

        Args:
            s3_key: S3 object key

        Returns:
            Metadata dict or None if not found
        """
        try:
            response = self.client.head_object(Bucket=self.bucket_name, Key=s3_key)

            metadata = {
                'size': response.get('ContentLength', 0),
                'last_modified': response.get('LastModified'),
                'content_type': response.get('ContentType'),
                'etag': response.get('ETag', '').strip('"'),
                'server_side_encryption': response.get('ServerSideEncryption'),
                'metadata': response.get('Metadata', {})
            }

            return metadata

        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                logger.warning(f"Video not found in S3: {s3_key}")
                return None
            else:
                logger.error(f"❌ Failed to get metadata for {s3_key}: {e}")
                return None

    def video_exists(self, s3_key: str) -> bool:
        """Check if video exists in S3.

        Args:
            s3_key: S3 object key

        Returns:
            True if video exists
        """
        return self.get_video_metadata(s3_key) is not None


class MockS3MediaManager:
    """Mock S3 manager for development/testing."""

    def __init__(self):
        self.bucket_name = settings.s3_bucket
        self.prefix = settings.s3_prefix
        self.presign_expiry = settings.s3_presign_expiry_seconds
        self.mock_storage = {}  # In-memory "storage"
        logger.info("🎭 Using mock S3 media manager")

    def generate_s3_key(self, user_id: str, file_extension: str = "mp4") -> str:
        """Generate mock S3 key."""
        unique_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().strftime("%Y%m%d")
        key = f"{self.prefix}{timestamp}/{user_id}/{unique_id}.{file_extension}"
        logger.info(f"🎭 Generated mock S3 key: {key}")
        return key

    async def upload_video(
        self,
        file_data: BinaryIO,
        s3_key: str,
        content_type: str = "video/mp4"
    ) -> dict:
        """Mock video upload."""
        # Read file size
        file_data.seek(0, 2)  # Seek to end
        file_size = file_data.tell()
        file_data.seek(0)  # Reset to beginning

        # Store in mock storage
        self.mock_storage[s3_key] = {
            'size': file_size,
            'content_type': content_type,
            'uploaded_at': datetime.utcnow(),
            'data': file_data.read()
        }

        upload_info = {
            'bucket': self.bucket_name,
            'key': s3_key,
            'size': file_size,
            'etag': f"mock-etag-{hash(s3_key)}",
            'last_modified': datetime.utcnow(),
            'content_type': content_type
        }

        logger.info(f"🎭 Mock uploaded video: {s3_key} ({file_size} bytes)")
        return upload_info

    def generate_presigned_url(
        self,
        s3_key: str,
        expiry_seconds: Optional[int] = None
    ) -> str:
        """Generate mock presigned URL."""
        if expiry_seconds is None:
            expiry_seconds = self.presign_expiry

        # Generate a realistic-looking mock URL
        expires_timestamp = int((datetime.utcnow() + timedelta(seconds=expiry_seconds)).timestamp())
        mock_url = (
            f"https://{self.bucket_name}.s3.{settings.aws_region}.amazonaws.com/{s3_key}"
            f"?X-Amz-Algorithm=AWS4-HMAC-SHA256"
            f"&X-Amz-Expires={expiry_seconds}"
            f"&X-Amz-SignedHeaders=host"
            f"&X-Amz-Signature=mock-signature-{hash(s3_key)}"
        )

        logger.info(f"🎭 Generated mock presigned URL for {s3_key}")
        return mock_url

    def generate_presigned_post(
        self,
        s3_key: str,
        expiry_seconds: int = 3600,
        max_file_size: int = 100 * 1024 * 1024
    ) -> dict:
        """Generate mock presigned POST."""
        return {
            'url': f"https://{self.bucket_name}.s3.{settings.aws_region}.amazonaws.com/",
            'fields': {
                'key': s3_key,
                'Content-Type': 'video/mp4',
                'policy': f'mock-policy-{hash(s3_key)}',
                'x-amz-algorithm': 'AWS4-HMAC-SHA256',
                'x-amz-signature': f'mock-signature-{hash(s3_key)}'
            }
        }

    def delete_video(self, s3_key: str) -> bool:
        """Mock delete video."""
        if s3_key in self.mock_storage:
            del self.mock_storage[s3_key]
            logger.info(f"🎭 Mock deleted video: {s3_key}")
            return True
        return False

    def get_video_metadata(self, s3_key: str) -> Optional[dict]:
        """Get mock video metadata."""
        if s3_key in self.mock_storage:
            stored = self.mock_storage[s3_key]
            return {
                'size': stored['size'],
                'last_modified': stored['uploaded_at'],
                'content_type': stored['content_type'],
                'etag': f"mock-etag-{hash(s3_key)}",
                'server_side_encryption': 'AES256',
                'metadata': {}
            }
        return None

    def video_exists(self, s3_key: str) -> bool:
        """Check if mock video exists."""
        return s3_key in self.mock_storage


def get_s3_manager() -> S3MediaManager | MockS3MediaManager:
    """Get S3 manager instance (real or mock based on availability)."""
    try:
        # Try to create real S3 manager
        manager = S3MediaManager()
        # Test connection by accessing client property
        _ = manager.client
        return manager
    except (HTTPException, Exception) as e:
        logger.warning(f"⚠️  S3 not available: {e}")
        logger.info("🎭 Falling back to mock S3 manager")
        return MockS3MediaManager()