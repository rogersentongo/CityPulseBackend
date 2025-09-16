"""Like endpoint with user taste learning."""
import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.dao import DatabaseOperations, get_db_ops
from app.deps import get_database
from app.models import LikeRequest, LikeResponse

logger = logging.getLogger(__name__)

router = APIRouter()

# Dependency injection
async def get_db_ops_dependency(db: AsyncIOMotorDatabase = Depends(get_database)) -> DatabaseOperations:
    """Get database operations dependency."""
    return await get_db_ops(db)


@router.post("/like", response_model=LikeResponse)
async def like_video(
    request: LikeRequest,
    db_ops: DatabaseOperations = Depends(get_db_ops_dependency),
) -> LikeResponse:
    """Like a video and update user's taste profile.

    This is the core personalization feature for your hackathon demo:
    1. Validate that the video exists
    2. Create/update like record
    3. Update user's taste embedding (running average)
    4. Return success response

    The taste learning happens here - each like updates the user's
    preference vector, which affects future feed rankings.
    """
    logger.info(f"❤️ Like request: user={request.user_id}, video={request.video_id}")

    try:
        # Step 1: Validate video exists
        logger.info(f"🔍 Validating video {request.video_id}")
        video = await db_ops.videos.get_video(request.video_id)

        if not video:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "video_not_found",
                    "message": f"Video {request.video_id} not found or expired"
                }
            )

        # Step 2: Check if already liked
        already_liked = await db_ops.likes.user_has_liked(
            request.user_id,
            request.video_id
        )

        if already_liked:
            logger.info(f"👍 User {request.user_id} already liked video {request.video_id}")
            return LikeResponse(
                ok=True,
                message="Video already liked"
            )

        # Step 3: Create like record
        logger.info(f"💾 Creating like record")
        like_id = await db_ops.likes.create_like(
            request.user_id,
            request.video_id
        )

        # Step 4: Update user taste profile
        if video.embedding:
            logger.info(f"🧠 Updating user taste profile")

            # This is the key personalization logic!
            # Each like updates the running average of the user's taste
            updated_user = await db_ops.users.update_user_taste(
                request.user_id,
                video.embedding
            )

            logger.info(
                f"✅ User taste updated: {request.user_id} "
                f"(likes: {updated_user.taste.n})"
            )

            # Log some debugging info about the taste evolution
            if logger.isEnabledFor(logging.DEBUG):
                if updated_user.taste.n > 1:
                    # Calculate how much the taste changed
                    taste_magnitude = sum(x**2 for x in updated_user.taste.embedding)**0.5
                    logger.debug(
                        f"Taste profile stats: n={updated_user.taste.n}, "
                        f"magnitude={taste_magnitude:.3f}"
                    )

        else:
            logger.warning(
                f"⚠️ Video {request.video_id} has no embedding - "
                f"taste profile not updated"
            )

        logger.info(f"✅ Like processed successfully: {like_id}")

        return LikeResponse(
            ok=True,
            message="Video liked successfully"
        )

    except HTTPException:
        # Re-raise HTTP exceptions (validation errors)
        raise

    except Exception as e:
        logger.error(f"❌ Like processing failed: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to process like. Please try again."
        )


@router.delete("/like", response_model=LikeResponse)
async def unlike_video(
    request: LikeRequest,
    db_ops: DatabaseOperations = Depends(get_db_ops_dependency),
) -> LikeResponse:
    """Unlike a video (remove like).

    Note: This doesn't update the taste profile in reverse,
    as that would be complex to implement correctly.
    In a production system, you might track this differently.
    """
    logger.info(f"💔 Unlike request: user={request.user_id}, video={request.video_id}")

    try:
        # Check if like exists
        already_liked = await db_ops.likes.user_has_liked(
            request.user_id,
            request.video_id
        )

        if not already_liked:
            return LikeResponse(
                ok=True,
                message="Video was not liked"
            )

        # Remove like record
        # Note: This is a simplified implementation
        # In production, you'd want to track taste profile changes more carefully
        await db_ops.db.likes.delete_one({
            "user_id": request.user_id,
            "video_id": request.video_id
        })

        logger.info(f"✅ Like removed: user={request.user_id}, video={request.video_id}")

        return LikeResponse(
            ok=True,
            message="Video unliked successfully"
        )

    except Exception as e:
        logger.error(f"❌ Unlike processing failed: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to process unlike. Please try again."
        )


@router.get("/user/{user_id}/taste")
async def get_user_taste_profile(
    user_id: str,
    db_ops: DatabaseOperations = Depends(get_db_ops_dependency),
) -> dict:
    """Get user's taste profile for debugging/analytics.

    This endpoint is useful for:
    - Debugging personalization issues
    - Analytics dashboards
    - User profile pages
    """
    logger.info(f"👤 Taste profile request for user {user_id}")

    try:
        user = await db_ops.users.get_user(user_id)

        # Return sanitized taste profile
        taste_info = {
            "user_id": user_id,
            "likes_count": user.taste.n,
            "has_taste_profile": user.taste.n > 0,
            "last_updated": user.taste.updated_at.isoformat() if user.taste.updated_at else None,
            "embedding_dimensions": len(user.taste.embedding) if user.taste.embedding else 0,
            # Don't return the actual embedding for privacy/size reasons
        }

        # Add some basic statistics if we have a taste profile
        if user.taste.embedding:
            embedding = user.taste.embedding
            taste_info.update({
                "embedding_magnitude": (sum(x**2 for x in embedding) ** 0.5),
                "embedding_mean": sum(embedding) / len(embedding),
                "embedding_std": (
                    sum((x - taste_info["embedding_mean"])**2 for x in embedding) / len(embedding)
                ) ** 0.5,
            })

        logger.info(f"✅ Taste profile retrieved for {user_id}")
        return taste_info

    except Exception as e:
        logger.error(f"❌ Failed to get taste profile for {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve taste profile"
        )