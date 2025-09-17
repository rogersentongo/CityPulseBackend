#!/usr/bin/env python3
"""Seed demo data for CityPulse hackathon demonstration.

This script creates realistic video content across all NYC boroughs
to showcase the AI-powered features during the demo.
"""
import asyncio
import sys
from datetime import datetime, timedelta
from pathlib import Path

from app.config import settings
from app.dao import get_db_ops
from app.deps import get_database
from app.llm import get_llm_service
from app.models import VideoDocument


# Demo video content with realistic NYC scenarios
DEMO_VIDEOS = [
    # Manhattan
    {
        "user_id": "demo_user_1",
        "borough": "Manhattan",
        "transcript": "Walking through Times Square at sunset and the energy is absolutely incredible. Street performers everywhere, tourists taking photos, and those massive LED billboards lighting up everything. Just caught an amazing breakdancer who had a huge crowd gathered around him.",
        "title": "Times Square Sunset: Street Energy",
        "tags": ["times-square", "street-performance", "manhattan", "sunset", "energy"],
        "created_hours_ago": 2,
    },
    {
        "user_id": "demo_user_2",
        "borough": "Manhattan",
        "transcript": "Central Park on this beautiful Saturday afternoon. Families having picnics, kids playing frisbee, and there's a live jazz band performing near Bethesda Fountain. The fall foliage is absolutely stunning right now.",
        "title": "Central Park Jazz & Fall Colors",
        "tags": ["central-park", "jazz", "family", "fall", "nature"],
        "created_hours_ago": 4,
    },
    {
        "user_id": "demo_user_3",
        "borough": "Manhattan",
        "transcript": "Food truck heaven in Washington Square Park! Found this incredible Korean BBQ truck and the line is around the block. NYU students everywhere and street musicians playing acoustic sets. This is peak NYC vibes.",
        "title": "Washington Square Food Truck Paradise",
        "tags": ["washington-square", "food-truck", "korean-food", "nyu", "music"],
        "created_hours_ago": 1,
    },

    # Brooklyn
    {
        "user_id": "demo_user_4",
        "borough": "Brooklyn",
        "transcript": "Williamsburg is absolutely popping today! Walking down Bedford Avenue and there's street art everywhere. New murals going up, vintage shops packed with people, and the most amazing coffee shop with a rooftop overlooking Manhattan.",
        "title": "Williamsburg Street Art & Coffee Culture",
        "tags": ["williamsburg", "street-art", "coffee", "bedford-avenue", "rooftop"],
        "created_hours_ago": 3,
    },
    {
        "user_id": "demo_user_5",
        "borough": "Brooklyn",
        "transcript": "Brooklyn Bridge Park farmers market is incredible right now. Local vendors selling fresh produce, artisanal bread, and handmade crafts. Kids playing in the park with the Manhattan skyline as the backdrop. Perfect Saturday morning.",
        "title": "Brooklyn Bridge Park Market Vibes",
        "tags": ["brooklyn-bridge-park", "farmers-market", "local-vendors", "skyline", "weekend"],
        "created_hours_ago": 5,
    },
    {
        "user_id": "demo_user_6",
        "borough": "Brooklyn",
        "transcript": "DUMBO waterfront at golden hour is unreal. Couples taking engagement photos, cyclists everywhere, and food vendors serving amazing tacos. The view of Manhattan from here never gets old. Pure magic.",
        "title": "DUMBO Golden Hour Magic",
        "tags": ["dumbo", "waterfront", "golden-hour", "photography", "tacos"],
        "created_hours_ago": 6,
    },

    # Queens
    {
        "user_id": "demo_user_7",
        "borough": "Queens",
        "transcript": "Astoria food scene is absolutely incredible today. Walking through the Greek neighborhood and found this family-owned taverna with live bouzouki music. The lamb gyros are the best I've had in NYC.",
        "title": "Astoria Greek Food & Live Music",
        "tags": ["astoria", "greek-food", "live-music", "taverna", "authentic"],
        "created_hours_ago": 2,
    },
    {
        "user_id": "demo_user_8",
        "borough": "Queens",
        "transcript": "Flushing Meadows Corona Park is buzzing with activity. Families from all over Queens having barbecues, kids playing soccer, and there's a cultural festival with music from around the world. So diverse and beautiful.",
        "title": "Flushing Meadows Cultural Festival",
        "tags": ["flushing-meadows", "cultural-festival", "diversity", "barbecue", "world-music"],
        "created_hours_ago": 4,
    },

    # Bronx
    {
        "user_id": "demo_user_9",
        "borough": "Bronx",
        "transcript": "South Bronx hip-hop scene is alive and well! Just witnessed an incredible cypher near Yankee Stadium. Local MCs spitting bars about their neighborhood, breakdancers, and a crowd that was completely locked in.",
        "title": "South Bronx Hip-Hop Cypher",
        "tags": ["south-bronx", "hip-hop", "cypher", "yankee-stadium", "breakdancing"],
        "created_hours_ago": 3,
    },
    {
        "user_id": "demo_user_10",
        "borough": "Bronx",
        "transcript": "Arthur Avenue in the Bronx is the real Little Italy! Family-owned pasta shops, fresh mozzarella being made right in front of you, and the most incredible cannoli. This is where authentic Italian-American culture thrives.",
        "title": "Arthur Avenue: Real Little Italy",
        "tags": ["arthur-avenue", "little-italy", "pasta", "mozzarella", "authentic-italian"],
        "created_hours_ago": 1,
    },

    # Staten Island
    {
        "user_id": "demo_user_11",
        "borough": "Staten Island",
        "transcript": "Staten Island Ferry ride with the most incredible sunset views of Manhattan. Locals and tourists all gathering on the deck, taking photos of the Statue of Liberty and lower Manhattan skyline. Free tour of NYC!",
        "title": "Staten Island Ferry Sunset Views",
        "tags": ["staten-island-ferry", "sunset", "statue-of-liberty", "manhattan-skyline", "free"],
        "created_hours_ago": 2,
    },
    {
        "user_id": "demo_user_12",
        "borough": "Staten Island",
        "transcript": "Historic Richmond Town is like stepping back in time. Colonial buildings, blacksmith demonstrations, and families learning about early American history. Kids are fascinated by the old-fashioned crafts and trades.",
        "title": "Richmond Town Living History",
        "tags": ["richmond-town", "history", "colonial", "blacksmith", "family-education"],
        "created_hours_ago": 5,
    }
]

