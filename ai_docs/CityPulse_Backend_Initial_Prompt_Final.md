# CityPulse NYC — Backend Initial Prompt (AWS S3 + EC2)

> **Use this file as the initial instruction to Claude Code.**  
> Goal: generate a production-ready MVP backend for a 5-minute live demo on Wednesday, using **AWS S3 for media storage** and **AWS EC2 for the API**, with **MongoDB Atlas** for metadata + vectors.

---

## Mission (MVP)

> **Note — Multimodal change:** Transcription now combines **audio ASR** + **frame captioning** + **OCR** and fuses them into a single text stream. Silent videos are supported. Also use uv for package management instead of the pip+venv.


**CityPulse** is a **24-hour, borough-based short-video feed** for NYC. Each uploaded clip is:

1) received by the API (running on EC2),  
2) processed: transcribed **(multimodal: audio+video → text)**, enriched (title + tags via LLM), embedded (vector), and borough-resolved (manual or GPS prefill),  
3) uploaded to **AWS S3** (mp4), and  
4) persisted in **MongoDB Atlas** with **TTL (24h)** and **Atlas Vector Search**.

We use **Atlas Vector Search** for:
- **Personalized ranking** via a per-user **taste embedding** (“memory”),
- **RAG summaries** for “Ask NYC” (top recent relevant clips → LLM summary).

### Location requirement (important)

- The **frontend shows a *manual* borough picker** (`Manhattan`, `Brooklyn`, `Queens`, `Bronx`, `Staten Island`).
- The **server may prefill** the borough **from the video’s QuickTime GPS** metadata (if present).
- **Persist only the final borough string**, **never** raw latitude/longitude.
- You may store `boroughSource: "manual" | "gps"` for transparency (but no coords).

### What we’ll demo

1) Open **Brooklyn** feed and scroll.  
2) Tap **Like** on 2–3 related clips → refresh → visible **re-ranking** (memory).  
3) **Ask NYC** (“What’s happening in Williamsburg right now?”) → 2–3 sentence RAG summary from recent clips.  
4) **Upload** a clip from camera roll → API processes → file lands in **S3**, doc in **Atlas** with `expiresAt` + `embedding`, then appears in feed.
5) Auth needs to have login

**Out of scope (MVP):** comments, follows/reposts, DMs, auto-blurring, neighborhood feeds, push notifications.

---

## Architecture

- **FastAPI** backend runs on **AWS EC2** (Ubuntu), reachable over HTTPS (Nginx reverse proxy optional) or direct HTTP for demo.
- **Media storage:** **AWS S3** (private bucket).  
  - For playback, backend returns a **time-limited presigned GET URL** per video in the feed responses.  
- **Metadata & vectors:** **MongoDB Atlas** (Vector Search + TTL).
- **LLM stack (default for MVP):**
  - Embeddings: `text-embedding-3-small` (1536 dims)
  - LLM (titles/tags & Ask NYC summary): `gpt-4o-mini`
  - multimodal transcription: OpenAI **Whisper API**
- Provide a **mock mode** for all providers to make seeding reliable offline.
-Docker

> **Implementation choice for MVP uploads:**  
> Use a **simple server-mediated upload**: the mobile app POSTs the mp4 to FastAPI; backend streams it to S3, then deletes any temp file.  
> (Optional stretch: add a **presigned POST** flow to upload directly to S3, then `/confirm` to start processing.)

---

## Environment (.env)

Create `.env` and `.env.example`:

```
# Mongo
MONGO_URI=
MONGO_DB=citypulse

# OpenAI
OPENAI_API_KEY=
EMBEDDING_MODEL=text-embedding-3-small
LLM_MODEL=gpt-4o-mini
TRANSCRIBE_PROVIDER=openai   # openai|mock
EMBEDDINGS_PROVIDER=openai   # openai|mock
LLM_PROVIDER=openai          # openai|mock

# AWS
AWS_REGION=us-east-1
S3_BUCKET=citypulse-media-demo
S3_PREFIX=uploads/                # optional folder prefix for mp4s
S3_PRESIGN_EXPIRY_SECONDS=3600    # presigned GET validity for playback

# API
PORT=8000
ALLOW_ORIGINS=*                   # dev/demo only

# Location handling
LOCATION_AUTODETECT=true          # server tries GPS prefill if needed
BOROUGH_REJECT_IF_UNKNOWN=true    # if inference fails and none provided → 400

# Multimodal (vision & OCR)
VISION_PROVIDER=openai          # openai|mock
OCR_PROVIDER=tesseract          # tesseract|textract|mock
FRAME_SAMPLE_FPS=0.5            # frames/s (0.5 = 1 frame every 2s)
SCENE_DETECT=true               # use scene-cut detection
SCENE_THRESHOLD=0.4             # ffmpeg select=gt(scene,0.4)
OCR_ENABLE=true
OCR_LANGS=eng
ASR_TIMEOUT_S=180
VISION_TIMEOUT_S=180
OCR_TIMEOUT_S=120
```

