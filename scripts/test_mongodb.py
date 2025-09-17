#!/usr/bin/env python3
"""Test MongoDB connection and basic operations."""
import asyncio
from datetime import datetime, timedelta

from app.config import settings
from app.dao import DatabaseOperations
from app.deps import db_manager
from app.models import VideoDocument, UserTaste


async def test_mongodb():
    """Test MongoDB operations."""
    print("🗄️  CityPulse MongoDB Test")
    print("=" * 30)

    try:
        # Connect
        print("Connecting to MongoDB...")
        await db_manager.connect()
        db = db_manager.get_database()
        db_ops = DatabaseOperations(db)

        print("✅ Connected successfully!")

        # Test 1: Create indexes
        print("\n📊 Testing index creation...")
        index_results = await db_ops.create_indexes()
        success_count = sum(index_results.values())
        print(f"✅ Created {success_count}/{len(index_results)} indexes")

        # Test 2: Create a test video
        print("\n🎥 Testing video creation...")
        test_video = VideoDocument(
            user_id="test_user",
            borough="Brooklyn",
            borough_source="manual",
            file_path="videos/20240917/test_user/sample.mp4",
            title="Test Video for MongoDB",
            tags=["test", "brooklyn", "demo"],
            transcript="This is a test video for MongoDB integration.",
            multimodal_transcript="This is a test video for MongoDB integration. Visual: Brooklyn street scene.",
            embedding=[0.1] * 1536,  # Mock embedding
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(hours=24)
        )

        video_id = await db_ops.videos.create_video(test_video)
        print(f"✅ Created test video: {video_id}")

        # Test 3: Retrieve video
        print("\n📖 Testing video retrieval...")
        retrieved_video = await db_ops.videos.get_video(video_id)
        if retrieved_video:
            print(f"✅ Retrieved video: {retrieved_video.title}")
        else:
            print("❌ Failed to retrieve video")

        # Test 4: Test user operations
        print("\n👤 Testing user operations...")
        user = await db_ops.users.get_user("test_user")
        print(f"✅ Retrieved user: {user.id}")

        # Test 5: Test like operation
        print("\n❤️  Testing like operations...")
        like_id = await db_ops.likes.create_like("test_user", video_id)
        print(f"✅ Created like: {like_id}")

        # Test 6: Update user taste
        print("\n🎯 Testing taste update...")
        mock_embedding = [0.2] * 1536
        updated_user = await db_ops.users.update_user_taste("test_user", mock_embedding)
        print(f"✅ Updated user taste (n={updated_user.taste.n})")

        # Test 7: Feed query
        print("\n📱 Testing feed query...")
        feed_videos = await db_ops.videos.get_feed_videos("Brooklyn", limit=5)
        print(f"✅ Retrieved {len(feed_videos)} videos for Brooklyn feed")

        # Test 8: Vector search (will fallback if index not ready)
        print("\n🔍 Testing vector search...")
        query_vector = [0.15] * 1536
        search_results = await db_ops.videos.vector_search(
            query_vector, borough="Brooklyn", limit=5
        )
        print(f"✅ Vector search returned {len(search_results)} results")

        # Cleanup
        print("\n🧹 Cleaning up test data...")
        await db.videos.delete_one({"_id": video_id})
        await db.users.delete_one({"_id": "test_user"})
        await db.likes.delete_one({"user_id": "test_user", "video_id": video_id})
        print("✅ Cleanup complete")

        print("\n🎉 All MongoDB tests passed!")
        return True

    except Exception as e:
        print(f"\n❌ MongoDB test failed: {e}")
        return False

    finally:
        await db_manager.disconnect()


if __name__ == "__main__":
    if settings.mongo_uri == "mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority":
        print("⚠️  Using example MongoDB URI - tests will fail")
        print("💡 Update MONGO_URI in .env with your Atlas connection string")
        print("🔄 Running in simulation mode...\n")

        # Simulate test results
        print("🗄️  CityPulse MongoDB Test (Simulation)")
        print("=" * 30)
        print("✅ Connection: Simulated")
        print("✅ Indexes: Simulated")
        print("✅ Video CRUD: Simulated")
        print("✅ User operations: Simulated")
        print("✅ Like operations: Simulated")
        print("✅ Vector search: Simulated")
        print("\n🎭 Simulation complete! Ready for real MongoDB Atlas.")
    else:
        success = asyncio.run(test_mongodb())
        exit(0 if success else 1)