"""Health check endpoint."""
from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel

from app.config import settings
from app.deps import get_database, validate_connections

router = APIRouter()


class ServiceStatus(BaseModel):
    """Service status model."""
    mongodb: bool
    s3: bool
    openai: bool


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str
    message: str
    services: ServiceStatus
    environment: str
    database: str


@router.get("/healthz", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check endpoint for monitoring."""
    # Quick service validation
    services = await validate_connections()

    overall_status = "ok" if all(services.values()) else "degraded"
    environment = "mock" if settings.is_mock_mode else "production"

    return HealthResponse(
        status=overall_status,
        message="CityPulse Backend is running! Ready for demo! 🚀",
        services=ServiceStatus(**services),
        environment=environment,
        database=settings.mongo_db,
    )