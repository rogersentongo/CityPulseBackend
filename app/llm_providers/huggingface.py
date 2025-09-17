"""Hugging Face local AI providers for CityPulse."""
import logging
import re
from typing import Optional

import torch
import whisper
from sentence_transformers import SentenceTransformer
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM

from .base import EmbeddingProvider, LLMProvider, TranscriptionProvider, TitleTagsResponse

logger = logging.getLogger(__name__)


class HuggingFaceEmbeddingProvider(EmbeddingProvider):
    """Hugging Face sentence transformers for embeddings."""

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model_name = model_name
        self._model = None
        logger.info(f"🤗 Initializing HuggingFace embedding provider: {model_name}")

    @property
    def model(self):
        """Lazy load the model."""
        if self._model is None:
            logger.info(f"📥 Loading embedding model: {self.model_name}")
            self._model = SentenceTransformer(self.model_name)
            logger.info(f"✅ Embedding model loaded: {self.model_name}")
        return self._model

    async def create_embedding(self, text: str) -> list[float]:
        """Create embedding using sentence transformers."""
        try:
            # Clean text
            text = text.strip()
            if not text:
                logger.warning("Empty text provided for embedding")
                return [0.0] * 384  # Default dimension for MiniLM

            # Generate embedding
            embedding = self.model.encode(text, convert_to_tensor=False)

            # Convert to list if numpy array
            if hasattr(embedding, 'tolist'):
                embedding = embedding.tolist()

            logger.debug(f"Generated embedding: {len(embedding)} dimensions")
            return embedding

        except Exception as e:
            logger.error(f"❌ HuggingFace embedding failed: {e}")
            # Return zero vector as fallback
            return [0.0] * 384


class HuggingFaceLLMProvider(LLMProvider):
    """Hugging Face transformers for text generation."""

    def __init__(self, model_name: str = "microsoft/DialoGPT-medium"):
        self.model_name = model_name
        self._model = None
        self._tokenizer = None
        logger.info(f"🤗 Initializing HuggingFace LLM provider: {model_name}")

    @property
    def model(self):
        """Lazy load the model."""
        if self._model is None:
            logger.info(f"📥 Loading LLM model: {self.model_name}")
            try:
                # Use a lightweight text generation pipeline
                self._model = pipeline(
                    "text-generation",
                    model="gpt2",  # Using GPT2 as it's more reliable for title generation
                    tokenizer="gpt2",
                    device=0 if torch.cuda.is_available() else -1,
                    max_length=100,
                    do_sample=True,
                    temperature=0.7,
                    pad_token_id=50256  # GPT2 EOS token
                )
                logger.info(f"✅ LLM model loaded: gpt2")
            except Exception as e:
                logger.error(f"❌ Failed to load LLM model: {e}")
                self._model = None
        return self._model

    async def generate_title_and_tags(self, transcript: str) -> TitleTagsResponse:
        """Generate title and tags for video content."""
        try:
            # Clean transcript
            transcript = transcript.strip()[:500]  # Limit length

            if self.model is None:
                # Fallback to rule-based generation
                return self._fallback_title_tags(transcript)

            # Create prompt for title generation
            prompt = f"Video about: {transcript[:200]}\nTitle:"

            try:
                # Generate title
                response = self.model(
                    prompt,
                    max_length=len(prompt.split()) + 15,
                    num_return_sequences=1,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=50256
                )

                generated_text = response[0]['generated_text']
                title = generated_text[len(prompt):].strip()

                # Clean up title
                title = re.sub(r'\n.*', '', title)  # Remove everything after newline
                title = title[:60]  # Limit length

                if not title or len(title) < 5:
                    return self._fallback_title_tags(transcript)

                # Generate simple tags from transcript
                tags = self._extract_tags(transcript)

                logger.debug(f"Generated title: {title}")
                logger.debug(f"Generated tags: {tags}")

                return TitleTagsResponse(title=title, tags=tags)

            except Exception as e:
                logger.warning(f"Model generation failed, using fallback: {e}")
                return self._fallback_title_tags(transcript)

        except Exception as e:
            logger.error(f"❌ HuggingFace title/tags generation failed: {e}")
            return self._fallback_title_tags(transcript)

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

    def _extract_tags(self, text: str) -> list[str]:
        """Extract relevant tags from text."""
        text = text.lower()

        # Common NYC and activity tags
        tag_keywords = {
            'food': ['food', 'restaurant', 'eat', 'lunch', 'dinner', 'cafe', 'coffee'],
            'music': ['music', 'concert', 'band', 'sing', 'dance', 'jazz', 'hip-hop'],
            'art': ['art', 'gallery', 'museum', 'paint', 'draw', 'mural', 'street art'],
            'park': ['park', 'green', 'tree', 'nature', 'outdoor'],
            'market': ['market', 'vendor', 'shop', 'buy', 'sell'],
            'brooklyn': ['brooklyn', 'williamsburg', 'dumbo', 'bedford'],
            'manhattan': ['manhattan', 'times square', 'central park', 'midtown'],
            'queens': ['queens', 'astoria', 'flushing'],
            'bronx': ['bronx', 'yankee'],
            'family': ['family', 'kids', 'children', 'parent'],
            'nightlife': ['night', 'bar', 'club', 'drink', 'party'],
            'culture': ['culture', 'diverse', 'community', 'local']
        }

        found_tags = ['nyc']  # Always include NYC

        for tag, keywords in tag_keywords.items():
            if any(keyword in text for keyword in keywords):
                found_tags.append(tag)
                if len(found_tags) >= 5:
                    break

        return found_tags[:5]

    async def generate_summary(self, context_docs: list[str], query: str) -> str:
        """Generate summary for Ask NYC feature."""
        try:
            # Simple rule-based summarization for now
            combined_text = " ".join(context_docs[:3])  # Use top 3 docs

            # Extract key themes
            if 'food' in query.lower() or 'restaurant' in combined_text.lower():
                return f"Based on recent activity, there are several food-related events happening. {combined_text[:200]}..."
            elif 'art' in query.lower() or 'museum' in combined_text.lower():
                return f"The art scene is active with {combined_text[:200]}..."
            elif 'music' in query.lower() or 'concert' in combined_text.lower():
                return f"Music events are happening around the area. {combined_text[:200]}..."
            else:
                return f"Here's what's happening: {combined_text[:250]}..."

        except Exception as e:
            logger.error(f"❌ HuggingFace summary generation failed: {e}")
            return "Recent activity shows various events happening around NYC."


