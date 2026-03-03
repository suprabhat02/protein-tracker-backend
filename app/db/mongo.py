import asyncio
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.core.config import get_settings


class MongoClientManager:
    def __init__(self) -> None:
        self._client: AsyncIOMotorClient | None = None
        self._db: AsyncIOMotorDatabase | None = None

    async def connect(self) -> None:
        settings = get_settings()
        self._client = AsyncIOMotorClient(
            settings.mongodb_uri,
            maxPoolSize=200,
            minPoolSize=20,
            serverSelectionTimeoutMS=30000,  # 30 seconds
            connectTimeoutMS=30000,  # 30 seconds
            socketTimeoutMS=30000,  # 30 seconds
            retryWrites=True,
        )
        # Test the connection immediately
        try:
            await asyncio.wait_for(self._client.admin.command("ping"), timeout=30.0)
            print("✅ MongoDB connection successful!")
        except asyncio.TimeoutError:
            print("⚠️ Warning: MongoDB connection timed out after 30 seconds.")
            print(
                "App will continue, but check your network connectivity to MongoDB Atlas."
            )
        except Exception as e:
            print(f"⚠️ Warning: MongoDB connection failed: {e}")
            print("App will continue running but database operations may fail.")
        self._db = self._client[settings.mongodb_db]

    async def disconnect(self) -> None:
        if self._client is not None:
            self._client.close()

    @property
    def db(self) -> AsyncIOMotorDatabase:
        if self._db is None:
            raise RuntimeError("Database connection has not been initialized.")
        return self._db


mongo_manager = MongoClientManager()


def get_database() -> AsyncIOMotorDatabase:
    return mongo_manager.db
