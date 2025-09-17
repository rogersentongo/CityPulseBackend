"""Ollama local AI providers for CityPulse."""
import asyncio
import json
import logging
from typing import Any, Dict, List

import ollama

from .base import EmbeddingProvider, LLMProvider, TitleTagsResponse

logger = logging.getLogger(__name__)


class OllamaEmbeddingProvider(EmbeddingProvider):
    """Ollama embedding provider using local models."""

    def __init__(self, model_name: str = "nomic-embed-text", host: str = "http://localhost:11434"):
        self.model_name = model_name
        self.host = host
        self.client = ollama.AsyncClient(host=host)
        logger.info(f"🦙 Initializing Ollama embedding provider: {model_name} at {host}")

    async def create_embedding(self, text: str) -> List[float]:
        """Create embedding using Ollama."""
        try:
            # Clean text
            text = text.strip()
            if not text:
                logger.warning("Empty text provided for embedding")
                return [0.0] * 768  # Default dimension for nomic-embed-text

            logger.debug(f"🔢 Creating embedding for text: {len(text)} characters")

            # Generate embedding using Ollama
            response = await self.client.embeddings(
                model=self.model_name,
                prompt=text
            )

            embedding = response.get('embedding', [])

            if not embedding:
                logger.warning("Empty embedding returned from Ollama")
                return [0.0] * 768

            logger.debug(f"✅ Embedding created: {len(embedding)} dimensions")
            return embedding

        except Exception as e:
            logger.error(f"❌ Ollama embedding failed: {e}")
            # Return zero vector as fallback
            return [0.0] * 768


class OllamaLLMProvider(LLMProvider):
    """Ollama LLM provider for text generation."""

    def __init__(self, model_name: str = "llama3.2:3b", host: str = "http://localhost:11434"):
        self.model_name = model_name
        self.host = host
        self.client = ollama.AsyncClient(host=host)
        logger.info(f"🦙 Initializing Ollama LLM provider: {model_name} at {host}")

    async def generate_title_and_tags(self, transcript: str, context: str = "") -> TitleTagsResponse:
        """Generate title and tags using Ollama."""
        try:
            logger.info(f"🏷️  Generating title and tags for transcript: {len(transcript)} characters")

            # Truncate transcript if too long
            max_length = 1000
            truncated_transcript = transcript[:max_length] + "..." if len(transcript) > max_length else transcript

            system_prompt = """You are a title and tag generator for short NYC borough videos. Generate a catchy title (max 60 characters) and 3-5 relevant tags.

Focus on:
- NYC-specific locations and culture
- Key activities or events
- Emotional tone or atmosphere
- Avoid private info and profanity

Return ONLY valid JSON in this exact format: {"title": "Short catchy title", "tags": ["tag1", "tag2", "tag3"]}"""

            user_prompt = f"""Generate a title and tags for this NYC video transcript:

Transcript: {truncated_transcript}

{f"Additional context: {context}" if context else ""}

Return JSON with title and tags:"""

            response = await self.client.chat(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                options={
                    "temperature": 0.7,
                    "num_predict": 150,
                    "stop": ["\n\n", "```"]
                }
            )

            result_text = response['message']['content'].strip()

            # Try to extract JSON from the response
            try:
                # Remove any markdown formatting
                if "```json" in result_text:
                    result_text = result_text.split("```json")[1].split("```")[0].strip()
                elif "```" in result_text:
                    result_text = result_text.split("```")[1].split("```")[0].strip()

                result_data = json.loads(result_text)
                title = result_data.get("title", "NYC Video")[:60]  # Enforce length limit
                tags = result_data.get("tags", ["nyc"])[:5]  # Limit to 5 tags

                # Ensure tags are strings
                tags = [str(tag) for tag in tags]

            except (json.JSONDecodeError, KeyError) as e:
                logger.warning(f"Failed to parse JSON response, using fallback: {e}")
                return self._fallback_title_tags(transcript)

            logger.info(f"✅ Generated title: '{title}' and {len(tags)} tags")
            return TitleTagsResponse(title=title, tags=tags)

        except Exception as e:
            logger.error(f"❌ Ollama title/tags generation failed: {e}")
            return self._fallback_title_tags(transcript)

    async def generate_summary(self, query: str, video_contents: List[Dict[str, Any]]) -> str:
        """Generate summary for Ask NYC RAG feature using Ollama."""
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

            system_prompt = """You are a concise live-events summarizer for NYC. Given multiple short video clips from recent hours, provide a neutral 2-3 sentence summary of what's happening.

Guidelines:
- Focus on factual information from the videos
- Avoid speculation
- Mention specific locations when available
- Keep it concise but informative
- Return plain text (no markdown or formatting)"""

            user_prompt = f"""Query: "{query}"

Recent video clips from NYC:
{context}

Provide a 2-3 sentence summary of what's happening:"""

            response = await self.client.chat(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                options={
                    "temperature": 0.3,
                    "num_predict": 200
                }
            )

            summary = response['message']['content'].strip()

            # Clean up the response
            if not summary:
                return "Unable to generate summary at this time."

            logger.info(f"✅ Generated RAG summary: {len(summary)} characters")
            return summary

        except Exception as e:
            logger.error(f"❌ Ollama RAG summary generation failed: {e}")
            return "Unable to generate summary at this time."

    def _fallback_title_tags(self, transcript: str) -> TitleTagsResponse:
        """Fallback title and tags generation using rules."""
        # Extract key words and phrases
        words = transcript.lower().split()

        # NYC-related keywords
        nyc_keywords = {
            'manhattan', 'brooklyn', 'queens', 'bronx', 'staten island',
            'times square', 'central park', 'williamsburg', 'dumbo',
            'nyc', 'new york', 'city'
        }

        activity_keywords = {
            'food', 'music', 'art', 'street', 'park', 'market', 'festival',
            'coffee', 'restaurant', 'bar', 'shop', 'walk', 'sunset'
        }

        # Find relevant keywords
        found_nyc = [word for word in words if word in nyc_keywords]
        found_activities = [word for word in words if word in activity_keywords]

        # Generate title
        if found_nyc and found_activities:
            title = f"NYC {found_activities[0].title()}: {found_nyc[0].title()} Experience"
        elif found_nyc:
            title = f"{found_nyc[0].title()} Adventures"
        elif found_activities:
            title = f"NYC {found_activities[0].title()} Scene"
        else:
            title = "NYC Life: Urban Experience"

        # Generate tags
        tags = ['nyc', 'urban']
        tags.extend(found_nyc[:2])
        tags.extend(found_activities[:3])

        # Ensure we have at least 3 tags
        default_tags = ['life', 'city', 'culture', 'local', 'street']
        while len(tags) < 5:
            for tag in default_tags:
                if tag not in tags:
                    tags.append(tag)
                    break

        return TitleTagsResponse(title=title[:60], tags=tags[:5])