> The app should **use IAM role on EC2** (best) or `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` env vars (fallback).  
> Bucket should be **private**; **no public objects**. Always use presigned GET for playback.

---

## Data Model (MongoDB)

**Collection: `videos`**
```json
{
  "_id": "ObjectId",
  "userId": "roger",
  "borough": "Brooklyn",                 // REQUIRED at persistence time
  "boroughSource": "manual",             // "manual" | "gps"
  "s3Key": "uploads/<uuid>.mp4",
  "mediaUrlTTL": "2025-09-15T05:00:00Z", // optional: when presigned GET expires (for debugging)
  "durationSec": 0,
  "transcript": "string",
  "multimodalTranscript": "string",         // fused ASR+vision+OCR text (works when no audio)
  "visualCaption": "string",                // short caption from frames
  "visualTags": ["string"],                 // optional scene/object tags
  "ocrText": "string",                      // concatenated OCR from frames
  "hasAudio": true,
  "embeddingSource": "audio|vision|hybrid",
  "title": "string",
  "tags": ["string"],
  "embedding": [0.0],                    // length 1536
  "createdAt": "ISODate",
  "expiresAt": "ISODate"                 // createdAt + 24h (TTL)
}
```

**Collection: `users`**
```json
{
  "_id": "roger",
  "taste": {
    "embedding": [0.0],  // running mean of liked video embeddings
    "n": 0,
    "updatedAt": "ISODate"
  }
}
```

**Collection: `likes`** (optional)
```json
{
  "_id": "ObjectId",
  "userId": "roger",
  "videoId": "ObjectId",
  "createdAt": "ISODate"
}
```

> **Privacy rule:** Never persist raw GPS coordinates. Use them transiently to map to a borough, then discard.

---

## Location Handling (Detailed)

### Frontend → `/upload` contract (server-mediated for MVP)

`multipart/form-data` fields:
- `file` (mp4)
- `userId` (string; “roger” for demo)
- `borough` (optional string; if present must be one of: `Manhattan | Brooklyn | Queens | Bronx | Staten Island`)
- `autoDetectBorough` (optional boolean; default `true`)

Decision tree:
- If `borough` is provided and valid → trust it (`boroughSource="manual"`).
- Else if `autoDetectBorough == true` and `LOCATION_AUTODETECT == true` → server extracts GPS via **ffprobe** → ISO6709 → `(lat,lon)` → **Shapely** borough polygon → `boroughSource="gps"`.
- Else → **400** `{ error: "borough_required", allowed: [...] }`.

> **We do not store `(lat,lon)`**—only the resulting borough and `boroughSource`.

### (Optional Stretch) Direct-to-S3 flow
- `POST /uploads/presign` → returns presigned POST (fields, key).
- Client uploads to S3 → `POST /uploads/confirm` with `{ key, userId, borough?, autoDetectBorough? }`.
- Server then streams from S3 to transcribe/process, then updates DB.

For Wednesday, **stick to server-mediated** to minimize moving parts.

---

## MongoDB Indexes (Atlas)

1) **TTL** auto-expire on `expiresAt`
```js
db.videos.createIndex({ expiresAt: 1 }, { expireAfterSeconds: 0 });
```

2) **Recency**
```js
db.videos.createIndex({ borough: 1, createdAt: -1 });
```

3) **Vector Search** (Atlas Search index `"embedding_index"`)
```json
{
  "mappings": {
    "dynamic": false,
    "fields": {
      "embedding": { "type": "knnVector", "dimensions": 1536, "similarity": "cosine" },
      "borough":   { "type": "string" },
      "createdAt": { "type": "date" }
    }
  }
}
```

---

## Endpoints & Contracts

### `POST /upload` (multipart)  — **server-mediated S3 upload**
**Inputs:** `file`, `userId`, optional `borough`, optional `autoDetectBorough` (default `true`).

**Flow:**
1. Receive file; save to a **secure temp file** on EC2 (e.g., `/tmp/<uuid>.mp4`).
2. **Resolve borough** (manual or GPS via ffprobe + polygon mapping).
3. **Multimodal transcription**:
   - If audio present → **ASR** with Whisper (or mock).
   - Sample/scene-detect frames → **Vision captioning** (VLM | mock).
   - (Optional) **OCR** on frames for on-screen text.
   - **Fuse** ASR+Vision+OCR into a single **multimodal transcript** (aligned by timestamps).
