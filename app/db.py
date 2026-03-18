from __future__ import annotations

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection

from app.config import settings


_client: AsyncIOMotorClient | None = None


def get_client() -> AsyncIOMotorClient:
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(settings.mongodb_uri)
    return _client


def get_collection() -> AsyncIOMotorCollection:
    client = get_client()
    db = client[settings.mongodb_db]
    return db[settings.mongodb_collection]


async def ensure_indexes() -> None:
    col = get_collection()
    await col.create_index("ProductID", unique=True)
    await col.create_index("Name")

