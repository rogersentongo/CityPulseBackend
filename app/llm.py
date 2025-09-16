"""LLM service layer with OpenAI integration and mock providers."""
import asyncio
import json
import logging
import tempfile
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from openai import AsyncOpenAI
from openai.types.audio import Transcription
from openai.types.chat import ChatCompletion
from openai.types.create_embedding_response import CreateEmbeddingResponse
from pydantic import BaseModel

from app.config import settings

logger = logging.getLogger(__name__)


class TitleTagsResponse(BaseModel):
    """Response model for title and tags generation."""
    title: str
    tags: List[str]


class TranscriptionProvider(ABC):
    """Abstract base class for audio transcription providers."""

    @abstractmethod
    async def transcribe_audio(self, audio_file_path: str) -> str:
        """Transcribe audio file to text."""
        pass


class EmbeddingProvider(ABC):
    """Abstract base class for text embedding providers."""

    @abstractmethod
    async def create_embedding(self, text: str) -> List[float]:
        """Create embedding vector for text."""
        pass


class LLMProvider(ABC):
    """Abstract base class for LLM text generation providers."""

    @abstractmethod
    async def generate_title_and_tags(self, transcript: str, context: str = "") -> TitleTagsResponse:
        """Generate title and tags from transcript."""
        pass

    @abstractmethod
    async def generate_summary(self, query: str, video_contents: List[Dict[str, Any]]) -> str:
        """Generate summary for Ask NYC feature."""
        pass


class OpenAITranscriptionProvider(TranscriptionProvider):
    """OpenAI Whisper transcription provider."""

    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)

    async def transcribe_audio(self, audio_file_path: str) -> str:
        """Transcribe audio using OpenAI Whisper."""
        try:
            logger.info(f"🎤 Starting Whisper transcription for {audio_file_path}")

            with open(audio_file_path, "rb") as audio_file:
                transcription: Transcription = await self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="text",
                    language="en",  # Optimize for English in NYC
                    prompt="This is a short video from New York City. Include proper nouns and place names."
                )

                # Whisper returns text directly when format is "text"
                transcript_text = str(transcription) if isinstance(transcription, str) else transcription.text

                logger.info(f"✅ Whisper transcription completed: {len(transcript_text)} characters")
                return transcript_text

        except Exception as e:
            logger.error(f"❌ Whisper transcription failed: {e}")
            return ""


class OpenAIEmbeddingProvider(EmbeddingProvider):
    """OpenAI text embedding provider."""

    def __init__(self, api_key: str, model: str = "text-embedding-3-small"):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model

    async def create_embedding(self, text: str) -> List[float]:
        """Create embedding using OpenAI."""
        try:
            logger.info(f"🔢 Creating embedding for text: {len(text)} characters")

            response: CreateEmbeddingResponse = await self.client.embeddings.create(
                model=self.model,
                input=text.strip(),
                encoding_format="float"
            )

            embedding = response.data[0].embedding
            logger.info(f"✅ Embedding created: {len(embedding)} dimensions")
            return embedding

        except Exception as e:
            logger.error(f"❌ Embedding creation failed: {e}")
            return []


