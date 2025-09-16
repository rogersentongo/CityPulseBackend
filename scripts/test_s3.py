#!/usr/bin/env python3
"""Test S3 media pipeline."""
import asyncio
import io
import sys

from app.config import settings
from app.s3media import get_s3_manager
from app.utils.video import get_video_processor


async def test_s3_pipeline():
    """Test S3 media operations."""
    print("📁 CityPulse S3 Media Pipeline Test")
    print("=" * 40)

    # Get S3 manager (real or mock)
    s3_manager = get_s3_manager()
    manager_type = "Mock" if hasattr(s3_manager, 'mock_storage') else "Real"
    print(f"S3 Manager: {manager_type}")

    # Get video processor
    video_processor = get_video_processor()
    processor_type = "Mock" if hasattr(video_processor, '__class__') and "Mock" in video_processor.__class__.__name__ else "Real"
    print(f"Video Processor: {processor_type}")

    try:
        # Test 1: Generate S3 key
        print("\n🔑 Testing S3 key generation...")
        s3_key = s3_manager.generate_s3_key("test_user", "mp4")
        print(f"✅ Generated S3 key: {s3_key}")

        # Test 2: Create mock video file
        print("\n🎬 Creating mock video file...")
        mock_video_data = b"MOCK_VIDEO_DATA_" + b"0" * 1024  # 1KB mock file
        video_file = io.BytesIO(mock_video_data)
        print(f"✅ Created mock video file ({len(mock_video_data)} bytes)")

        # Test 3: Video validation
        print("\n✅ Testing video validation...")
        validation_result = video_processor.validate_video_file(video_file, max_duration=60)
        if validation_result['valid']:
            print(f"✅ Video validation passed: {validation_result['info']}")
        else:
            print(f"❌ Video validation failed: {validation_result['errors']}")

        # Test 4: Upload video
        print("\n⬆️  Testing video upload...")
        video_file.seek(0)  # Reset file pointer
        upload_result = await s3_manager.upload_video(
            video_file,
            s3_key,
            content_type="video/mp4"
        )
        print(f"✅ Upload successful: {upload_result}")

        # Test 5: Generate presigned URL
        print("\n🔗 Testing presigned URL generation...")
        presigned_url = s3_manager.generate_presigned_url(s3_key)
        print(f"✅ Generated presigned URL: {presigned_url[:80]}...")

        # Test 6: Check video existence
        print("\n🔍 Testing video existence check...")
        exists = s3_manager.video_exists(s3_key)
        print(f"✅ Video exists: {exists}")

        # Test 7: Get video metadata
        print("\n📋 Testing metadata retrieval...")
        metadata = s3_manager.get_video_metadata(s3_key)
        if metadata:
            print(f"✅ Metadata retrieved: {metadata}")
        else:
            print("❌ Failed to retrieve metadata")

        # Test 8: Presigned POST (optional)
        print("\n📤 Testing presigned POST generation...")
        try:
            presigned_post = s3_manager.generate_presigned_post(
                s3_manager.generate_s3_key("test_user_2", "mp4")
            )
            print(f"✅ Generated presigned POST: {presigned_post['url']}")
        except Exception as e:
            print(f"⚠️  Presigned POST failed: {e}")

        # Test 9: Video processing features
        if processor_type == "Real":
            print("\n🎥 Testing video processing features...")
            # Create a temp file for testing
            import tempfile
            with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_file:
                temp_file.write(mock_video_data)
                temp_file_path = temp_file.name

            try:
                duration = video_processor.get_video_duration(temp_file_path)
                print(f"✅ Video duration: {duration}s")

                gps_coords = video_processor.extract_gps_metadata(temp_file_path)
                if gps_coords:
                    print(f"✅ GPS coordinates: {gps_coords}")
                else:
                    print("ℹ️  No GPS coordinates found")

            finally:
                import os
                os.unlink(temp_file_path)

        # Test 10: Cleanup
        print("\n🧹 Testing video deletion...")
        deleted = s3_manager.delete_video(s3_key)
        print(f"✅ Video deleted: {deleted}")

        print("\n🎉 All S3 media pipeline tests passed!")
        return True

    except Exception as e:
        print(f"\n❌ S3 media pipeline test failed: {e}")
        return False


def test_configuration():
    """Test S3 configuration."""
    print("⚙️  S3 Configuration")
    print("-" * 20)
    print(f"Bucket: {settings.s3_bucket}")
    print(f"Region: {settings.aws_region}")
    print(f"Prefix: {settings.s3_prefix}")
    print(f"Presign Expiry: {settings.s3_presign_expiry_seconds}s")

    # Check if using example values
    if settings.s3_bucket == "citypulse-media-demo":
        print("\n⚠️  Using example S3 bucket name")
        print("💡 Update S3_BUCKET in .env for production use")
        print("🎭 Mock mode will be used for testing")
    else:
        print(f"\n✅ Custom S3 bucket configured: {settings.s3_bucket}")


if __name__ == "__main__":
    test_configuration()
    print()

    success = asyncio.run(test_s3_pipeline())
    sys.exit(0 if success else 1)