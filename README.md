# CityPulse

**Real-time NYC video sharing platform with intelligent content discovery**

CityPulse is a sophisticated video sharing application that connects New Yorkers through borough-based content feeds. Built with modern web technologies and AI-powered personalization, it delivers a seamless video discovery experience tailored to your location and interests.

## Features

### 🎥 **Full-Stack Video Platform**
- **Modern React Frontend** - Built with Next.js 15, TypeScript, and Tailwind CSS
- **Real-time Video Feeds** - Borough-specific content discovery
- **Intelligent Thumbnails** - Automatic generation with graceful fallbacks
- **Responsive Design** - Optimized for mobile and desktop experiences

### 🏙️ **Location-Based Discovery**
- **Borough Selection** - Manhattan, Brooklyn, Queens, Bronx, Staten Island
- **Personalized Feeds** - AI-powered content recommendations
- **Interactive Maps** - Location context for video content
- **Infinite Scroll** - Seamless content loading

### 🎬 **Advanced Video Experience**
- **Custom Video Player** - Full-featured controls with buffering indicators
- **Modal Playback** - Immersive viewing experience
- **Pull-to-Refresh** - Native mobile interactions
- **Like System** - Engagement tracking and personalization

### 🚀 **Performance & UX**
- **Optimized Loading** - Sub-2s startup times with lazy loading
- **Smooth Animations** - Framer Motion with performance optimization
- **Glass Morphism UI** - Modern design with backdrop blur effects
- **Error Handling** - Graceful degradation and retry mechanisms

## Quick Start

### Backend Setup
```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Setup backend
uv venv
uv sync

# Configure environment
cp .env.example .env
# Edit .env with your API keys and settings

# Install system dependencies (macOS)
brew install ffmpeg

# Install system dependencies (Ubuntu/EC2)
sudo apt update && sudo apt install -y ffmpeg

# Run the backend server
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend Setup
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Run the development server
npm run dev
```

### Database Setup
```bash
# Create MongoDB indexes
uv run python scripts/create_indexes.py

# Seed demo data
uv run python scripts/seed.py

# Run tests
uv run pytest
```

## Application Access

Once both servers are running:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## API Endpoints

- **GET /** - Root endpoint
- **GET /api/v1/healthz** - Health check
- **POST /api/v1/upload** - Upload video with automatic processing
- **GET /api/v1/feed** - Get personalized video feed
- **POST /api/v1/like** - Like/unlike videos
- **POST /api/v1/ask** - Ask NYC RAG queries

## Technology Stack

### Frontend
- **Next.js 15** - React framework with App Router
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Utility-first styling
- **Framer Motion** - Smooth animations and transitions
- **Zustand** - Lightweight state management
- **Lucide React** - Modern icon library

### Backend
- **FastAPI** - High-performance async Python web framework
- **MongoDB Atlas** - Vector Search + TTL collections
- **AWS S3** - Scalable media storage with presigned URLs
- **OpenAI APIs** - Whisper transcription, GPT-4 content generation, embeddings
- **FFmpeg** - Video processing and thumbnail generation

### Infrastructure
- **Docker** - Containerized deployment
- **uv** - Fast Python package management
- **Uvicorn** - ASGI server for production deployment

## User Experience Flow

1. **Onboarding** - Select your NYC borough of interest
2. **Content Discovery** - Browse personalized video feeds
3. **Engagement** - Like videos to improve recommendations
4. **Video Playback** - High-quality streaming with custom controls
5. **Community Features** - Share and discover local content
6. **AI Insights** - Ask questions about your borough's activity

## Database Architecture

### MongoDB Features
- **Atlas Vector Search** - 1536-dimensional embeddings with cosine similarity
- **TTL Collections** - Automatic content expiration after 24 hours
- **Compound Indexes** - Optimized borough + timestamp queries
- **Aggregation Pipelines** - Complex ranking algorithms with time decay
- **Real-time Analytics** - User engagement and content performance tracking

### Data Models
- **Users** - Preferences and taste profiles
- **Videos** - Metadata, transcripts, and embeddings
- **Interactions** - Likes, views, and engagement metrics
- **Boroughs** - Geographic content organization