class OpenAILLMProvider(LLMProvider):
    """OpenAI GPT provider for text generation."""

    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model

    async def generate_title_and_tags(self, transcript: str, context: str = "") -> TitleTagsResponse:
        """Generate title and tags using GPT."""
        try:
            logger.info(f"🏷️  Generating title and tags for transcript: {len(transcript)} characters")

            # Truncate transcript if too long
            max_length = 1000
            truncated_transcript = transcript[:max_length] + "..." if len(transcript) > max_length else transcript

            system_prompt = """Generate a short, catchy title (<= 60 chars) and 3-5 concise tags for a short NYC borough story based on the transcript.

Focus on:
- NYC-specific locations and culture
- Key activities or events
- Emotional tone or atmosphere
- Avoid private info and profanity

Return valid JSON: {"title": "...", "tags": ["...", "..."]}"""

            user_prompt = f"""Transcript: {truncated_transcript}

{f"Context: {context}" if context else ""}

Generate title and tags as JSON:"""

            response: ChatCompletion = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=150,
                response_format={"type": "json_object"}
            )

            result_text = response.choices[0].message.content or "{}"
            result_data = json.loads(result_text)

            title = result_data.get("title", "NYC Video")[:60]  # Enforce length limit
            tags = result_data.get("tags", ["nyc"])[:5]  # Limit to 5 tags

            logger.info(f"✅ Generated title: '{title}' and {len(tags)} tags")
            return TitleTagsResponse(title=title, tags=tags)

        except Exception as e:
            logger.error(f"❌ Title/tags generation failed: {e}")
            return TitleTagsResponse(title="NYC Video", tags=["nyc"])

    async def generate_summary(self, query: str, video_contents: List[Dict[str, Any]]) -> str:
        """Generate summary for Ask NYC RAG feature."""
        try:
            logger.info(f"📝 Generating RAG summary for query: '{query}' with {len(video_contents)} videos")

            if not video_contents:
                return "No recent videos found for this query."

            # Format video content for the prompt
            video_summaries = []
            for i, video in enumerate(video_contents[:10], 1):  # Limit to top 10
                title = video.get('title', 'Untitled')
                transcript = video.get('transcript', '')
                tags = ', '.join(video.get('tags', []))
                created_at = video.get('created_at', '')

                summary = f"{i}. \"{title}\" ({created_at})\n   Tags: {tags}\n   Content: {transcript[:200]}{'...' if len(transcript) > 200 else ''}"
                video_summaries.append(summary)

            context = "\n\n".join(video_summaries)

            system_prompt = """You are a concise live-events summarizer for NYC. Given multiple short clips from the last few hours, produce a neutral 2-3 sentence "what's happening" summary with concrete details.

Guidelines:
- Focus on factual information from the videos
- Avoid speculation
- Mention specific locations when available
- Keep it concise but informative
- Return plain text (no markdown)"""

            user_prompt = f"""Query: "{query}"

Recent video clips:
{context}

Provide a 2-3 sentence summary of what's happening:"""

            response: ChatCompletion = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=200
            )

            summary = response.choices[0].message.content or "Unable to generate summary."
            logger.info(f"✅ Generated RAG summary: {len(summary)} characters")
            return summary

        except Exception as e:
            logger.error(f"❌ RAG summary generation failed: {e}")
            return "Unable to generate summary at this time."


# Mock Providers for Development
class MockTranscriptionProvider(TranscriptionProvider):
    """Mock transcription provider for development."""

    async def transcribe_audio(self, audio_file_path: str) -> str:
        """Mock transcription with realistic content."""
        await asyncio.sleep(1)  # Simulate processing time

        # Generate different mock transcripts for variety
        mock_transcripts = [
            "Just walking through Williamsburg and the energy here is incredible. Street art everywhere, amazing coffee shops, and the view of Manhattan from the waterfront is breathtaking.",
            "Caught this amazing street performance in Washington Square Park. The musician was playing jazz guitar and everyone stopped to listen. This is why I love NYC.",
            "Food truck festival in Brooklyn Bridge Park today. Tried some amazing tacos and the weather is perfect. Manhattan skyline looks incredible from here.",
            "Weekend farmers market in Union Square. Fresh produce, local vendors, and great atmosphere. Love how diverse this city is.",
            "Sunset from the High Line is unreal. Walking through Chelsea and Meatpacking District, watching the Hudson River. NYC never gets old.",
        ]

        import random
        transcript = random.choice(mock_transcripts)

        logger.info(f"🎭 Mock transcription: {transcript[:50]}...")
        return transcript


class MockEmbeddingProvider(EmbeddingProvider):
    """Mock embedding provider for development."""

    async def create_embedding(self, text: str) -> List[float]:
        """Generate mock embedding vector."""
        await asyncio.sleep(0.2)  # Simulate API call

        # Generate a realistic-looking embedding based on text content
        import hashlib
        import random

        # Use text hash for deterministic but varied embeddings
        text_hash = hashlib.md5(text.encode()).hexdigest()
        random.seed(text_hash)

        # Generate 1536-dimensional embedding (matching text-embedding-3-small)
        embedding = [random.uniform(-1, 1) for _ in range(1536)]

        # Normalize to unit vector (more realistic)
        magnitude = sum(x**2 for x in embedding) ** 0.5
        embedding = [x / magnitude for x in embedding]

        logger.info(f"🎭 Mock embedding: {len(embedding)} dimensions")
        return embedding


