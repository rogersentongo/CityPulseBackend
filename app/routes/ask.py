"""Ask NYC RAG endpoint with LLM-powered summaries."""
import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.dao import DatabaseOperations, get_db_ops
from app.deps import get_database
from app.llm import get_llm_service
from app.models import AskRequest, AskResponse, AskSource, Borough, VALID_BOROUGHS

logger = logging.getLogger(__name__)

router = APIRouter()

# Dependency injection
async def get_db_ops_dependency(db: AsyncIOMotorDatabase = Depends(get_database)) -> DatabaseOperations:
    """Get database operations dependency."""
    return await get_db_ops(db)


@router.post("/ask", response_model=AskResponse)
async def ask_nyc(
    request: AskRequest,
    db_ops: DatabaseOperations = Depends(get_db_ops_dependency),
) -> AskResponse:
    """Ask NYC - RAG-powered Q&A about recent video content.

    This is the impressive AI feature for your demo:
    1. Embed user's natural language query
    2. Vector search against recent video transcripts
    3. Use LLM to generate coherent summary from top results
    4. Return answer with source videos

    Example queries:
    - "What's happening in Williamsburg right now?"
    - "Any food events in Brooklyn today?"
    - "Show me street art activities"
    """
    logger.info(f"❓ Ask NYC query: '{request.query}' (borough: {request.borough})")

    # Validate borough if provided
    if request.borough and request.borough not in VALID_BOROUGHS:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "borough_invalid",
                "message": f"Invalid borough: {request.borough}",
                "allowed": VALID_BOROUGHS
            }
        )

    try:
        # Get LLM service
        llm_service = get_llm_service()

        # Step 1: Create embedding for the query
        logger.info("🔢 Creating query embedding")
        query_embedding = await llm_service.embedding_provider.create_embedding(request.query)

        if not query_embedding:
            logger.warning("Failed to create query embedding, using text search fallback")
            # Fallback: get recent videos without vector search
            recent_videos = await db_ops.videos.get_feed_videos(
                borough=request.borough or "Manhattan",
                limit=10,
                since_hours=request.window_hours
            )
            video_sources = [(video, 0.5) for video in recent_videos]  # Mock scores
        else:
            # Step 2: Vector search for relevant videos
            logger.info(f"🔍 Vector searching for relevant videos (window: {request.window_hours}h)")
            video_sources = await db_ops.videos.get_videos_for_rag(
                query_vector=query_embedding,
                borough=request.borough,
                window_hours=request.window_hours,
                limit=10
            )

        if not video_sources:
            return AskResponse(
                answer="No recent videos found matching your query. Try expanding your time window or checking different boroughs.",
                sources=[],
                borough=request.borough
            )

        # Step 3: Prepare video content for LLM
        logger.info(f"📊 Found {len(video_sources)} relevant videos")
        video_contents = []

        for video, score in video_sources:
            video_content = {
                "video_id": str(video.id) if video.id else "unknown",
                "title": video.title or "Untitled",
                "transcript": video.transcript or "",
                "multimodal_transcript": video.multimodal_transcript or video.transcript or "",
                "tags": video.tags or [],
                "created_at": video.created_at.isoformat() if video.created_at else "",
                "borough": video.borough,
                "relevance_score": score
            }
            video_contents.append(video_content)

        # Step 4: Generate LLM summary
        logger.info("🤖 Generating AI summary")
        answer = await llm_service.generate_ask_nyc_summary(request.query, video_contents)

        # Step 5: Create source references
        sources = []
        for video, score in video_sources[:5]:  # Limit to top 5 sources
            source = AskSource(
                video_id=str(video.id) if video.id else "unknown",
                title=video.title or "Untitled Video",
                created_at=video.created_at,
                relevance_score=score
            )
            sources.append(source)

        response = AskResponse(
            answer=answer,
            sources=sources,
            borough=request.borough
        )

        logger.info(f"✅ Ask NYC completed: {len(answer)} char answer, {len(sources)} sources")
        return response

    except Exception as e:
        logger.error(f"❌ Ask NYC failed: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to process your question. Please try again."
        )


@router.get("/ask-suggestions")
async def get_ask_suggestions(
    borough: Borough = Query(..., description="Borough to get suggestions for")
) -> dict:
    """Get suggested Ask NYC questions for a borough.

    This helps users understand what kinds of questions they can ask
    and showcases the RAG capabilities.
    """
    logger.info(f"💡 Getting Ask suggestions for {borough}")

    if borough not in VALID_BOROUGHS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid borough: {borough}"
        )

    # Borough-specific suggestions
    suggestions = {
        "Manhattan": [
            "What's happening in Times Square right now?",
            "Any street performances in Washington Square Park?",
            "Show me food activities in the Village",
            "What's the vibe in Central Park today?",
            "Any art events happening in SoHo?"
        ],
        "Brooklyn": [
            "What's happening in Williamsburg right now?",
            "Any food events in DUMBO today?",
            "Show me street art activities in Bushwick",
            "What's going on at Brooklyn Bridge Park?",
            "Any music events in Park Slope?"
        ],
        "Queens": [
            "What's happening in Astoria today?",
            "Any cultural events in Flushing?",
            "Show me food activities in Long Island City",
            "What's the scene in Jackson Heights?",
            "Any events at Gantry Plaza State Park?"
        ],
        "Bronx": [
            "What's happening in the South Bronx?",
            "Any events at Yankee Stadium area?",
            "Show me activities in the Bronx Zoo area",
            "What's going on in Fordham?",
            "Any cultural events happening?"
        ],
        "Staten Island": [
            "What's happening at the Staten Island Ferry?",
            "Any events in St. George?",
            "Show me activities near the boardwalk",
            "What's going on in Richmond Town?",
            "Any nature activities happening?"
        ]
    }

    return {
        "borough": borough,
        "suggestions": suggestions[borough],
        "tip": "Ask about specific activities, locations, or current events to get the best results!"
    }