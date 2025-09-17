# CityPulse Simplified Hackathon Plan - Local Video Storage

## 🎯 **Core Changes: Remove AWS S3, Focus on MongoDB**

### **Key Simplifications**
1. **Local Video Storage** - Store videos in `/app/media/videos/` directory
2. **Simple File URLs** - Serve videos directly via FastAPI static files
3. **MongoDB Spotlight** - Emphasize Vector Search, TTL, and personalization
4. **Mock-First Approach** - All AI providers default to mock for reliable demo

---

## 🏗️ **Simplified Architecture**

### **Video Storage Flow**
```
Upload → Local Directory → MongoDB Record → Direct File Serving
```

**Instead of:** `Client → FastAPI → S3 → Presigned URLs`
**Now:** `Client → FastAPI → Local Storage → Direct URLs`

### **File Structure**
```
/app/media/
  videos/
    20240917/
      roger/
        uuid1.mp4
        uuid2.mp4
```

---

## 📁 **Demo Video Setup**

### **Local Video Storage Structure**
```
/app/media/
  videos/
    20240917/          # Today's date folder
      roger/           # Demo user
        video1.mp4     # Your pre-loaded demo videos
        video2.mp4
        video3.mp4
      demo_user/
        brooklyn1.mp4  # Borough-specific content
        manhattan1.mp4
```

### **How You'll Add Demo Videos**

1. **Drop videos into** `/app/media/videos/` directory structure
2. **Run seed script** that will:
   - Scan for your pre-placed video files
   - Generate mock transcripts/titles for each
   - Create MongoDB records with embeddings
   - Set up the demo user's taste profile

### **Seed Script Will Handle**
```python
# scripts/seed_demo_data.py will:
- Find your .mp4 files in /app/media/videos/
- Create VideoDocument records for each
- Generate realistic mock transcripts/titles
- Insert into MongoDB with proper borough tags
- Create diverse content for good demo flow
```

### **Demo Benefits**
- ✅ **No upload needed during demo** - videos already there
- ✅ **Reliable content** - you control what's shown
- ✅ **Instant playback** - local files, no network issues
- ✅ **Diverse boroughs** - organize by NYC areas for demo

---

## 🔧 **Required Changes**

### **1. Replace S3MediaManager with LocalMediaManager**
- Remove AWS dependencies completely
- Create simple file operations (save, serve, delete)
- Generate local file paths instead of S3 keys

### **2. Update Configuration**
- Remove all AWS/S3 config variables
- Add `MEDIA_BASE_PATH=/app/media`
- Set all providers to `mock` by default

### **3. Simplify Upload Endpoint**
- Remove S3 upload logic
- Save files to local directory structure
- Store file paths in MongoDB instead of S3 keys

### **4. Add Static File Serving**
- Mount `/media` as static files in FastAPI
- Videos accessible via `/media/videos/...`

---

## 🎪 **5-Minute Demo Script**

### **MongoDB Features to Highlight:**

1. **[1 min] Vector Search Demo**
   - Show taste learning: like videos → personalized ranking
   - "Watch how MongoDB learns your preferences in real-time!"

2. **[1 min] TTL Collections**
   - Mention 24-hour auto-expiration
   - "Videos automatically disappear after 24h using MongoDB TTL"

3. **[2 min] RAG with Ask NYC**
   - Query: "What's happening in Brooklyn right now?"
   - Show vector similarity search → LLM summarization

4. **[1 min] Borough-Based Filtering**
   - Browse different NYC boroughs
   - Show geospatial indexing and queries

### **Prize Category Alignment:**
- **Best Use of MongoDB**: Vector Search + TTL + Geo queries
- **Best Memory Hack**: User taste embeddings (running mean)
- **Best Multimodal**: Audio transcription → text embeddings

---

## 📦 **Implementation Steps**

### **Phase 1: Core Refactoring**
1. Create `LocalMediaManager` class
2. Update `config.py` to remove AWS settings
3. Modify upload endpoint for local storage
4. Add static file mounting to `main.py`

### **Phase 2: Demo Preparation**
1. Set all providers to `mock` by default
2. Create compelling seed data for demo
3. Test complete flow: upload → like → feed reordering
4. Practice "Ask NYC" queries with pre-seeded content

### **Phase 3: Demo Polish**
1. Add demo-specific logging for visual feedback
2. Create backup static responses for network issues
3. Prepare MongoDB Atlas dashboard for audience

---

## 🚀 **Benefits of This Approach**

1. **⚡ Faster Development** - No AWS setup/credentials needed
2. **🛡️ Demo Reliability** - No external dependencies to fail
3. **🎯 MongoDB Focus** - Showcases DB features, not storage complexity
4. **💻 Local Development** - Works entirely offline
5. **📱 Same API** - Frontend doesn't need changes

---

## 📂 **Files to Modify**

### **Remove/Replace:**
- `app/s3media.py` → `app/local_media.py`
- All AWS config in `config.py`
- S3 logic in upload routes

### **Update:**
- `app/main.py` - add static file serving
- `app/routes/upload.py` - local storage logic
- `.env.example` - remove AWS vars
- `app/models.py` - `s3_key` → `file_path`

### **Keep Same:**
- All MongoDB operations
- User taste learning
- Vector search logic
- Feed ranking algorithms

---

## 🎯 **Hackathon Context**

### **Event Details**
- **Event**: MongoDB Demopalooza at AI Tinkerers NYC (Javits Center)
- **Format**: 5 minutes demo + 90 seconds Q&A
- **Audience**: ~125 attendees from AI Tinkerers and MongoDB communities
- **Recording**: Professional cameras, shared afterward

### **Prize Categories**
- **Best Use of MongoDB** - Our primary target
- **Best Memory Hack** - User taste learning system
- **Best Multimodal Build** - Audio + text processing
- **Crowd Favorite** - Engaging NYC-focused demo

### **Demo Success Metrics**
1. **MongoDB Vector Search** prominently featured
2. **Real-time personalization** visible to audience
3. **Reliable demo flow** - no network dependencies
4. **Clear value proposition** - hyperlocal NYC content
5. **Technical depth** - showcase Atlas capabilities

---

## 🔄 **Your Workflow**

### **Preparation Steps**
1. Place 10-15 interesting NYC-related videos in `/app/media/videos/` structure
2. Organize by borough for demo flow
3. Run `uv run python scripts/seed_demo_data.py`
4. Test complete demo script with seeded data
5. Practice MongoDB Atlas dashboard navigation

### **Demo Day Setup**
1. Local MongoDB backup ready
2. All providers in mock mode
3. Pre-seeded content loaded
4. Demo script rehearsed
5. Backup responses for Q&A

This plan maintains all the impressive MongoDB features while eliminating AWS complexity, making your demo bulletproof and MongoDB-focused!