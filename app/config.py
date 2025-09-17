"""Application configuration using Pydantic Settings."""
from functools import lru_cache
from typing import Literal

from pydantic import Field, validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with validation."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # MongoDB Configuration
    mongo_uri: str = Field(..., description="MongoDB Atlas connection string")
    mongo_db: str = Field(default="citypulse", description="Database name")

    # OpenAI Configuration (optional for mock mode)
    openai_api_key: str = Field(default="", description="OpenAI API key")
    embedding_model: str = Field(default="text-embedding-3-small")
    llm_model: str = Field(default="gpt-4o-mini")
    transcribe_provider: Literal["openai", "mock"] = Field(default="mock")
    embeddings_provider: Literal["openai", "mock"] = Field(default="mock")
    llm_provider: Literal["openai", "mock"] = Field(default="mock")

    # Local Media Configuration
    media_base_path: str = Field(default="./app/media", description="Base path for local media storage")

    # API Configuration
    port: int = Field(default=8000)
    allow_origins: str = Field(default="*", description="CORS origins (comma-separated)")

    # Location Handling
    location_autodetect: bool = Field(default=True)
    borough_reject_if_unknown: bool = Field(default=True)

    # Multimodal Processing
    vision_provider: Literal["openai", "mock"] = Field(default="mock")
    ocr_provider: Literal["tesseract", "textract", "mock"] = Field(default="tesseract")
    frame_sample_fps: float = Field(default=0.5, description="Frames per second for video sampling")
    scene_detect: bool = Field(default=True)
    scene_threshold: float = Field(default=0.4)
    ocr_enable: bool = Field(default=True)
    ocr_langs: str = Field(default="eng")
    asr_timeout_s: int = Field(default=180)
    vision_timeout_s: int = Field(default=180)
    ocr_timeout_s: int = Field(default=120)

    @validator("allow_origins")
    def parse_origins(cls, v: str) -> list[str]:
        """Parse comma-separated origins."""
        return [origin.strip() for origin in v.split(",")]


    @property
    def is_mock_mode(self) -> bool:
        """Check if running in mock mode for all providers."""
        return (
            self.transcribe_provider == "mock"
            and self.embeddings_provider == "mock"
            and self.llm_provider == "mock"
        )


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()


# Global settings instance
settings = get_settings()