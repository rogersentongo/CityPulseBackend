"""Video upload endpoint with processing pipeline."""
import logging
from datetime import datetime, timedelta
from typing import Annotated, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, UploadFile
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.dao import get_db_ops, DatabaseOperations
from app.deps import get_database
from app.models import Borough, UploadResponse, VideoDocument, VALID_BOROUGHS
from app.s3media import get_s3_manager
from app.utils.upload import get_upload_handler
from app.utils.video import get_video_processor

logger = logging.getLogger(__name__)

router = APIRouter()

# Type aliases for cleaner dependency injection
async def get_db_ops_dependency(db: AsyncIOMotorDatabase = Depends(get_database)) -> DatabaseOperations:
    """Get database operations dependency."""
    return await get_db_ops(db)


async def process_video_pipeline(
    video_id: str,
    temp_file_path: str,
    s3_key: str,
    user_id: str,
    borough: Borough,
    borough_source: str,
    db_ops: DatabaseOperations,
) -> None:
    """Background task to process video after upload.

    This runs the complete AI processing pipeline:
    1. Audio transcription (Whisper)
    2. Title and tags generation (GPT)
    3. Text embedding generation (text-embedding-3-small)
    4. Database update with results
    """
    try:
        logger.info(f"🔄 Starting video processing pipeline for video {video_id}")

        # Run AI processing
        await process_video_with_ai(
            video_id=video_id,
            temp_file_path=temp_file_path,
            s3_key=s3_key,
            user_id=user_id,
            borough=borough,
            db_ops=db_ops
        )

        logger.info(f"✅ Video processing pipeline completed for {video_id}")

    except Exception as e:
        logger.error(f"❌ Video processing pipeline failed for {video_id}: {e}")
        # In production, you might want to implement retry logic
        # or move failed videos to a dead letter queue

    finally:
        # Cleanup temp file
        from app.utils.upload import get_upload_handler
        upload_handler = get_upload_handler()
        upload_handler.cleanup_temp_file(temp_file_path)


async def process_video_with_ai(
    video_id: str,
    temp_file_path: str,
    s3_key: str,
    user_id: str,
    borough: Borough,
    db_ops: DatabaseOperations,
) -> None:
    """Real AI video processing pipeline."""
    from app.llm import get_llm_service

    try:
        logger.info(f"🤖 Starting AI processing for video {video_id}")

        # Get LLM service
        llm_service = get_llm_service()

        # Process video audio with AI
        transcript, embedding, title, tags = await llm_service.process_video_audio(temp_file_path)

        # Update video document with AI results
        video = await db_ops.videos.get_video(video_id)
        if video:
            # Update the video with AI-generated content
            update_data = {
                "transcript": transcript,
                "multimodal_transcript": transcript,  # For Phase 1, same as transcript
                "title": title,
                "tags": tags,
                "embedding": embedding,
                "embedding_source": "audio"
            }

            await db_ops.db.videos.update_one(
                {"_id": video_id},
                {"$set": update_data}
            )

            logger.info(f"✅ AI processing completed for video {video_id}: '{title}'")
        else:
            logger.error(f"❌ Video {video_id} not found for AI update")

    except Exception as e:
        logger.error(f"❌ AI processing failed for video {video_id}: {e}")
        # Update video with error status
        try:
            await db_ops.db.videos.update_one(
                {"_id": video_id},
                {"$set": {
                    "transcript": "Processing failed",
                    "title": "Processing Error",
                    "tags": ["error"],
                    "embedding": [0.0] * 1536
                }}
            )
        except Exception as update_error:
            logger.error(f"❌ Failed to update video with error status: {update_error}")


def resolve_borough_from_gps(gps_coords: Optional[tuple[float, float]]) -> Optional[Borough]:
    """Resolve NYC borough from GPS coordinates.

    For Phase 1, we'll use a simple implementation.
    In production, this would use Shapely with NYC borough polygons.
    """
    if not gps_coords:
        return None

    lat, lon = gps_coords

    # Simple bounding box approach for Phase 1
    # These are approximate bounds for NYC boroughs
    if 40.7000 <= lat <= 40.8000 and -74.0200 <= lon <= -73.9000:
        return "Manhattan"
    elif 40.6000 <= lat <= 40.7500 and -74.0500 <= lon <= -73.8500:
        return "Brooklyn"
    elif 40.7000 <= lat <= 40.8000 and -73.9500 <= lon <= -73.7000:
        return "Queens"
    elif 40.8000 <= lat <= 40.9000 and -73.9500 <= lon <= -73.8000:
        return "Bronx"
    elif 40.5000 <= lat <= 40.6500 and -74.2500 <= lon <= -74.0500:
        return "Staten Island"

    logger.warning(f"GPS coordinates {gps_coords} not within NYC boroughs")
    return None


