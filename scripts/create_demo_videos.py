#!/usr/bin/env python3
"""Create demo video files for local storage demo.

This script creates placeholder video files in the correct directory structure
so that the seeded data has actual files to serve.
"""
import asyncio
import sys
from datetime import datetime, timedelta
from pathlib import Path

from app.config import settings
from app.local_media import get_media_manager


# Same demo video data from seed script
DEMO_VIDEOS = [
    # Manhattan
    {"user_id": "demo_user_1", "borough": "Manhattan", "title": "Times Square Sunset: Street Energy", "created_hours_ago": 2},
    {"user_id": "demo_user_2", "borough": "Manhattan", "title": "Central Park Jazz & Fall Colors", "created_hours_ago": 4},
    {"user_id": "demo_user_3", "borough": "Manhattan", "title": "Washington Square Food Truck Paradise", "created_hours_ago": 1},

    # Brooklyn
    {"user_id": "demo_user_4", "borough": "Brooklyn", "title": "Williamsburg Street Art & Coffee Culture", "created_hours_ago": 3},
    {"user_id": "demo_user_5", "borough": "Brooklyn", "title": "Brooklyn Bridge Park Market Vibes", "created_hours_ago": 5},
    {"user_id": "demo_user_6", "borough": "Brooklyn", "title": "DUMBO Golden Hour Magic", "created_hours_ago": 6},

    # Queens
    {"user_id": "demo_user_7", "borough": "Queens", "title": "Astoria Greek Food & Live Music", "created_hours_ago": 2},
    {"user_id": "demo_user_8", "borough": "Queens", "title": "Flushing Meadows Cultural Festival", "created_hours_ago": 4},

    # Bronx
    {"user_id": "demo_user_9", "borough": "Bronx", "title": "South Bronx Hip-Hop Cypher", "created_hours_ago": 3},
    {"user_id": "demo_user_10", "borough": "Bronx", "title": "Arthur Avenue: Real Little Italy", "created_hours_ago": 1},

    # Staten Island
    {"user_id": "demo_user_11", "borough": "Staten Island", "title": "Staten Island Ferry Sunset Views", "created_hours_ago": 2},
    {"user_id": "demo_user_12", "borough": "Staten Island", "title": "Richmond Town Living History", "created_hours_ago": 5},
]


def create_dummy_mp4_file(file_path: Path, duration_seconds: int = 45) -> None:
    """Create a tiny dummy MP4 file for demo purposes.

    This creates a minimal valid MP4 file that browsers can recognize.
    For a real demo, you'd replace these with actual video files.
    """
    # Minimal MP4 header that browsers will recognize
    # This is not a playable video, but it's a valid file structure
    mp4_header = bytes([
        # ftyp box (file type)
        0x00, 0x00, 0x00, 0x20,  # box size (32 bytes)
        0x66, 0x74, 0x79, 0x70,  # 'ftyp'
        0x69, 0x73, 0x6F, 0x6D,  # major brand 'isom'
        0x00, 0x00, 0x02, 0x00,  # minor version
        0x69, 0x73, 0x6F, 0x6D,  # compatible brands
        0x69, 0x73, 0x6F, 0x32,
        0x61, 0x76, 0x63, 0x31,
        0x6D, 0x70, 0x34, 0x31,

        # mdat box (media data) - empty for demo
        0x00, 0x00, 0x00, 0x08,  # box size (8 bytes)
        0x6D, 0x64, 0x61, 0x74,  # 'mdat'
    ])

    file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(file_path, 'wb') as f:
        f.write(mp4_header)

    print(f"📹 Created dummy MP4: {file_path}")


async def create_demo_video_files():
    """Create demo video files in the correct local directory structure."""
    print("🎬 Creating demo video files for local storage...")
    print("=" * 50)

    media_manager = get_media_manager()
    base_path = Path(settings.media_base_path)

    # Ensure base directory exists
    base_path.mkdir(parents=True, exist_ok=True)

    created_files = []

    for video_data in DEMO_VIDEOS:
        # Calculate when this video was "created"
        created_at = datetime.utcnow() - timedelta(hours=video_data["created_hours_ago"])

        # Generate the same file path that the seed script will use
        file_path = f"videos/{created_at.strftime('%Y%m%d')}/{video_data['user_id']}/{created_at.strftime('%H%M%S')}.mp4"

        # Create absolute path
        absolute_path = media_manager.get_absolute_path(file_path)

        # Create dummy video file
        create_dummy_mp4_file(absolute_path, duration_seconds=45)

        created_files.append({
            'file_path': file_path,
            'absolute_path': absolute_path,
            'title': video_data['title'],
            'borough': video_data['borough'],
            'url': media_manager.get_url_path(file_path)
        })

    print(f"\n✅ Created {len(created_files)} demo video files")

    # Show file structure
    print(f"\n📁 File structure created in: {base_path}")
    for video in created_files:
        print(f"   🎥 {video['file_path']} - {video['title'][:40]}...")
        print(f"      URL: {video['url']}")
        print(f"      Borough: {video['borough']}")
        print()

    # Show storage stats
    stats = media_manager.get_storage_stats()
    print(f"📊 Storage Stats:")
    print(f"   Total files: {stats['total_files']}")
    print(f"   Total size: {stats['total_size_mb']} MB")
    print(f"   Base path: {stats['base_path']}")

    return created_files


def show_instructions():
    """Show instructions for replacing dummy files with real videos."""
    print("\n📝 Instructions for Demo Preparation:")
    print("=" * 50)
    print("1. Replace dummy .mp4 files with real NYC videos")
    print("2. Keep the same filenames and directory structure")
    print("3. Recommended: Keep videos under 60 seconds for demo")
    print("4. Run the seed script after placing real videos:")
    print("   uv run python scripts/seed_demo_data.py")
    print("5. Test the API endpoints:")
    print("   uv run uvicorn app.main:app --reload")
    print("\n🎯 Demo Flow:")
    print("- Browse different boroughs")
    print("- Like videos to see personalized ranking")
    print("- Try 'Ask NYC' queries like:")
    print("  * 'What's happening in Williamsburg?'")
    print("  * 'Any food events in Brooklyn?'")
    print("  * 'Show me street art activities'")


async def main():
    """Main function."""
    print("🚀 CityPulse Demo Video File Creator")
    print("=" * 40)

    try:
        created_files = await create_demo_video_files()
        show_instructions()

        print(f"\n🎉 Demo video files created successfully!")
        print(f"📹 {len(created_files)} video files ready for demo")

        return True

    except Exception as e:
        print(f"❌ Failed to create demo video files: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)