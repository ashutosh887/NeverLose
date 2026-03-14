import os
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

_client: Optional[AsyncIOMotorClient] = None


def _uri() -> str:
    return os.getenv("MONGODB_URI", "")


def _db_name() -> str:
    return os.getenv("MONGODB_DB", "neverlose")


def get_db() -> Optional[AsyncIOMotorDatabase]:
    if _client is None:
        return None
    return _client[_db_name()]


async def connect() -> bool:
    global _client
    uri = _uri()
    if not uri:
        print("[db] MONGODB_URI not set — running without MongoDB")
        return False
    try:
        _client = AsyncIOMotorClient(uri, serverSelectionTimeoutMS=5000)
        await _client.admin.command("ping")
        print(f"[db] Connected to MongoDB: {_db_name()}")
        return True
    except Exception as exc:
        print(f"[db] MongoDB connection failed: {exc}")
        _client = None
        return False


async def disconnect() -> None:
    global _client
    if _client:
        _client.close()
        _client = None
        print("[db] MongoDB disconnected")


async def ping() -> bool:
    if _client is None:
        return False
    try:
        await _client.admin.command("ping")
        return True
    except Exception:
        return False
