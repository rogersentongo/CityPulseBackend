"""Data Access Object for MongoDB operations."""
import logging
from datetime import datetime, timedelta
from typing import Any, Optional

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import DESCENDING

from app.models import (
    LikeDocument,
    UserDocument,
    UserTaste,
    VideoDocument,
    Borough,
)

logger = logging.getLogger(__name__)


class VideoDAO:
    """Data access object for video operations."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.videos

    async def create_video(self, video: VideoDocument) -> str:
        """Create a new video document."""
        # Ensure expires_at is set (24 hours from now)
        if not video.expires_at:
            video.expires_at = video.created_at + timedelta(hours=24)

        video_dict = video.model_dump(by_alias=True, exclude={"id"})
        result = await self.collection.insert_one(video_dict)
        logger.info(f"Created video {result.inserted_id} in {video.borough}")
        return str(result.inserted_id)

    async def get_video(self, video_id: str) -> Optional[VideoDocument]:
        """Get video by ID."""
        try:
            doc = await self.collection.find_one({"_id": ObjectId(video_id)})
            if doc:
                doc["_id"] = str(doc["_id"])
                return VideoDocument(**doc)
            return None
        except Exception as e:
            logger.error(f"Error getting video {video_id}: {e}")
            return None

    async def get_feed_videos(
        self,
        borough: Borough,
        limit: int = 20,
        skip: int = 0,
        since_hours: int = 48,
    ) -> list[VideoDocument]:
        """Get recent videos for a borough feed."""
        since_time = datetime.utcnow() - timedelta(hours=since_hours)

        cursor = self.collection.find(
            {
                "borough": borough,
                "created_at": {"$gte": since_time}
            }
        ).sort("created_at", DESCENDING).skip(skip).limit(limit)

        videos = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            videos.append(VideoDocument(**doc))

        logger.info(f"Retrieved {len(videos)} videos for {borough} feed")
        return videos

    async def vector_search(
        self,
        query_vector: list[float],
        borough: Optional[Borough] = None,
        limit: int = 50,
        since_hours: int = 48,
    ) -> list[tuple[VideoDocument, float]]:
        """Perform vector search using MongoDB Atlas Vector Search."""
        since_time = datetime.utcnow() - timedelta(hours=since_hours)

        # Build the aggregation pipeline for Atlas Vector Search
        pipeline = [
            {
                "$vectorSearch": {
                    "index": "embedding_index",
                    "path": "embedding",
                    "queryVector": query_vector,
                    "numCandidates": limit * 2,  # Cast wider net
                    "limit": limit,
                    "filter": {
                        "created_at": {"$gte": since_time}
                    }
                }
            },
            {
                "$addFields": {
                    "search_score": {"$meta": "vectorSearchScore"}
                }
            }
        ]

        # Add borough filter if specified
        if borough:
            pipeline[0]["$vectorSearch"]["filter"]["borough"] = borough

        try:
            results = []
            async for doc in self.collection.aggregate(pipeline):
                doc["_id"] = str(doc["_id"])
                score = doc.pop("search_score", 0.0)
                video = VideoDocument(**doc)
                results.append((video, score))

            logger.info(f"Vector search returned {len(results)} results for {borough or 'all boroughs'}")
            return results

        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            # Fallback to regular search
            logger.info("Falling back to recency-based search")
            videos = await self.get_feed_videos(borough or "Manhattan", limit, since_hours=since_hours)
            return [(video, 0.5) for video in videos]  # Mock scores

    async def get_videos_for_rag(
        self,
        query_vector: list[float],
        borough: Optional[Borough] = None,
        window_hours: int = 6,
        limit: int = 10,
    ) -> list[tuple[VideoDocument, float]]:
        """Get relevant videos for RAG (Ask NYC) queries."""
        return await self.vector_search(
            query_vector=query_vector,
            borough=borough,
            limit=limit,
            since_hours=window_hours,
        )


class UserDAO:
    """Data access object for user operations."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.users

    async def get_user(self, user_id: str) -> UserDocument:
        """Get user by ID, create if doesn't exist."""
        doc = await self.collection.find_one({"_id": user_id})

        if doc:
            return UserDocument(**doc)
        else:
            # Create new user with empty taste profile
            user = UserDocument(id=user_id, taste=UserTaste())
            await self.collection.insert_one(user.model_dump(by_alias=True))
            logger.info(f"Created new user: {user_id}")
            return user

    async def update_user_taste(
        self,
        user_id: str,
        video_embedding: list[float],
    ) -> UserDocument:
        """Update user taste profile with new liked video embedding."""
        user = await self.get_user(user_id)

        if user.taste.n == 0:
            # First like - use the embedding directly
            new_embedding = video_embedding
            new_n = 1
        else:
            # Update running mean: new_mean = (old_mean * n + new_vector) / (n + 1)
            old_embedding = user.taste.embedding
            n = user.taste.n

            new_embedding = [
                (old_val * n + new_val) / (n + 1)
                for old_val, new_val in zip(old_embedding, video_embedding)
            ]
            new_n = n + 1

        # Update user taste
        updated_taste = UserTaste(
            embedding=new_embedding,
            n=new_n,
            updated_at=datetime.utcnow()
        )

        await self.collection.update_one(
            {"_id": user_id},
            {
                "$set": {
                    "taste": updated_taste.model_dump()
                }
            }
        )

        user.taste = updated_taste
        logger.info(f"Updated taste for user {user_id} (n={new_n})")
        return user


