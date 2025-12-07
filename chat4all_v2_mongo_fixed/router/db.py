from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient

from config import settings

_client: Optional[AsyncIOMotorClient] = None


def get_client() -> AsyncIOMotorClient:
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(settings.mongo_url)
    return _client


def get_db():
    client = get_client()
    return client[settings.mongo_db]