@router.post("/upload", response_model=UploadResponse)
async def upload_video(
    background_tasks: BackgroundTasks,
    db_ops: DatabaseOperations = Depends(get_db_ops_dependency),
    file: UploadFile = File(..., description="Video file to upload"),
    user_id: str = Form(..., description="User uploading the video"),
    borough: Optional[str] = Form(None, description="Manual borough selection"),
    auto_detect_borough: bool = Form(True, description="Auto-detect borough from GPS"),
) -> UploadResponse:
    """Upload and process a video file.

    This endpoint handles the complete upload workflow:
    1. Validate and save uploaded file
    2. Extract video metadata and GPS coordinates
    3. Resolve borough (manual or GPS-based)
    4. Upload to S3
    5. Create database record
    6. Start background processing (transcription, AI processing)
    """
    logger.info(f"📤 Upload request from user {user_id}")

    # Validate borough if provided
    if borough and borough not in VALID_BOROUGHS:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "borough_invalid",
                "message": f"Invalid borough: {borough}",
                "allowed": VALID_BOROUGHS,
                "provided": borough
            }
        )

    # Initialize services
    upload_handler = get_upload_handler()
    video_processor = get_video_processor()
    s3_manager = get_s3_manager()

    temp_file_path: Optional[str] = None

    try:
        # Step 1: Save and validate uploaded file
        logger.info("💾 Saving uploaded file to temporary location")
        temp_file_path = await upload_handler.save_temp_file(file)

        # Step 2: Extract video metadata
        logger.info("🎬 Extracting video metadata")
        video_info = video_processor.get_video_info(temp_file_path)

        if not video_info.get('has_video'):
            raise HTTPException(
                status_code=400,
                detail="Invalid video file: no video stream found"
            )

        duration = video_info.get('duration', 0)
        if duration > 60:  # 60 second limit for Phase 1
            raise HTTPException(
                status_code=400,
                detail=f"Video too long: {duration}s (max 60s)"
            )

        # Step 3: Resolve borough
        final_borough: Optional[Borough] = None
        borough_source = "manual"

        if borough:
            # Manual borough takes precedence
            final_borough = borough
            borough_source = "manual"
            logger.info(f"📍 Using manual borough: {borough}")

        elif auto_detect_borough:
            # Try GPS extraction
            logger.info("🗺️ Attempting GPS extraction")
            gps_coords = video_processor.extract_gps_metadata(temp_file_path)

            if gps_coords:
                detected_borough = resolve_borough_from_gps(gps_coords)
                if detected_borough:
                    final_borough = detected_borough
                    borough_source = "gps"
                    logger.info(f"📍 Detected borough from GPS: {detected_borough}")
                else:
                    logger.warning("GPS coordinates found but not within NYC boroughs")

        # Validate that we have a borough
        if not final_borough:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "borough_required",
                    "message": "Borough is required. Provide manually or enable auto-detection",
                    "allowed": VALID_BOROUGHS
                }
            )

        # Step 4: Upload to S3
        logger.info("☁️ Uploading video to S3")
        s3_key = s3_manager.generate_s3_key(user_id, "mp4")

        with upload_handler.get_file_stream(temp_file_path) as file_stream:
            upload_result = await s3_manager.upload_video(
                file_stream,
                s3_key,
                content_type="video/mp4"
            )

        logger.info(f"✅ Video uploaded to S3: {s3_key}")

        # Step 5: Create video document
        logger.info("💾 Creating video database record")
        video_doc = VideoDocument(
            user_id=user_id,
            borough=final_borough,
            borough_source=borough_source,
            s3_key=s3_key,
            duration_sec=duration,
            has_audio=video_info.get('has_audio', True),
            # For Phase 1, we'll add placeholder content
            # These will be populated by the background processing
            transcript="Processing...",
            multimodal_transcript="Processing...",
            title="Processing video...",
            tags=["processing"],
            embedding=[],  # Will be populated by background task
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(hours=24)
        )

        video_id = await db_ops.videos.create_video(video_doc)
        logger.info(f"✅ Video record created: {video_id}")

        # Step 6: Generate presigned URL for immediate access
        media_url = s3_manager.generate_presigned_url(s3_key)

        # Step 7: Start background processing
        logger.info("🔄 Starting background video processing")
        background_tasks.add_task(
            process_video_pipeline,
            video_id,
            temp_file_path,
            s3_key,
            user_id,
            final_borough,
            borough_source,
            db_ops
        )

        # For Phase 1, return immediate response with placeholder data
        return UploadResponse(
            video_id=video_id,
            media_url=media_url,
            borough=final_borough,
            borough_source=borough_source,
            title="Processing video...",
            tags=["processing"],
            transcript="Video is being processed. Transcript will be available shortly."
        )

    except HTTPException:
        # Re-raise HTTP exceptions (validation errors)
        if temp_file_path:
            upload_handler.cleanup_temp_file(temp_file_path)
        raise

    except Exception as e:
        # Handle unexpected errors
        logger.error(f"❌ Upload failed: {e}")
        if temp_file_path:
            upload_handler.cleanup_temp_file(temp_file_path)

        raise HTTPException(
            status_code=500,
            detail="Video upload failed. Please try again."
        )