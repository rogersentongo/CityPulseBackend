"""Pydantic models for API requests and responses."""
from datetime import datetime
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


# Enums and Constants
Borough = Literal["Manhattan", "Brooklyn", "Queens", "Bronx", "Staten Island"]
VALID_BOROUGHS = ["Manhattan", "Brooklyn", "Queens", "Bronx", "Staten Island"]


# Database Models (MongoDB documents)
class VideoDocument(BaseModel):
    """Video document model for MongoDB."""
    id: Optional[str] = Field(None, alias="_id")
    user_id: str = Field(..., description="User who uploaded the video")
    borough: Borough = Field(..., description="NYC borough")
    borough_source: Literal["manual", "gps"] = Field(..., description="How borough was determined")
    s3_key: str = Field(..., description="S3 object key for video file")
    media_url_ttl: Optional[datetime] = Field(None, description="When presigned URL expires")
    duration_sec: float = Field(default=0.0, description="Video duration in seconds")

    # Content processing results
    transcript: str = Field(default="", description="Audio transcription")
    multimodal_transcript: str = Field(default="", description="Fused ASR+vision+OCR text")
    visual_caption: str = Field(default="", description="Short visual description")
    visual_tags: list[str] = Field(default_factory=list, description="Scene/object tags")
    ocr_text: str = Field(default="", description="Text extracted from video frames")
    has_audio: bool = Field(default=True, description="Whether video contains audio")
    embedding_source: Literal["audio", "vision", "hybrid"] = Field(default="audio")

    # AI-generated metadata
    title: str = Field(default="", description="AI-generated title")
    tags: list[str] = Field(default_factory=list, description="Content tags")
    embedding: list[float] = Field(default_factory=list, description="1536-dim vector embedding")

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime = Field(..., description="TTL expiration (created_at + 24h)")

    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class UserDocument(BaseModel):
    """User document model for MongoDB."""
    id: str = Field(..., alias="_id", description="User ID")
    taste: "UserTaste" = Field(default_factory=lambda: UserTaste())

    class Config:
        populate_by_name = True


class UserTaste(BaseModel):
    """User taste profile for personalized ranking."""
    embedding: list[float] = Field(default_factory=list, description="Mean of liked video embeddings")
    n: int = Field(default=0, description="Number of likes contributing to taste")
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class LikeDocument(BaseModel):
    """Like document model for MongoDB."""
    id: Optional[str] = Field(None, alias="_id")
    user_id: str = Field(..., description="User who liked the video")
    video_id: str = Field(..., description="Video that was liked")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True


# API Request Models
class UploadRequest(BaseModel):
    """Upload request metadata (form fields)."""
    user_id: str = Field(..., description="User uploading the video")
    borough: Optional[Borough] = Field(None, description="Manual borough selection")
    auto_detect_borough: bool = Field(default=True, description="Auto-detect borough from GPS")


class LikeRequest(BaseModel):
    """Like video request."""
    user_id: str = Field(..., description="User liking the video")
    video_id: str = Field(..., description="Video to like")


class AskRequest(BaseModel):
    """Ask NYC RAG request."""
    query: str = Field(..., description="Natural language question")
    borough: Optional[Borough] = Field(None, description="Filter by borough")
    window_hours: int = Field(default=6, description="Time window for relevant content")


# API Response Models
class VideoResponse(BaseModel):
    """Video response for feed endpoints."""
    video_id: str = Field(..., description="Video ID")
    media_url: str = Field(..., description="Presigned URL for video playback")
    title: str = Field(..., description="Video title")
    tags: list[str] = Field(..., description="Content tags")
    borough: Borough = Field(..., description="NYC borough")
    created_at: datetime = Field(..., description="Upload timestamp")
    duration_sec: float = Field(..., description="Video duration")


class UploadResponse(BaseModel):
    """Upload completion response."""
    video_id: str = Field(..., description="Created video ID")
    media_url: str = Field(..., description="Presigned URL for immediate playback")
    borough: Borough = Field(..., description="Final borough assignment")
    borough_source: Literal["manual", "gps"] = Field(..., description="How borough was determined")
    title: str = Field(..., description="AI-generated title")
    tags: list[str] = Field(..., description="AI-generated tags")
    transcript: str = Field(..., description="Video transcription")


class FeedResponse(BaseModel):
    """Feed response with personalized videos."""
    videos: list[VideoResponse] = Field(..., description="Personalized video feed")
    total_count: int = Field(..., description="Total videos in feed")
    has_more: bool = Field(..., description="Whether more videos are available")


class LikeResponse(BaseModel):
    """Like operation response."""
    ok: bool = Field(default=True, description="Operation success")
    message: str = Field(default="Video liked successfully")


class AskResponse(BaseModel):
    """Ask NYC RAG response."""
    answer: str = Field(..., description="AI-generated summary")
    sources: list["AskSource"] = Field(..., description="Source videos used for answer")
    borough: Optional[Borough] = Field(None, description="Borough filter applied")


class AskSource(BaseModel):
    """Source video for Ask NYC response."""
    video_id: str = Field(..., description="Source video ID")
    title: str = Field(..., description="Video title")
    created_at: datetime = Field(..., description="Video timestamp")
    relevance_score: float = Field(..., description="Similarity score")


# Error Models
class ErrorResponse(BaseModel):
    """Standard error response."""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[dict[str, Any]] = Field(None, description="Additional error details")


class BoroughValidationError(BaseModel):
    """Borough validation error with suggestions."""
    error: str = Field(default="borough_required")
    message: str = Field(..., description="Error message")
    allowed: list[str] = Field(default=VALID_BOROUGHS, description="Valid borough values")
    provided: Optional[str] = Field(None, description="Value that was provided")