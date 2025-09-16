# CityPulse Backend

**NYC 24-hour borough-based video feed with MongoDB Atlas Vector Search**

> Built for MongoDB Demopalooza at AI Tinkerers NYC

## Quick Start

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Setup project
uv venv
uv sync

# Configure environment
cp .env.example .env
# Edit .env with your API keys and settings

# Install system dependencies (macOS)
brew install ffmpeg

# Install system dependencies (Ubuntu/EC2)
sudo apt update && sudo apt install -y ffmpeg

# Run the development server
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Run tests
uv run pytest

# Create MongoDB indexes
uv run python scripts/create_indexes.py

# Seed demo data
uv run python scripts/seed.py
```

## API Endpoints

- **GET /** - Root endpoint
- **GET /api/v1/healthz** - Health check
- **POST /api/v1/upload** - Upload video (coming next)
- **GET /api/v1/feed** - Get personalized feed (coming next)
- **POST /api/v1/like** - Like a video (coming next)
- **POST /api/v1/ask** - Ask NYC RAG queries (Phase 2)

## Architecture

- **FastAPI** - Modern async Python web framework
- **MongoDB Atlas** - Vector Search + TTL collections
- **AWS S3** - Private media storage with presigned URLs
- **OpenAI** - Whisper transcription, GPT-4 titles/tags, embeddings
- **Docker** - Containerized deployment

## Demo Flow (5 minutes)

1. **Browse Brooklyn feed** - Show borough-based content
2. **Like 2-3 videos** - Demonstrate taste learning
3. **Refresh feed** - Show personalized reordering
4. **Ask "What's happening in Williamsburg?"** - RAG summary
5. **Upload new video** - End-to-end processing

## MongoDB Features Showcased

- **Atlas Vector Search** - 1536-dim embeddings with cosine similarity
- **TTL Collections** - Auto-expire videos after 24 hours
- **Compound Indexes** - Borough + timestamp for fast queries
- **Aggregation Pipeline** - Complex ranking with time decay

Built with ❤️ for the MongoDB community.