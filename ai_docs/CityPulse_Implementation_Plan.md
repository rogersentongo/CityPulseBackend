# CityPulse Implementation Plan
## MongoDB Demopalooza Strategy & Post-Hackathon Roadmap

> **Target Event:** MongoDB Demopalooza at AI Tinkerers NYC
> **Demo Time:** 5 minutes + 90 seconds Q&A
> **Prize Categories:** Best Use of MongoDB, Best Memory Hack, Best Multimodal Build, Crowd Favorite

---

## Phase 1: Demo-Critical Features (Priority 1)

### 1. MongoDB Atlas Vector Search Setup
- **Collection:** `videos` with 1536-dim embeddings
- **Atlas Search Index:** `embedding_index` with cosine similarity
- **TTL Index:** Auto-expire videos after 24 hours
- **Compound Index:** `borough + createdAt` for feed queries

### 2. Basic Video Upload & Audio Transcription
- **Endpoint:** `POST /upload` (server-mediated S3 upload)
- **Processing:** Audio-only transcription via OpenAI Whisper
- **Storage:** S3 bucket with presigned GET URLs for playback
- **Borough Resolution:** GPS metadata → borough mapping (no lat/lon storage)

### 3. User Taste Memory System
- **Collection:** `users` with taste embedding (running mean)
- **Endpoint:** `POST /like` updates user taste vector
- **Algorithm:** Incremental mean: `new_mean = (old_mean * n + new_vector) / (n + 1)`

### 4. Personalized Feed Ranking
- **Endpoint:** `GET /feed?borough=Brooklyn&userId=roger`
- **Algorithm:** `0.65 * vector_similarity + 0.35 * time_decay`
- **Fallback:** Recent-first for new users without taste profile

### 5. Pre-Seeded NYC Content
- **Script:** `scripts/seed.py` with 10-15 compelling NYC videos
- **Content Strategy:** Mix of boroughs, interesting transcripts for RAG
- **Mock Providers:** Ensure offline demo capability

---

## Phase 2: Demo Enhancement (Priority 2)

### 1. RAG "Ask NYC" Feature
- **Endpoint:** `POST /ask` with natural language queries
- **Flow:** Query embedding → vector search → LLM summarization
- **Demo Query:** "What's happening in Williamsburg right now?"
- **Response:** 2-3 sentence summary with source videos

### 2. Borough-Based Filtering
- **Geographic Logic:** Shapely point-in-polygon for GPS coordinates
- **GeoJSON:** NYC borough boundaries (included in codebase)
- **Manual Override:** Frontend borough picker takes precedence

### 3. Multimodal Processing (Audio + Vision)
- **Vision:** Frame sampling + OpenAI GPT-4V for scene descriptions
- **OCR:** Tesseract for on-screen text extraction
- **Fusion:** Combine ASR + vision + OCR into unified transcript
- **Embedding:** Use fused multimodal text for vector search

### 4. Offline/Mock Mode
- **Environment Variables:** `*_PROVIDER=mock` for all external services
- **Mock Responses:** Realistic transcripts, embeddings, LLM outputs
- **Local MongoDB:** Docker container for network-independent demo

---

## Demopalooza Demo Strategy

### 5-Minute Demo Flow
1. **[30s] Setup:** "CityPulse - personalized NYC video feed with MongoDB Vector Search"
2. **[90s] Browse:** Show Brooklyn feed, explain borough concept
3. **[90s] Learn:** Like 2-3 videos, refresh feed, show reordering
4. **[60s] Ask:** "What's happening in Williamsburg?" → RAG response
5. **[30s] Tech:** Quick MongoDB Atlas Vector Search highlight

### Key Messaging Points
- **Memory:** "The app learns your taste through vector embeddings"
- **MongoDB:** "Atlas Vector Search enables real-time personalization"
- **Multimodal:** "We process audio, video, and text together"
- **Local:** "Borough-focused content for NYC communities"

### Backup Plans
- **Network Issues:** Local MongoDB + mock providers
- **API Failures:** Pre-computed responses for demo queries
- **Video Playback:** Backup local files if S3 presigning fails

---

## Post-Hackathon Scaling Path

### Production Readiness Checklist

#### Security & Authentication
- [ ] JWT-based user authentication
- [ ] Rate limiting (Redis-based)
- [ ] Input validation & sanitization
- [ ] Content moderation pipeline
- [ ] HTTPS/TLS certificates