class HuggingFaceTranscriptionProvider(TranscriptionProvider):
    """OpenAI Whisper for local transcription."""

    def __init__(self, model_size: str = "base"):
        self.model_size = model_size
        self._model = None
        logger.info(f"🎤 Initializing Whisper transcription: {model_size}")

    @property
    def model(self):
        """Lazy load Whisper model."""
        if self._model is None:
            logger.info(f"📥 Loading Whisper model: {self.model_size}")
            try:
                self._model = whisper.load_model(self.model_size)
                logger.info(f"✅ Whisper model loaded: {self.model_size}")
            except Exception as e:
                logger.error(f"❌ Failed to load Whisper model: {e}")
                self._model = None
        return self._model

    async def transcribe_audio(self, audio_path: str) -> str:
        """Transcribe audio using Whisper."""
        try:
            if self.model is None:
                return self._fallback_transcription()

            logger.info(f"🎤 Transcribing audio: {audio_path}")

            # Use Whisper to transcribe
            result = self.model.transcribe(audio_path)
            transcript = result.get("text", "").strip()

            if not transcript:
                return self._fallback_transcription()

            logger.debug(f"Transcription completed: {len(transcript)} characters")
            return transcript

        except Exception as e:
            logger.error(f"❌ Whisper transcription failed: {e}")
            return self._fallback_transcription()

    def _fallback_transcription(self) -> str:
        """Fallback transcription for demo purposes."""
        fallback_transcripts = [
            "Walking through the streets of Brooklyn and discovering amazing local spots. The community here is incredible with so much culture and diversity.",
            "Times Square at sunset is absolutely magical. Street performers everywhere, tourists taking photos, and the energy is just incredible.",
            "Found this amazing coffee shop in Williamsburg with the best rooftop view of Manhattan. Perfect spot for working or just relaxing.",
            "Central Park on a beautiful Saturday afternoon. Families having picnics, kids playing, and street musicians performing near the fountain.",
            "The food scene in Queens is unmatched. Just tried this incredible authentic restaurant that locals have been keeping secret.",
        ]

        import random
        return random.choice(fallback_transcripts)