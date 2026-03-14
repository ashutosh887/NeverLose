"""
Tool: calculate_convenience_fee
Wraps Pine Labs Convenience Fee API (new Plural API).

Returns fee breakdown across payment methods so the agent can help
the customer compare actual cost of each payment option.
"""

import json
import os
from pathlib import Path
from typing import List, Optional

import httpx

from config.pinelabs import PineLabsConfig
from tools.auth import get_pine_labs_token

MOCK_DIR = Path(__file__).parent.parent / "mock"


def _is_mock() -> bool:
    return os.getenv("USE_MOCK", "true").lower() == "true"


async def calculate_convenience_fee(
    order_id: str,
    amount_paisa: int,
    payment_methods: Optional[List[str]] = None,
) -> dict:
    """
    Get convenience fee breakdown across payment methods.

    Args:
        order_id:        Pine Labs order ID.
        amount_paisa:    Order amount in paisa (used to compute fee amounts).
        payment_methods: List of methods to compare. Defaults to all.
                         Options: "upi", "credit_card", "debit_card",
                                  "net_banking", "emi_no_cost".

    Returns dict with fees list — each entry has:
        payment_method, fee_percentage, fee_amount_paisa, display, is_recommended.
    """
    if _is_mock():
        data = json.loads((MOCK_DIR / "convenience_fee.json").read_text())
        # Recompute fee amounts for the actual order amount
        for fee in data["fees"]:
            if fee["fee_percentage"] > 0:
                fee["fee_amount_paisa"] = int(amount_paisa * fee["fee_percentage"] / 100)
        if payment_methods:
            data["fees"] = [f for f in data["fees"] if f["payment_method"] in payment_methods]
        return data

    try:
        return await _live_convenience_fee(order_id, amount_paisa, payment_methods)
    except Exception as e:
        print(f"[convenience_fee] Live API failed ({e}), falling back to mock")
        return json.loads((MOCK_DIR / "convenience_fee.json").read_text())


async def _live_convenience_fee(
    order_id: str,
    amount_paisa: int,
    payment_methods: Optional[List[str]],
) -> dict:
    token = await get_pine_labs_token()

    payload: dict = {
        "order_id": order_id,
        "amount": amount_paisa,
    }
    if payment_methods:
        payload["payment_methods"] = payment_methods

    async with httpx.AsyncClient(timeout=PineLabsConfig.STATUS_TIMEOUT_SECONDS) as client:
        response = await client.post(
            f"{PineLabsConfig.PLURAL_BASE_URL}{PineLabsConfig.Endpoints.CONVENIENCE_FEE}",
            json=payload,
            headers=PineLabsConfig.plural_headers(token),
        )
        response.raise_for_status()
        return response.json()