#### Performance & Reliability
- [ ] Background job processing (Celery + Redis)
- [ ] Database connection pooling
- [ ] Error monitoring (Sentry)
- [ ] Structured logging
- [ ] Health checks & metrics

#### Scalability
- [ ] CDN for video delivery (CloudFront)
- [ ] Feed caching (Redis)
- [ ] Database read replicas
- [ ] Auto-scaling EC2 instances
- [ ] Load balancing (ALB)

### Architecture Evolution Roadmap

#### 100 Users (Week 1-2)
- Add proper authentication
- Implement background video processing
- Basic monitoring & logging
- Simple content moderation

#### 1,000 Users (Month 1-2)
- Redis caching layer
- CDN for global delivery
- Push notifications
- Analytics dashboard
- API rate limiting

#### 10,000+ Users (Month 3+)
- Microservices architecture
- Multiple database clusters
- Real-time recommendations
- Advanced content moderation
- Mobile app optimization

### Technology Stack Validation

#### Current (Hackathon)
- **API:** FastAPI + Uvicorn
- **Database:** MongoDB Atlas (Vector Search)
- **Storage:** AWS S3 + presigned URLs
- **AI:** OpenAI (Whisper, GPT-4, embeddings)
- **Deployment:** Single EC2 instance

#### Production (Scaled)
- **API:** FastAPI + Gunicorn (multi-worker)
- **Database:** MongoDB Atlas (sharded clusters)
- **Storage:** S3 + CloudFront CDN
- **AI:** OpenAI + potential local models
- **Deployment:** Auto-scaling groups + ALB
- **Caching:** Redis cluster
- **Jobs:** Celery + Redis
- **Monitoring:** DataDog/New Relic

---

## Technical Implementation Notes

### Priority Order
1. **MongoDB setup first** - This is your differentiator
2. **Basic upload/feed flow** - Core user experience
3. **Taste learning** - The "magic" personalization moment
4. **RAG feature** - Impressive AI capability showcase
5. **Multimodal enhancement** - If time permits

### Dependencies & Setup
```bash
# Core dependencies
fastapi
uvicorn
pymongo[srv]
boto3
python-multipart
python-dotenv
openai
shapely
tenacity

# System requirements
ffmpeg (for video processing)
MongoDB Atlas cluster
AWS S3 bucket + IAM role
OpenAI API key
```

### Testing Strategy
- **Unit tests:** Core algorithms (ranking, embedding updates)
- **Integration tests:** MongoDB operations, S3 uploads
- **E2E tests:** Full upload → process → feed flow
- **Demo rehearsal:** Practice exact demo flow multiple times

### Risk Mitigation
- **Multiple fallbacks:** Mock providers for all external dependencies
- **Offline capability:** Local MongoDB for demo emergencies
- **Simple demo flow:** Focus on one clear user story
- **Pre-seeded content:** Don't rely on live uploads during demo

---

## Success Metrics

### Hackathon Goals
- [ ] **Best Use of MongoDB** - Showcase Vector Search capabilities
- [ ] **Best Memory Hack** - Demonstrate taste learning system
- [ ] **Best Multimodal Build** - Audio + video + text processing
- [ ] **Crowd Favorite** - Engaging demo with clear value proposition

### Post-Hackathon Goals
- [ ] **Week 1:** Production deployment with authentication
- [ ] **Month 1:** 100+ active users across NYC boroughs
- [ ] **Month 3:** 1,000+ users with engagement metrics
- [ ] **Month 6:** Revenue model validation (premium features/ads)

---

## Key Architectural Decisions

### Why These Technologies?
- **MongoDB Atlas Vector Search:** Native vector capabilities, no separate vector DB needed
- **FastAPI:** Fast async Python, excellent for AI/ML integration
- **S3 + Presigned URLs:** Infinite scalability, keeps servers lightweight
- **OpenAI APIs:** Fastest path to working multimodal AI
- **Borough-based:** Natural content filtering, NYC-specific appeal

### What We're NOT Building (MVP Scope)
- Comments/social features
- Direct messaging
- Follow/unfollow mechanics
- Advanced content moderation
- Multiple cities beyond NYC
- Real-time notifications (initially)

This implementation plan balances hackathon demo needs with long-term production scalability, ensuring your Monday-Wednesday sprint creates a foundation for a real application.