# Demo user profiles for taste learning
DEMO_USERS = [
    {"user_id": "demo_user_1", "preferences": ["street-performance", "urban-energy", "manhattan"]},
    {"user_id": "demo_user_2", "preferences": ["nature", "jazz", "family-friendly"]},
    {"user_id": "demo_user_3", "preferences": ["food", "music", "students"]},
    {"user_id": "demo_user_4", "preferences": ["street-art", "coffee", "brooklyn"]},
    {"user_id": "demo_user_5", "preferences": ["farmers-market", "local", "community"]},
    {"user_id": "demo_user_6", "preferences": ["photography", "waterfront", "romantic"]},
    {"user_id": "demo_user_7", "preferences": ["authentic-food", "culture", "queens"]},
    {"user_id": "demo_user_8", "preferences": ["diversity", "families", "festivals"]},
    {"user_id": "demo_user_9", "preferences": ["hip-hop", "bronx", "urban-culture"]},
    {"user_id": "demo_user_10", "preferences": ["italian-food", "authentic", "traditional"]},
    {"user_id": "demo_user_11", "preferences": ["views", "tourism", "free-activities"]},
    {"user_id": "demo_user_12", "preferences": ["history", "education", "family"]},
]


async def create_demo_video(video_data: dict, llm_service) -> str:
    """Create a demo video document with AI-generated content."""
    print(f"📹 Creating demo video: {video_data['title']}")

    # Get database operations
    db = await get_database()
    db_ops = await get_db_ops(db)

    # Generate embedding for the transcript
    embedding = await llm_service.embedding_provider.create_embedding(video_data["transcript"])

    # Calculate creation time
    created_at = datetime.utcnow() - timedelta(hours=video_data["created_hours_ago"])
    expires_at = created_at + timedelta(hours=24)  # 24-hour TTL

    # Create video document
    video_doc = VideoDocument(
        user_id=video_data["user_id"],
        borough=video_data["borough"],
        borough_source="manual",
        file_path=f"videos/{created_at.strftime('%Y%m%d')}/{video_data['user_id']}/{created_at.strftime('%H%M%S')}.mp4",
        duration_sec=45,  # Mock duration
        has_audio=True,
        transcript=video_data["transcript"],
        multimodal_transcript=video_data["transcript"],
        title=video_data["title"],
        tags=video_data["tags"],
        embedding=embedding,
        embedding_source="audio",
        created_at=created_at,
        expires_at=expires_at
    )

    # Create video in database
    video_id = await db_ops.videos.create_video(video_doc)
    print(f"✅ Created video {video_id}: '{video_data['title']}'")

    return video_id


