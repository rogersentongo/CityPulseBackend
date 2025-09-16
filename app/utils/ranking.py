"""Personalized ranking algorithms for video feeds."""
import math
from datetime import datetime
from typing import Any

from app.models import VideoDocument


def calculate_time_decay(created_at: datetime, decay_hours: float = 24.0) -> float:
    """Calculate time decay factor for ranking.

    Args:
        created_at: When the video was created
        decay_hours: Half-life for time decay (default 24 hours)

    Returns:
        Time decay factor between 0 and 1
    """
    now = datetime.utcnow()
    hours_since = (now - created_at).total_seconds() / 3600.0

    # Exponential decay: decay_factor = exp(-hours_since / decay_hours)
    decay_factor = math.exp(-hours_since / decay_hours)
    return max(0.0, min(1.0, decay_factor))


def normalize_vector_score(score: float) -> float:
    """Normalize Atlas Vector Search score to [0, 1] range.

    MongoDB Atlas returns scores that can vary by similarity metric.
    For cosine similarity, scores are typically in [0, 1] already.
    """
    return max(0.0, min(1.0, score))


def calculate_final_score(
    vector_score: float,
    time_decay: float,
    vector_weight: float = 0.65,
    time_weight: float = 0.35,
) -> float:
    """Calculate final ranking score combining similarity and recency.

    Args:
        vector_score: Normalized vector similarity score [0, 1]
        time_decay: Time decay factor [0, 1]
        vector_weight: Weight for vector similarity (default 0.65)
        time_weight: Weight for time decay (default 0.35)

    Returns:
        Combined score [0, 1]
    """
    return (vector_weight * vector_score) + (time_weight * time_decay)


def rank_videos_personalized(
    video_scores: list[tuple[VideoDocument, float]],
    decay_hours: float = 24.0,
    vector_weight: float = 0.65,
) -> list[tuple[VideoDocument, dict[str, float]]]:
    """Rank videos using personalized algorithm.

    Args:
        video_scores: List of (video, vector_score) tuples
        decay_hours: Time decay half-life
        vector_weight: Weight for vector similarity vs time

    Returns:
        List of (video, score_breakdown) sorted by final score
    """
    ranked_videos = []

    for video, vector_score in video_scores:
        # Calculate components
        normalized_vector_score = normalize_vector_score(vector_score)
        time_decay = calculate_time_decay(video.created_at, decay_hours)
        final_score = calculate_final_score(
            normalized_vector_score,
            time_decay,
            vector_weight,
            1.0 - vector_weight
        )

        score_breakdown = {
            "vector_score": normalized_vector_score,
            "time_decay": time_decay,
            "final_score": final_score,
            "vector_weight": vector_weight,
            "time_weight": 1.0 - vector_weight,
        }

        ranked_videos.append((video, score_breakdown))

    # Sort by final score (descending)
    ranked_videos.sort(key=lambda x: x[1]["final_score"], reverse=True)

    return ranked_videos


def rank_videos_recency(
    videos: list[VideoDocument],
    decay_hours: float = 24.0,
) -> list[tuple[VideoDocument, dict[str, float]]]:
    """Rank videos by recency only (fallback for users without taste).

    Args:
        videos: List of videos to rank
        decay_hours: Time decay half-life

    Returns:
        List of (video, score_breakdown) sorted by recency
    """
    ranked_videos = []

    for video in videos:
        time_decay = calculate_time_decay(video.created_at, decay_hours)

        score_breakdown = {
            "vector_score": 0.0,  # No personalization
            "time_decay": time_decay,
            "final_score": time_decay,  # Pure recency ranking
            "vector_weight": 0.0,
            "time_weight": 1.0,
        }

        ranked_videos.append((video, score_breakdown))

    # Sort by time decay (most recent first)
    ranked_videos.sort(key=lambda x: x[1]["final_score"], reverse=True)

    return ranked_videos


def apply_diversity_filter(
    ranked_videos: list[tuple[VideoDocument, dict[str, float]]],
    max_same_tags: int = 3,
) -> list[tuple[VideoDocument, dict[str, float]]]:
    """Apply diversity filter to prevent too many videos with same tags.

    This is a simple MMR (Maximal Marginal Relevance) implementation.
    """
    if len(ranked_videos) <= max_same_tags:
        return ranked_videos

    # Track tag usage
    tag_counts: dict[str, int] = {}
    filtered_videos = []

    for video, scores in ranked_videos:
        # Check if adding this video would exceed tag limits
        video_tags = set(video.tags)
        max_tag_count = max(
            (tag_counts.get(tag, 0) for tag in video_tags),
            default=0
        )

        if max_tag_count < max_same_tags:
            # Add video and update tag counts
            filtered_videos.append((video, scores))
            for tag in video_tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1

    return filtered_videos


def explain_ranking(
    video: VideoDocument,
    scores: dict[str, float],
) -> str:
    """Generate human-readable explanation of ranking decision."""
    explanation_parts = []

    if scores["vector_weight"] > 0:
        explanation_parts.append(
            f"similarity: {scores['vector_score']:.2f} "
            f"(weight: {scores['vector_weight']:.1%})"
        )

    explanation_parts.append(
        f"recency: {scores['time_decay']:.2f} "
        f"(weight: {scores['time_weight']:.1%})"
    )

    explanation_parts.append(f"final: {scores['final_score']:.2f}")

    return f"Ranking for '{video.title}': {' + '.join(explanation_parts)}"