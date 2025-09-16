#!/usr/bin/env python3
"""Test configuration and service connections."""
import asyncio
import sys

from app.config import settings
from app.deps import validate_connections


async def test_configuration():
    """Test all configuration and connections."""
    print("🔧 CityPulse Configuration Test")
    print("=" * 40)

    # Show configuration
    print(f"Database: {settings.mongo_db}")
    print(f"S3 Bucket: {settings.s3_bucket}")
    print(f"AWS Region: {settings.aws_region}")
    print(f"Environment: {'Mock Mode' if settings.is_mock_mode else 'Production'}")
    print(f"Providers:")
    print(f"  - Transcription: {settings.transcribe_provider}")
    print(f"  - Embeddings: {settings.embeddings_provider}")
    print(f"  - LLM: {settings.llm_provider}")
    print(f"  - Vision: {settings.vision_provider}")
    print()

    # Test connections
    print("🔍 Testing Service Connections...")
    print("-" * 30)

    results = await validate_connections()

    for service, status in results.items():
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {service.upper()}: {'Connected' if status else 'Failed'}")

    print()

    # Summary
    failed_count = sum(1 for status in results.values() if not status)
    total_count = len(results)

    if failed_count == 0:
        print("🎉 All services are ready! You're good to go!")
        return True
    else:
        print(f"⚠️  {failed_count}/{total_count} services failed.")
        if settings.is_mock_mode:
            print("💡 Running in mock mode - this is OK for development and demo!")
            return True
        else:
            print("💡 Update your .env file with proper credentials.")
            return False


if __name__ == "__main__":
    success = asyncio.run(test_configuration())
    sys.exit(0 if success else 1)