async def create_demo_users(llm_service) -> dict:
    """Create demo users with preference embeddings."""
    print("\n👥 Creating demo users with preferences...")

    db = await get_database()
    db_ops = await get_db_ops(db)

    user_embeddings = {}

    for user in DEMO_USERS:
        # Create preference embedding from user's interests
        preference_text = " ".join(user["preferences"])
        preference_embedding = await llm_service.embedding_provider.create_embedding(preference_text)

        # Get user (will create if doesn't exist) and then update taste with preferences
        user_doc = await db_ops.users.get_user(user["user_id"])

        # Simulate the user having some initial taste by updating with preference embedding
        await db_ops.users.update_user_taste(user["user_id"], preference_embedding)

        user_embeddings[user["user_id"]] = preference_embedding
        print(f"✅ Created user {user['user_id']} with preferences: {', '.join(user['preferences'])}")

    return user_embeddings


async def create_demo_likes(video_ids: list, user_embeddings: dict, llm_service):
    """Create realistic like interactions for taste learning."""
    print("\n👍 Creating demo like interactions...")

    db = await get_database()
    db_ops = await get_db_ops(db)

    # Simulate users liking videos that match their preferences
    like_count = 0

    for i, video_data in enumerate(DEMO_VIDEOS):
        video_id = video_ids[i]

        # Users like videos with similar tags to their preferences
        for user in DEMO_USERS:
            user_id = user["user_id"]
            user_prefs = set(user["preferences"])
            video_tags = set(video_data["tags"])

            # Calculate preference overlap
            overlap = len(user_prefs.intersection(video_tags))

            # Higher overlap = higher chance of liking (simulate realistic behavior)
            if overlap >= 2 or (overlap >= 1 and len(video_tags) <= 3):
                await db_ops.likes.create_like(user_id=user_id, video_id=video_id)
                like_count += 1
                print(f"❤️  {user_id} liked '{video_data['title'][:30]}...' (overlap: {overlap})")

    print(f"✅ Created {like_count} like interactions")


async def verify_demo_data():
    """Verify the seeded data is working correctly."""
    print("\n🔍 Verifying seeded demo data...")

    db = await get_database()
    db_ops = await get_db_ops(db)

    # Test 1: Check video counts by borough
    for borough in ["Manhattan", "Brooklyn", "Queens", "Bronx", "Staten Island"]:
        videos = await db_ops.videos.get_feed_videos(borough, limit=10)
        print(f"📍 {borough}: {len(videos)} videos")

    # Test 2: Test Ask NYC with seeded content
    llm_service = get_llm_service()

    test_queries = [
        "What's happening in Williamsburg?",
        "Any food events in Brooklyn?",
        "Show me street art activities",
        "What music events are happening?",
        "Any family activities in parks?"
    ]

    print("\n🤖 Testing Ask NYC with seeded content:")
    for query in test_queries:
        try:
            query_embedding = await llm_service.embedding_provider.create_embedding(query)
            video_sources = await db_ops.videos.get_videos_for_rag(
                query_vector=query_embedding,
                limit=5
            )

            if video_sources:
                print(f"✅ '{query}': Found {len(video_sources)} relevant videos")
                for video, score in video_sources[:2]:  # Show top 2
                    print(f"   - '{video.title}' (score: {score:.3f})")
            else:
                print(f"⚠️  '{query}': No videos found")
        except Exception as e:
            print(f"❌ '{query}': Error - {e}")


async def main():
    """Main seeding function."""
    print("🌱 CityPulse Demo Data Seeding")
    print("=" * 40)

    try:
        # Initialize LLM service for embeddings
        llm_service = get_llm_service()

        # Step 1: Create demo users
        user_embeddings = await create_demo_users(llm_service)

        # Step 2: Create demo videos
        print(f"\n📹 Creating {len(DEMO_VIDEOS)} demo videos...")
        video_ids = []

        for video_data in DEMO_VIDEOS:
            video_id = await create_demo_video(video_data, llm_service)
            video_ids.append(video_id)

        # Step 3: Create like interactions
        await create_demo_likes(video_ids, user_embeddings, llm_service)

        # Step 4: Verify everything works
        await verify_demo_data()

        print(f"\n🎉 Demo seeding completed successfully!")
        print(f"📊 Created:")
        print(f"   - {len(DEMO_USERS)} demo users with preferences")
        print(f"   - {len(DEMO_VIDEOS)} demo videos across all boroughs")
        print(f"   - Realistic like interactions for taste learning")
        print(f"\n🚀 Ready for hackathon demo!")

        return True

    except Exception as e:
        print(f"❌ Demo seeding failed: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)