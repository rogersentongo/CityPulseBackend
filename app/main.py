"""FastAPI application entry point."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.deps import shutdown_event, startup_event
from app.routes import health


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    await startup_event()
    yield
    # Shutdown
    await shutdown_event()


app = FastAPI(
    title="CityPulse Backend",
    description="NYC 24-hour borough-based video feed with MongoDB Atlas Vector Search",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS middleware with configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api/v1", tags=["Health"])

# Import additional route modules
from app.routes import upload, feed, like, ask

app.include_router(upload.router, prefix="/api/v1", tags=["Upload"])
app.include_router(feed.router, prefix="/api/v1", tags=["Feed"])
app.include_router(like.router, prefix="/api/v1", tags=["Likes"])
app.include_router(ask.router, prefix="/api/v1", tags=["Ask NYC"])

# Mount static files for video serving
app.mount("/media", StaticFiles(directory=settings.media_base_path), name="media")

@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint."""
    return {"message": "CityPulse Backend - Ready for MongoDB Demopalooza! 🎬🏙️"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)