class LikeDAO:
    """Data access object for like operations."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.likes

    async def create_like(self, user_id: str, video_id: str) -> str:
        """Create a like record."""
        # Check if already liked
        existing = await self.collection.find_one({
            "user_id": user_id,
            "video_id": video_id
        })

        if existing:
            logger.info(f"User {user_id} already liked video {video_id}")
            return str(existing["_id"])

        like = LikeDocument(
            user_id=user_id,
            video_id=video_id,
            created_at=datetime.utcnow()
        )

        result = await self.collection.insert_one(
            like.model_dump(by_alias=True, exclude={"id"})
        )

        logger.info(f"User {user_id} liked video {video_id}")
        return str(result.inserted_id)

    async def user_has_liked(self, user_id: str, video_id: str) -> bool:
        """Check if user has already liked a video."""
        like = await self.collection.find_one({
            "user_id": user_id,
            "video_id": video_id
        })
        return like is not None


class DatabaseOperations:
    """Combined database operations for easy dependency injection."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.videos = VideoDAO(db)
        self.users = UserDAO(db)
        self.likes = LikeDAO(db)

    async def create_indexes(self) -> dict[str, bool]:
        """Create all necessary indexes."""
        results = {}

        try:
            # TTL index for video expiration
            await self.db.videos.create_index(
                "expires_at",
                expireAfterSeconds=0,
                name="ttl_expires_at"
            )
            results["videos_ttl"] = True
            logger.info("✅ Created TTL index on videos.expires_at")

        except Exception as e:
            logger.error(f"❌ Failed to create TTL index: {e}")
            results["videos_ttl"] = False

        try:
            # Compound index for borough + created_at queries
            await self.db.videos.create_index(
                [("borough", 1), ("created_at", -1)],
                name="borough_created_at"
            )
            results["videos_compound"] = True
            logger.info("✅ Created compound index on videos.borough+created_at")

        except Exception as e:
            logger.error(f"❌ Failed to create compound index: {e}")
            results["videos_compound"] = False

        try:
            # Index for like uniqueness
            await self.db.likes.create_index(
                [("user_id", 1), ("video_id", 1)],
                unique=True,
                name="user_video_unique"
            )
            results["likes_unique"] = True
            logger.info("✅ Created unique index on likes.user_id+video_id")

        except Exception as e:
            logger.error(f"❌ Failed to create likes index: {e}")
            results["likes_unique"] = False

        return results


async def get_db_ops(db: AsyncIOMotorDatabase) -> DatabaseOperations:
    """Get database operations instance."""
    return DatabaseOperations(db)