class MockLLMProvider(LLMProvider):
    """Mock LLM provider for development."""

    async def generate_title_and_tags(self, transcript: str, context: str = "") -> TitleTagsResponse:
        """Generate mock title and tags."""
        await asyncio.sleep(0.5)  # Simulate API call

        # Extract keywords for more realistic titles
        keywords = transcript.lower().split()

        # Generate contextual title and tags
        if "brooklyn" in transcript.lower() or "williamsburg" in transcript.lower():
            title = "Brooklyn Vibes: Street Art & Coffee Culture"
            tags = ["brooklyn", "williamsburg", "street-art", "coffee", "culture"]
        elif "park" in transcript.lower():
            title = "NYC Park Life: Music & Community"
            tags = ["nyc", "park", "music", "community", "outdoor"]
        elif "food" in transcript.lower() or "restaurant" in transcript.lower():
            title = "NYC Food Scene: Amazing Local Eats"
            tags = ["nyc", "food", "restaurant", "local", "dining"]
        elif "manhattan" in transcript.lower():
            title = "Manhattan Moments: City Energy"
            tags = ["manhattan", "city", "urban", "energy", "nyc"]
        else:
            title = "NYC Life: Urban Adventures"
            tags = ["nyc", "urban", "life", "adventure", "city"]

        logger.info(f"🎭 Mock title: '{title}' and tags: {tags}")
        return TitleTagsResponse(title=title, tags=tags)

    async def generate_summary(self, query: str, video_contents: List[Dict[str, Any]]) -> str:
        """Generate mock summary."""
        await asyncio.sleep(0.3)

        if not video_contents:
            return "No recent videos found matching your query."

        # Generate contextual summary based on query
        if "williamsburg" in query.lower():
            summary = "Recent activity in Williamsburg shows vibrant street art scene and bustling coffee culture. Local artists have been active around Bedford Avenue, and several new cafés are drawing crowds with their rooftop views of Manhattan."
        elif "food" in query.lower():
            summary = "NYC's food scene is buzzing with weekend farmers markets and food truck festivals. Union Square and Brooklyn Bridge Park are seeing high activity with diverse vendors and fresh local produce."
        else:
            summary = f"Recent videos show active NYC life with street performances, outdoor activities, and community gatherings. The energy around parks and public spaces has been particularly vibrant in the past few hours."

        logger.info(f"🎭 Mock summary: {summary[:50]}...")
        return summary


class LLMService:
    """Main LLM service that coordinates all providers."""

    def __init__(self):
        self.transcription_provider = self._get_transcription_provider()
        self.embedding_provider = self._get_embedding_provider()
        self.llm_provider = self._get_llm_provider()

    def _get_transcription_provider(self) -> TranscriptionProvider:
        """Get transcription provider based on configuration."""
        if settings.transcribe_provider == "openai" and settings.openai_api_key:
            return OpenAITranscriptionProvider(settings.openai_api_key)
        else:
            logger.info("🎭 Using mock transcription provider")
            return MockTranscriptionProvider()

    def _get_embedding_provider(self) -> EmbeddingProvider:
        """Get embedding provider based on configuration."""
        if settings.embeddings_provider == "openai" and settings.openai_api_key:
            return OpenAIEmbeddingProvider(settings.openai_api_key, settings.embedding_model)
        else:
            logger.info("🎭 Using mock embedding provider")
            return MockEmbeddingProvider()

    def _get_llm_provider(self) -> LLMProvider:
        """Get LLM provider based on configuration."""
        if settings.llm_provider == "openai" and settings.openai_api_key:
            return OpenAILLMProvider(settings.openai_api_key, settings.llm_model)
        else:
            logger.info("🎭 Using mock LLM provider")
            return MockLLMProvider()

    async def process_video_audio(self, video_file_path: str) -> Tuple[str, List[float], str, List[str]]:
        """Complete audio processing pipeline.

        Returns:
            Tuple of (transcript, embedding, title, tags)
        """
        try:
            logger.info(f"🎬 Starting complete video audio processing for {video_file_path}")

            # Step 1: Extract audio and transcribe
            transcript = await self.transcription_provider.transcribe_audio(video_file_path)

            if not transcript:
                logger.warning("No transcript generated, using fallback")
                transcript = "Video content processed"

            # Step 2: Generate title and tags
            title_tags = await self.llm_provider.generate_title_and_tags(transcript)

            # Step 3: Create embedding from transcript
            embedding = await self.embedding_provider.create_embedding(transcript)

            logger.info(f"✅ Complete audio processing finished")
            return transcript, embedding, title_tags.title, title_tags.tags

        except Exception as e:
            logger.error(f"❌ Video audio processing failed: {e}")
            # Return safe fallbacks
            return (
                "Processing failed",
                [0.0] * 1536,  # Zero embedding
                "NYC Video",
                ["nyc", "video"]
            )

    async def generate_ask_nyc_summary(self, query: str, video_contents: List[Dict[str, Any]]) -> str:
        """Generate summary for Ask NYC feature."""
        return await self.llm_provider.generate_summary(query, video_contents)


# Global service instance
_llm_service: Optional[LLMService] = None


def get_llm_service() -> LLMService:
    """Get global LLM service instance."""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service