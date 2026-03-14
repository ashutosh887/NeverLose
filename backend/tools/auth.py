"""
Pine Labs Bearer Token helper for the new Plural API.

Used by: checkout.py, payment_links.py, qr_code.py, convenience_fee.py

The EMI Calculator v3 (legacy API) does NOT use this — it uses
merchant_id + merchant_access_code directly in the request body.
"""

import os
from datetime import datetime, timedelta

import httpx

# In-process cache — avoids re-fetching on every tool call.
# Token TTL from Pine Labs is ~60 min; we refresh at 55 min.
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

    base_url = os.getenv("PINE_LABS_PLURAL_URL", "https://pluraluat.v2.pinepg.in")
    client_id = os.getenv("PINE_LABS_CLIENT_ID", "")
    client_secret = os.getenv("PINE_LABS_CLIENT_SECRET", "")

    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.post(
            f"{base_url}/api/auth/v1/token",
            json={
                "client_id": client_id,
                "client_secret": client_secret,
                "grant_type": "client_credentials",
            },
        )
        response.raise_for_status()
        data = response.json()

    _token_cache["token"] = data["access_token"]
    # Refresh 5 min before actual expiry to avoid edge-case failures
    _token_cache["expires_at"] = now + timedelta(minutes=55)

    return _token_cache["token"]


def clear_token_cache() -> None:
    """Force token refresh on next call. Useful after 401 responses."""
    _token_cache["token"] = None
    _token_cache["expires_at"] = None