4. **LLM on multimodal text** → `title` (≤60 chars) + 3–5 `tags`.
   - Input priority: `multimodalTranscript.text` → `transcript` → `visualCaption` → `ocrText`.
5. **Embed** the best available combined text (same priority as above).
6. **Upload to S3** at `s3://$S3_BUCKET/$S3_PREFIX/<uuid>.mp4` with `Content-Type: video/mp4` and server-side encryption (SSE-S3).
7. Delete temp file.
8. Insert video doc with `{ s3Key, borough, boroughSource, transcript, title, tags, embedding, createdAt, expiresAt }`.
9. Return `{ videoId, mediaUrl (presigned GET), borough, boroughSource, title, tags }`.

> **mediaUrl** must be a **presigned GET** (valid for `S3_PRESIGN_EXPIRY_SECONDS`) generated per response so the mobile player can stream the video. Do not store a permanent public URL.

### `GET /feed?borough=Brooklyn&userId=roger&limit=20`
**Flow:**
- Candidate set: `videos` with `borough` and `createdAt >= now - 48h`.
- If user has `taste.embedding`:
  - `$vectorSearch` with `queryVector=taste.embedding` (limit ~50).
  - `time_decay = exp(-hours_since/24)`.
  - Blend: `final = 0.65 * normalizedVectorScore + 0.35 * time_decay`.
  - Sort by `final` (tiebreak: `createdAt` desc).
- Else: recent sort (+ optional MMR diversity).
- For each item, attach a **fresh S3 presigned GET** URL (`expires in S3_PRESIGN_EXPIRY_SECONDS`).
**Return:** array of `{ videoId, mediaUrl, title, tags, createdAt }`.

### `POST /like`
**Body:** `{ userId, videoId }`  
**Flow:** update running mean in `users.taste` using liked video’s `embedding` (`n` increments).  
**Return:** `{ ok: true }`.

### `POST /ask`
**Body:** `{ query, borough, windowHours?: number }` (default 6)  
**Flow:** embed query → vector search filtered by borough & time window → top-K transcripts/titles/tags → LLM **2–3 sentence** summary (plain text).  
**Return:** `{ answer: string, sources: [{ videoId, createdAt }] }`.

### `GET /healthz`
**Return:** `{ status: "ok" }`.

---

## File Layout (generate)

```
backend/
  app/
    __init__.py
    main.py                 # FastAPI app, CORS, routes
    deps.py                 # settings (dotenv), Mongo client, S3 client (boto3)
    models.py               # Pydantic schemas (requests/responses)
    dao.py                  # CRUD for videos/users/likes
    llm.py                  # providers: transcribe, embed, title/tags, summarize (openai + mock)
    rank.py                 # scoring & time-decay helpers
    s3media.py              # S3 put_object, generate_presigned_url, key helpers
    routes/
      upload.py             # POST /upload
      feed.py               # GET /feed
      like.py               # POST /like
      ask.py                # POST /ask
      health.py             # GET /healthz
    utils/
      geo.py                # ffprobe GPS extraction (ISO6709)
      boroughs.py           # shapely point-in-polygon mapping + bundled GeoJSON
      time.py               # utcnow, decay helpers
    utils/nyc_boroughs.geojson
  scripts/
    create_indexes.py       # TTL + recency; prints Atlas Search JSON
    seed.py                 # seed demo clips (mock providers supported), uploads to S3
  tests/
    test_health.py
    test_upload_borough_logic.py
    test_feed_basic.py
  .env.example
  requirements.txt (or pyproject.toml)
  README.md
```

---

## Dependencies

- `fastapi`, `uvicorn`
- `pydantic`
- `pymongo` (or `motor` for async)
- `boto3`
- `python-multipart`
- `python-dotenv`
- `ffmpeg` (system dependency) + `ffmpeg-python` **or** `subprocess` with `ffprobe`
- `shapely` (borough polygons; include GeoJSON)
- `tenacity` (optional retries)
- `pytest` (tests)

> **EC2 AMI setup**: install `ffmpeg` (`sudo apt update && sudo apt install -y ffmpeg`), Python 3.10+, and ensure instance role or AWS keys are configured.  
> **Security group**: open port 80/8000 for demo.  
> Optional: Nginx reverse proxy on port 80 → Uvicorn 8000; add domain + TLS later.

---

## LLM Prompts (implement in `llm.py`)

**Title+Tags — system**
```
Generate a short, catchy title (<= 60 chars) and 3–5 concise tags for a short NYC borough story based on the transcript. Return JSON: {"title":"...","tags":["...","..."]}. Avoid private info and profanity.
```

