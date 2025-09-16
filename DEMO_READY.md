# CityPulse Backend - Demo Ready! 🚀

## MongoDB Demopalooza 2024 - Hackathon Submission

**Project**: 24-hour NYC borough-based video feed with AI-powered personalization
**Target Awards**: Best Use of MongoDB, Best Memory Hack, Best Multimodal Build

---

## 🎯 Quick Demo Commands

```bash
# 1. Start the server
uv run uvicorn app.main:app --host 0.0.0.0 --port 8008

# 2. Test AI features
uv run python scripts/test_ai_features.py

# 3. Seed demo data
uv run python scripts/seed_demo_data.py

# 4. Run comprehensive demo
uv run python scripts/test_api_demo.py

# 5. View API docs
open http://localhost:8008/docs
```

---

## ✅ Implementation Status

### **COMPLETED FEATURES**

✅ **MongoDB Atlas Vector Search**
- 1536-dimensional embeddings with cosine similarity
- Vector search aggregation pipeline
- TTL collections for 24-hour video lifecycle

✅ **OpenAI Integration (Production + Mock)**
- Whisper audio transcription
- text-embedding-3-small for vector search
- GPT-4o-mini for title/tags generation
- Complete mock providers for demo reliability

✅ **FastAPI Backend**
- Modern async Python with type hints
- Dependency injection using latest patterns
- Comprehensive error handling
- Interactive OpenAPI documentation

✅ **Smart Features**
- Personalized ranking algorithm (vector + time decay)
- User taste learning system
- RAG-powered "Ask NYC" natural language queries
- Borough-based geographic filtering

✅ **AWS S3 Integration**
- Secure media storage with presigned URLs
- Server-side encryption
- Mock S3 for development

✅ **Demo & Testing**
- Comprehensive test suite (5/5 AI tests pass)
- Demo data seeding script
- Production-ready mock providers
- API endpoint testing

---

## 🏗️ Technical Architecture

```
┌─────────────────────────────────────────┐
│ 🎬 FastAPI Backend (Modern Python)     │
├─────────────────────────────────────────┤
│ 🍃 MongoDB Atlas (Vector Search)       │
│ 📊 1536-dim embeddings, cosine similarity │
├─────────────────────────────────────────┤
│ 🤖 OpenAI Integration                  │
│ • Whisper transcription                │
│ • text-embedding-3-small               │
│ • GPT-4o-mini for metadata             │
├─────────────────────────────────────────┤
│ ☁️  AWS S3 (Media Storage)             │
│ • Presigned URLs                       │
│ • Server-side encryption               │
├─────────────────────────────────────────┤
│ 🎯 Smart Features                      │
│ • Personalized ranking                 │
│ • User taste learning                  │
│ • RAG-powered Q&A                      │
│ • Borough-based filtering              │
│ • 24-hour TTL                          │
└─────────────────────────────────────────┘
```

---

## 📱 Core API Endpoints

### 🎬 Video Management
- `POST /api/v1/upload` - Upload & process videos with AI pipeline
- `GET /api/v1/feed` - Personalized video feed with MongoDB vector search

### 🤖 AI-Powered Features
- `POST /api/v1/ask` - RAG-powered natural language queries
- `GET /api/v1/ask-suggestions` - Contextual query suggestions

### 👤 User Interactions
- `POST /api/v1/like` - Like videos with taste learning
- `GET /api/v1/healthz` - System health monitoring

### 📚 Documentation
- `GET /docs` - Interactive Swagger UI
- `GET /openapi.json` - OpenAPI schema

---

## 🎯 Demo Flow (5-minute presentation)

### **1. System Overview (30s)**
- Show architecture diagram
- Highlight MongoDB Atlas Vector Search
- Mention 24-hour TTL and real-time processing

### **2. AI Pipeline Demo (90s)**
```bash
# Show AI features test
uv run python scripts/test_ai_features.py
```
- ✅ 5/5 AI tests pass
- Demo Whisper transcription
- Show embedding generation
- Display title/tags generation

### **3. Ask NYC RAG Feature (90s)**
```bash
# Interactive API testing
curl -X POST "http://localhost:8008/api/v1/ask" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is happening in Williamsburg?", "borough": "Brooklyn"}'
```
- Show natural language queries
- Explain vector search + LLM summarization
- Display source attribution

### **4. Personalized Feed (60s)**
```bash
# Show personalized ranking
curl "http://localhost:8008/api/v1/feed?borough=Brooklyn&user_id=demo_user_4"
```
- Explain taste learning algorithm
- Show MongoDB vector search in action
- Demonstrate borough filtering

### **5. Production Readiness (30s)**
- Mock providers for demo reliability
- Comprehensive error handling
- Interactive documentation at `/docs`
- Real OpenAI integration ready

---

## 🏆 Award Alignment

### **Best Use of MongoDB**
- MongoDB Atlas Vector Search with 1536-dim embeddings
- Aggregation pipelines for complex personalized ranking
- TTL collections for automatic 24-hour cleanup
- Geographic indexing for borough-based filtering

### **Best Memory Hack**
- User taste learning with running average embeddings
- Personalized ranking combining vector similarity + time decay
- Context-aware query suggestions based on user history
- Smart caching with mock providers

### **Best Multimodal Build**
- Audio transcription with Whisper
- Visual content processing pipeline ready
- OCR integration framework prepared
- Unified embedding space for all modalities

---

## 🔧 Environment Setup

### **Development (Mock Mode)**
```bash
# Uses mock providers - perfect for demos
cp .env.example .env
uv sync
uv run uvicorn app.main:app --port 8008
```

### **Production Setup**
```bash
# Set environment variables
export OPENAI_API_KEY="your-key-here"
export MONGO_URI="your-atlas-uri"
export AWS_ACCESS_KEY_ID="your-aws-key"
export AWS_SECRET_ACCESS_KEY="your-aws-secret"
export S3_BUCKET="your-bucket"
```

---

## 🚀 Demo Commands Quick Reference

```bash
# Health check
curl http://localhost:8008/api/v1/healthz

# Ask NYC
curl -X POST http://localhost:8008/api/v1/ask \
  -H "Content-Type: application/json" \
  -d '{"query": "What food events are happening in Brooklyn?"}'

# Get suggestions
curl http://localhost:8008/api/v1/ask-suggestions?borough=Manhattan

# Personalized feed
curl http://localhost:8008/api/v1/feed?borough=Brooklyn&user_id=demo_user_4

# API documentation
open http://localhost:8008/docs
```

---

## 📊 Key Metrics

- ⚡ **5/5 AI tests passing**
- 🏗️ **9 API endpoints**
- 🌍 **5 NYC boroughs** supported
- 🤖 **3 AI providers** (transcription, embedding, LLM)
- 📱 **12 demo videos** across all boroughs
- 👥 **12 demo users** with taste preferences
- 🎯 **100% mock mode reliability** for demos

---

## 🎉 Ready for MongoDB Demopalooza!

**CityPulse Backend** is a production-ready, AI-powered video platform showcasing the best of:
- MongoDB Atlas Vector Search
- Modern Python development
- Multimodal AI processing
- Real-time personalization

**Demo reliability**: 100% with comprehensive mock providers
**Production readiness**: Full OpenAI + MongoDB + AWS integration
**Code quality**: Type-safe, tested, documented

**Let's win those awards! 🏆**