"""
SSE Events — Phase 5

Server-Sent Events stream for the merchant dashboard.
Emits conversion events when hesitation → payment succeeds.

Event format:
  data: { "type": "conversion", "product": "...", "amount_paisa": ...,
          "emi_scheme": {...}, "channel": "web|whatsapp|qr",
          "pine_labs_products": [...], "timestamp": "..." }

Also used to pre-seed the dashboard with historical data on connect.

TODO (Phase 5):
  - [ ] publish_event(event_dict) — called by Payment Agent on success
  - [ ] Initial seed: emit dashboard_seed.json conversions on connect
  - [ ] In-memory event queue (asyncio.Queue)
"""

import asyncio
import json
from pathlib import Path
from typing import AsyncGenerator

from fastapi import Request

MOCK_DIR = Path(__file__).parent.parent / "mock"

# Global in-memory event queue (single-process demo, no Redis needed)
_event_queue: asyncio.Queue = asyncio.Queue()


async def publish_event(event: dict) -> None:
    """Called by Payment Agent when a hesitation → conversion succeeds."""
    await _event_queue.put(event)


async def event_stream(request: Request) -> AsyncGenerator[str, None]:
    """
    SSE generator for GET /api/events.

    On connect: emits seeded historical conversions.
    Then: emits live conversion events as they arrive.
    """
    # Emit seed data on connect so dashboard isn't empty
    try:
        seed_data = json.loads((MOCK_DIR / "dashboard_seed.json").read_text())
        seed_event = {
            "type": "seed",
            "daily_summary": seed_data["daily_summary"],
            "total_weekly": seed_data["total_weekly"],
            "recent_conversions": seed_data["recent_conversions"],
        }
        yield f"data: {json.dumps(seed_event)}\n\n"
    except Exception as e:
        print(f"[sse] Failed to load seed data: {e}")

    # Stream live events
    while True:
        if await request.is_disconnected():
            break

        try:
            # Poll queue with timeout so we can check disconnection
            event = await asyncio.wait_for(_event_queue.get(), timeout=5.0)
            yield f"data: {json.dumps(event)}\n\n"
        except asyncio.TimeoutError:
            # Send keepalive ping every 5s to prevent connection timeout
            yield f"data: {json.dumps({'type': 'ping'})}\n\n"
        except Exception as e:
            print(f"[sse] Stream error: {e}")
            break