**Ask NYC Summary — system**
```
You are a concise live-events summarizer. Given multiple short clips (title, tags, multimodal transcript excerpt, timestamps) for a NYC borough from the last N hours, produce a neutral 2–3 sentence “what’s happening” summary with concrete details. Avoid speculation. Return plain text.
```

---

## Ranking Helpers

- Normalize Atlas vector score to `[0,1]` (if needed).  
- `time_decay = exp(-hours_since/24)`.  
- `final = 0.65 * sim + 0.35 * time_decay`.  
- Fallbacks:
  - If no taste vector → recent + (optional) MMR diversity.
  - If vector index unavailable → recent only.

---

## Acceptance Criteria
- Handles **silent videos** by generating captions/OCR and fusing into `multimodalTranscript`.
- Uses **multimodal text** for titles/tags/entities/embeddings and Ask NYC.

- `GET /healthz` returns OK.
- `POST /upload`:
  - Accepts manual `borough` or infers via GPS if `autoDetectBorough` true.
  - **Never** persists lat/lon; persists only `borough` + `boroughSource`.
  - Streams file to **S3** and saves `s3Key` in `videos`.
  - Inserts transcript, title, tags, embedding, `expiresAt = createdAt + 24h`.
- `POST /like` updates `users.taste.embedding` (running mean) and increments `n`.
- `GET /feed` re-ranks by taste + time decay; includes **presigned GET** URLs; order changes after a few likes.
- `POST /ask` returns a crisp 2–3 sentence summary with sources list.
- `scripts/create_indexes.py` creates TTL + recency; prints Atlas Search JSON.
- `scripts/seed.py` seeds 10–15 items (mock providers), uploads mp4s to S3, and inserts docs.
- Tests pass, especially `test_upload_borough_logic.py` (manual vs gps vs failure).

---

## README Commands (include)

```bash
# one-time install (choose one)
curl -LsSf https://astral.sh/uv/install.sh | sh   # adds ~/.local/bin/uv
# or: brew install uv

# setup (on EC2 or local)
sudo apt update && sudo apt install -y ffmpeg
uv venv                                    # creates .venv
uv sync                                     # installs from pyproject/uv.lock (fast)
cp .env.example .env                        # fill in vars

# run api  (adjust module path to your layout; ex: backend.app.main:app)
uv run uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --reload

# create indexes
uv run python scripts/create_indexes.py

# seed demo data
uv run python scripts/seed.py

# tests
uv run pytest -q

```

---

## AWS Setup Quickstart (document in README)

1) **S3 bucket** (private): `citypulse-media-demo` in `$AWS_REGION`.  
2) **IAM**: attach to EC2 instance role with minimal policy:
```json
{
  "Version":"2012-10-17",
  "Statement":[
    {"Effect":"Allow","Action":["s3:PutObject","s3:GetObject","s3:DeleteObject"],"Resource":"arn:aws:s3:::citypulse-media-demo/*"},
    {"Effect":"Allow","Action":["s3:ListBucket"],"Resource":"arn:aws:s3:::citypulse-media-demo"}
  ]
}
```
3) **EC2**: t3.small/t3.medium, open port 80/8000, install ffmpeg + Python, deploy code.  
4) **(Optional)** Nginx reverse proxy on port 80 → Uvicorn 8000; add domain + TLS later.

---

## Implementation Guidance

- **CORS**: allow Expo dev origins and your EC2 host.  
- **Media URLs**: never expose raw S3 URLs; always **presign GET** per response. Avoid storing presigned URLs in DB.  
- **Validation**: strict borough list; enforce MP4 and ≤ 60s duration if `ffprobe` available; otherwise skip gracefully.  
- **Errors**:  
  - **400** for invalid borough or inference failure (when required)  
  - **422** for malformed inputs  
  - **500** for provider/S3/ffprobe failures  
- **Logging**: method+path, ms latency, provider errors, and for uploads, `boroughSource` and `s3Key` (but no coords).  
- **Security**: use instance role credentials if possible; otherwise env keys; never log secrets.

---

## Final Instruction to Claude Code

**Generate the full backend project** according to this spec:

1) Create the folder/file layout.  
2) Implement endpoints, DAOs, location utils (`ffprobe` GPS + Shapely mapping), S3 integration (put + presign), LLM providers (OpenAI + mock), ranking, and scripts.  
3) Add `.env.example`, `requirements.txt` (or `pyproject.toml`), and a clear `README.md` with AWS setup steps.  
4) Include tests, especially for the borough resolution decision tree and S3 presign/upload paths.  
5) Print “next steps” to deploy on EC2 and run the demo.

If anything is ambiguous, choose the simplest path that preserves demo reliability and **strictly adheres to the privacy rule: store only the borough; never lat/lon**.
