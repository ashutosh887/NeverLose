"""
Pine Labs Bearer Token helper for the new Plural API.

Used by: checkout.py, payment_links.py, qr_code.py, convenience_fee.py

The EMI Calculator v3 (legacy API) does NOT use this — it uses
merchant_id + merchant_access_code directly in the request body.
"""

from datetime import datetime, timedelta

import httpx

from config.pinelabs import PineLabsConfig

# In-process cache — avoids re-fetching on every tool call.
# Token TTL from Pine Labs is ~60 min; we refresh at 55 min (PineLabsConfig.TOKEN_TTL_MINUTES).
_token_cache: dict = {"token": None, "expires_at": None}


async def get_pine_labs_token() -> str:
    """
    Get (or return cached) Bearer token for Pine Labs Plural API.

    Raises httpx.HTTPStatusError on auth failure — caller should handle
    and fall back to mock if USE_MOCK is set.
    """
    now = datetime.utcnow()

    if (
        _token_cache["token"]
        and _token_cache["expires_at"]
        and now < _token_cache["expires_at"]
    ):
        return _token_cache["token"]

    async with httpx.AsyncClient(timeout=PineLabsConfig.AUTH_TIMEOUT_SECONDS) as client:
        response = await client.post(
            f"{PineLabsConfig.PLURAL_BASE_URL}{PineLabsConfig.Endpoints.AUTH_TOKEN}",
            json=PineLabsConfig.auth_payload(),
        )
        response.raise_for_status()
        data = response.json()

    _token_cache["token"] = data["access_token"]
    _token_cache["expires_at"] = now + timedelta(minutes=PineLabsConfig.TOKEN_TTL_MINUTES)

    return _token_cache["token"]


def clear_token_cache() -> None:
    """Force token refresh on next call. Useful after 401 responses."""
    _token_cache["token"] = None
    _token_cache["expires_at"] = None
