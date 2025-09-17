"""Base classes for LLM providers."""
from abc import ABC, abstractmethod
from typing import List

from pydantic import BaseModel


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
    async def generate_summary(self, context_docs: List[str], query: str) -> str:
        """Generate summary for Ask NYC feature."""
        pass