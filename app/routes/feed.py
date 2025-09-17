"""Personalized video feed endpoint with MongoDB vector search."""
import logging
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.dao import DatabaseOperations, get_db_ops
from app.deps import get_database
from app.models import Borough, FeedResponse, VideoResponse, VALID_BOROUGHS
from app.local_media import get_media_manager
from app.utils.ranking import rank_videos_personalized, rank_videos_recency

logger = logging.getLogger(__name__)

router = APIRouter()

# Dependency injection
async def get_db_ops_dependency(db: AsyncIOMotorDatabase = Depends(get_database)) -> DatabaseOperations:
    """Get database operations dependency."""
    return await get_db_ops(db)


@router.get("/feed", response_model=FeedResponse)
async def get_personalized_feed(
    db_ops: DatabaseOperations = Depends(get_db_ops_dependency),
    borough: Borough = Query(..., description="NYC borough to filter by"),
    user_id: str = Query(..., description="User requesting the feed"),
    limit: int = Query(20, ge=1, le=50, description="Number of videos to return"),
    skip: int = Query(0, ge=0, description="Number of videos to skip (pagination)"),
    since_hours: int = Query(48, ge=1, le=168, description="Hours of content to consider"),
) -> FeedResponse:
    """Get personalized video feed for a user in a specific borough.

    This endpoint implements the core hackathon feature:
    1. Fetch user's taste profile (if any)
    2. If user has taste: Use vector search + time decay ranking
    3. If new user: Use recency-based ranking
    4. Generate presigned URLs for all videos
    5. Return ranked feed with metadata
    """
    logger.info(f"📱 Feed request: user={user_id}, borough={borough}, limit={limit}")

    # Validate borough
    if borough not in VALID_BOROUGHS:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "borough_invalid",
                "message": f"Invalid borough: {borough}",
                "allowed": VALID_BOROUGHS
            }
        )

    try:
        # Step 1: Get user profile
        logger.info(f"👤 Fetching user profile for {user_id}")
        user = await db_ops.users.get_user(user_id)

        # Step 2: Determine ranking strategy
        media_manager = get_media_manager()

        if user.taste.n > 0:
            # User has taste profile - use personalized ranking
            logger.info(f"🎯 Using personalized ranking (user has {user.taste.n} likes)")

            # Get candidates via vector search
            video_scores = await db_ops.videos.vector_search(
                query_vector=user.taste.embedding,
                borough=borough,
                limit=limit * 2,  # Get more candidates for better ranking
                since_hours=since_hours
            )

            if not video_scores:
                logger.info("No videos found via vector search, falling back to recency")
                # Fallback to recency if vector search returns nothing
                videos = await db_ops.videos.get_feed_videos(
                    borough=borough,
                    limit=limit,
                    skip=skip,
                    since_hours=since_hours
                )
                ranked_videos = rank_videos_recency(videos)
            else:
                # Apply personalized ranking
                ranked_videos = rank_videos_personalized(
                    video_scores,
                    decay_hours=24.0,
                    vector_weight=0.65
                )

        else:
            # New user - use recency-based ranking
            logger.info(f"📅 Using recency ranking (new user)")

            videos = await db_ops.videos.get_feed_videos(
                borough=borough,
                limit=limit * 2,  # Get more for potential diversity filtering
                skip=skip,
                since_hours=since_hours
            )

            ranked_videos = rank_videos_recency(videos, decay_hours=24.0)

        # Step 3: Apply pagination and limits
        paginated_videos = ranked_videos[skip:skip + limit]

        # Step 4: Generate URLs and create response
        logger.info(f"🔗 Generating URLs for {len(paginated_videos)} videos")
        video_responses = []

        for video, score_breakdown in paginated_videos:
            try:
                # Generate URL for each video
                media_url = media_manager.get_url_path(video.file_path)

                video_response = VideoResponse(
                    video_id=str(video.id) if video.id else "unknown",
                    media_url=media_url,
                    title=video.title or "Untitled Video",
                    tags=video.tags or [],
                    borough=video.borough,
                    created_at=video.created_at,
                    duration_sec=video.duration_sec
                )

                video_responses.append(video_response)

                # Log ranking explanation for debugging
                if logger.isEnabledFor(logging.DEBUG):
                    logger.debug(
                        f"Video ranked: {video.title} - "
                        f"final_score={score_breakdown['final_score']:.3f} "
                        f"(vector={score_breakdown['vector_score']:.3f}, "
                        f"time={score_breakdown['time_decay']:.3f})"
                    )

            except Exception as e:
                logger.error(f"❌ Failed to process video {video.id}: {e}")
                # Continue with other videos instead of failing entire request
                continue

        # Step 5: Calculate response metadata
        total_available = len(ranked_videos)
        has_more = skip + limit < total_available

        response = FeedResponse(
            videos=video_responses,
            total_count=len(video_responses),
            has_more=has_more
        )

        logger.info(
            f"✅ Feed generated: {len(video_responses)} videos, "
            f"personalized={user.taste.n > 0}, has_more={has_more}"
        )

        return response

    except Exception as e:
        logger.error(f"❌ Feed generation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to generate feed. Please try again."
        )


@router.get("/feed/{borough}/recent", response_model=FeedResponse)
async def get_recent_feed(
    borough: Borough,
    db_ops: DatabaseOperations = Depends(get_db_ops_dependency),
    limit: int = Query(20, ge=1, le=50),
    skip: int = Query(0, ge=0),
    since_hours: int = Query(24, ge=1, le=168),
) -> FeedResponse:
    """Get recent videos by recency only (no personalization).

    This is useful for:
    - Public/anonymous browsing
    - Testing without user profiles
    - Fallback when personalization fails
    """
    logger.info(f"📅 Recent feed request: borough={borough}, limit={limit}")

    if borough not in VALID_BOROUGHS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid borough: {borough}. Allowed: {VALID_BOROUGHS}"
        )

    try:
        # Get recent videos
        videos = await db_ops.videos.get_feed_videos(
            borough=borough,
            limit=limit,
            skip=skip,
            since_hours=since_hours
        )

        # Generate URLs
        media_manager = get_media_manager()
        video_responses = []

        for video in videos:
            try:
                media_url = media_manager.get_url_path(video.file_path)

                video_response = VideoResponse(
                    video_id=str(video.id) if video.id else "unknown",
                    media_url=media_url,
                    title=video.title or "Untitled Video",
                    tags=video.tags or [],
                    borough=video.borough,
                    created_at=video.created_at,
                    duration_sec=video.duration_sec
                )

                video_responses.append(video_response)

            except Exception as e:
                logger.error(f"❌ Failed to process video {video.id}: {e}")
                continue

        # Calculate if more videos are available
        # This is a simple approximation - in production you might want to count total
        has_more = len(video_responses) == limit

        response = FeedResponse(
            videos=video_responses,
            total_count=len(video_responses),
            has_more=has_more
        )

        logger.info(f"✅ Recent feed generated: {len(video_responses)} videos")
        return response

    except Exception as e:
        logger.error(f"❌ Recent feed generation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to generate recent feed. Please try again."
        )