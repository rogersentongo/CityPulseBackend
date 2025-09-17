"""Application dependencies - database, local media, OpenAI clients."""
import logging
from functools import lru_cache
from typing import AsyncGenerator

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from openai import AsyncOpenAI
from pymongo.errors import ServerSelectionTimeoutError

from app.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseManager:
    """MongoDB connection manager."""

    def __init__(self):
        self.client: AsyncIOMotorClient | None = None
        self.database: AsyncIOMotorDatabase | None = None

    async def connect(self) -> None:
        """Connect to MongoDB Atlas."""
        try:
            self.client = AsyncIOMotorClient(
                settings.mongo_uri,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=10000,
                socketTimeoutMS=10000,
            )
            # Test connection
            await self.client.admin.command('ping')
            self.database = self.client[settings.mongo_db]
            logger.info(f"✅ Connected to MongoDB: {settings.mongo_db}")
        except ServerSelectionTimeoutError as e:
            logger.error(f"❌ MongoDB connection failed: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ Unexpected MongoDB error: {e}")
            raise

    async def disconnect(self) -> None:
        """Disconnect from MongoDB."""
        if self.client:
            self.client.close()
            logger.info("✅ Disconnected from MongoDB")

    def get_database(self) -> AsyncIOMotorDatabase:
        """Get database instance."""
        if not self.database:
            raise RuntimeError("Database not connected. Call connect() first.")
        return self.database


# Global database manager
db_manager = DatabaseManager()


class MockCursor:
    """Mock cursor for database operations."""

    def __init__(self, data=None):
        self.data = data or []
        self.index = 0

    def sort(self, *args, **kwargs):
        return self

    def skip(self, *args, **kwargs):
        return self

    def limit(self, *args, **kwargs):
        return self

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self.index >= len(self.data):
            raise StopAsyncIteration
        item = self.data[self.index]
        self.index += 1
        return item


class MockCollection:
    """Mock collection for database operations."""

    def __init__(self):
        self.data = []

    def find(self, *args, **kwargs):
        return MockCursor(self.data)

    async def find_one(self, *args, **kwargs):
        return None

    async def insert_one(self, *args, **kwargs):
        return type('MockResult', (), {'inserted_id': 'mock_id'})()

    async def update_one(self, *args, **kwargs):
        return type('MockResult', (), {'modified_count': 1})()

    async def delete_one(self, *args, **kwargs):
        return type('MockResult', (), {'deleted_count': 1})()

    def aggregate(self, *args, **kwargs):
        return MockCursor([])


class MockDatabase:
    """Mock database for development mode."""

    def __init__(self):
        self._videos = MockCollection()
        self._users = MockCollection()
        self._likes = MockCollection()

    @property
    def videos(self):
        return self._videos

    @property
    def users(self):
        return self._users

    @property
    def likes(self):
        return self._likes

    def __getattr__(self, name):
        """Return mock collection for any attribute access."""
        return MockCollection()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


async def get_database() -> AsyncIOMotorDatabase:
    """Dependency to get database instance."""
    try:
        return db_manager.get_database()
    except RuntimeError:
        # If database is not connected, try to connect (for mock mode)
        # In production, this would be handled by startup events
        logger.warning("Database not connected, attempting connection...")

        # For mock mode, return a mock database that won't cause connection errors
        if settings.is_mock_mode:
            logger.info("🎭 Using mock database for development")
            return MockDatabase()
        else:
            # In production mode, try to connect
            await db_manager.connect()
            return db_manager.get_database()




@lru_cache()
def get_openai_client() -> AsyncOpenAI:
    """Get OpenAI async client."""
    try:
        client = AsyncOpenAI(api_key=settings.openai_api_key)
        logger.info("✅ OpenAI client initialized")
        return client
    except Exception as e:
        logger.error(f"❌ OpenAI client initialization failed: {e}")
        raise


async def validate_connections() -> dict[str, bool]:
    """Validate all external service connections."""
    results = {
        "mongodb": False,
        "openai": False,
    }

    # Test MongoDB
    try:
        await db_manager.connect()
        results["mongodb"] = True
    except Exception as e:
        logger.error(f"MongoDB validation failed: {e}")

    # Test OpenAI
    try:
        if settings.openai_api_key and not settings.is_mock_mode:
            client = get_openai_client()
            # Test with a simple request
            await client.models.list()
            results["openai"] = True
        else:
            logger.info("OpenAI validation skipped (mock mode or no API key)")
            results["openai"] = True  # Consider mock mode as valid
    except Exception as e:
        logger.error(f"OpenAI validation failed: {e}")

    return results


# Lifespan events for FastAPI
async def startup_event() -> None:
    """Application startup event."""
    logger.info("🚀 Starting CityPulse Backend...")
    logger.info(f"Environment: {'Mock Mode' if settings.is_mock_mode else 'Production'}")

    # Validate connections
    validation_results = await validate_connections()

    failed_services = [
        service for service, status in validation_results.items()
        if not status
    ]

    if failed_services:
        logger.warning(f"⚠️  Some services failed validation: {failed_services}")
        logger.info("💡 Consider using mock providers for demo reliability")
    else:
        logger.info("✅ All services validated successfully!")


async def shutdown_event() -> None:
    """Application shutdown event."""
    logger.info("🛑 Shutting down CityPulse Backend...")
    await db_manager.disconnect()