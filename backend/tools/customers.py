"""
Tool: get_customer_profile
Wraps Pine Labs Customers API (new Plural API).

Used for personalisation: preferred language, cards on file,
prior purchase history, EMI preferences.
"""

import json
import os
from pathlib import Path
from typing import Optional

import httpx

from tools.auth import get_pine_labs_token

MOCK_DIR = Path(__file__).parent.parent / "mock"


def _is_mock() -> bool:
    return os.getenv("USE_MOCK", "true").lower() == "true"


async def get_customer_profile(
    customer_id: Optional[str] = None,
    phone: Optional[str] = None,
) -> dict:
    """
    Get customer profile for personalisation.

    Args:
        customer_id: Pine Labs customer ID.
        phone:       Customer phone number (fallback lookup).

    Returns dict with:
        name, phone, preferred_language, cards_on_file,
        purchase_history, emi_preference, hesitation_history.
    """
    if _is_mock():
        return json.loads((MOCK_DIR / "customer_profile.json").read_text())

    try:
        return await _live_get_customer(customer_id, phone)
    except Exception as e:
        print(f"[customers] Live API failed ({e}), falling back to mock")
        return json.loads((MOCK_DIR / "customer_profile.json").read_text())


async def _live_get_customer(
    customer_id: Optional[str],
    phone: Optional[str],
) -> dict:
    base_url = os.getenv("PINE_LABS_PLURAL_URL", "https://pluraluat.v2.pinepg.in")
    token = await get_pine_labs_token()

    lookup = customer_id or phone
    if not lookup:
        raise ValueError("customer_id or phone required")

    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.get(
            f"{base_url}/api/v1/customers/{lookup}",
            headers={"Authorization": f"Bearer {token}"},
        )
        response.raise_for_status()
        return response.json()
