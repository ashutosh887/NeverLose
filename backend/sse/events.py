import asyncio
import json
from pathlib import Path
from typing import AsyncGenerator

from fastapi import Request

MOCK_DIR = Path(__file__).parent.parent / "mock"

_event_queue: asyncio.Queue = asyncio.Queue()


async def publish_event(event: dict) -> None:
    await _event_queue.put(event)


async def _load_seed_from_mongo() -> dict:
    try:
        from db.client import get_db
        db = get_db()
        if db is None:
            return {}

        conversions_cursor = db["conversions"].find({}, {"_id": 0}).sort("timestamp", -1).limit(10)
        recent_conversions = await conversions_cursor.to_list(length=10)

        summaries_cursor = db["daily_summaries"].find({}, {"_id": 0}).sort("date", 1)
        daily_summary = await summaries_cursor.to_list(length=7)

        weekly_doc = await db["weekly_stats"].find_one({}, {"_id": 0})

        return {
            "daily_summary": daily_summary,
            "total_weekly": weekly_doc or {},
            "recent_conversions": recent_conversions,
        }
    except Exception as exc:
        print(f"[sse] MongoDB seed load failed: {exc}")
        return {}


async def _load_seed_from_file() -> dict:
    try:
        data = json.loads((MOCK_DIR / "dashboard_seed.json").read_text())
        return {
            "daily_summary": data["daily_summary"],
            "total_weekly": data["total_weekly"],
            "recent_conversions": data["recent_conversions"],
        }
    except Exception as exc:
        print(f"[sse] File seed load failed: {exc}")
        return {}


async def event_stream(request: Request) -> AsyncGenerator[str, None]:
    seed = await _load_seed_from_mongo()
    if not seed:
        seed = await _load_seed_from_file()

    if seed:
        yield f"data: {json.dumps({'type': 'seed', **seed})}\n\n"

    while True:
        if await request.is_disconnected():
            break

        try:
            event = await asyncio.wait_for(_event_queue.get(), timeout=5.0)
            yield f"data: {json.dumps(event)}\n\n"
        except asyncio.TimeoutError:
            yield f"data: {json.dumps({'type': 'ping'})}\n\n"
        except Exception as exc:
            print(f"[sse] Stream error: {exc}")
            break
