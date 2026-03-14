"""
Tools: create_checkout, check_payment_status, get_order_details
Wraps Pine Labs Hosted Checkout API (POST /api/checkout/v1/orders).

Flow: single API call → returns token + order_id + redirect_url.
      redirect_url is the Infinity Checkout page where customer pays.
      allowed_payment_methods includes CREDIT_EMI / DEBIT_EMI for EMI flow.

SAFETY: create_checkout enforces user_confirmed=True.
        Policy middleware (middleware/policy.py) provides a second check.
"""

import json
import os
from pathlib import Path
from typing import Optional

import httpx

from config.pinelabs import PineLabsConfig
from tools.auth import get_pine_labs_token

MOCK_DIR = Path(__file__).parent.parent / "mock"


def _is_mock() -> bool:
    return os.getenv("USE_MOCK", "true").lower() == "true"


# ── create_checkout ────────────────────────────────────────────────

async def create_checkout(
    amount_paisa: int,
    product_id: str,
    customer_id: str,
    user_confirmed: bool = False,
    emi_scheme: Optional[dict] = None,
) -> dict:
    """
    Create a Pine Labs order + Infinity Checkout URL.

    REQUIRES user_confirmed=True. Returns error dict if not confirmed.

    Args:
        amount_paisa:   Net order amount in paisa (post-discount).
        product_id:     Product identifier.
        customer_id:    Customer identifier.
        user_confirmed: MUST be True. Agent must get explicit confirmation.
        emi_scheme:     Optional selected EMI scheme dict.

    Returns dict with order_id, checkout_url.
    """
    if not user_confirmed:
        return {
            "error": "CONFIRMATION_REQUIRED",
            "message": "user_confirmed must be True before creating a checkout. Ask the customer to confirm their order.",
        }

    if _is_mock():
        data = json.loads((MOCK_DIR / "checkout.json").read_text())
        # Patch amount into mock response
        data["order"]["amount_paisa"] = amount_paisa
        if emi_scheme:
            data["order"]["emi_scheme"] = emi_scheme
        return data

    try:
        return await _live_create_checkout(amount_paisa, product_id, customer_id, emi_scheme)
    except Exception as e:
        print(f"[checkout] Live API failed ({e}), falling back to mock")
        data = json.loads((MOCK_DIR / "checkout.json").read_text())
        data["order"]["amount_paisa"] = amount_paisa
        return data


async def _live_create_checkout(
    amount_paisa: int,
    product_id: str,
    customer_id: str,
    emi_scheme: Optional[dict],
) -> dict:
    token = await get_pine_labs_token()

    # Hosted Checkout — single API call.
    # Pine Labs returns redirect_url which opens Infinity Checkout page.
    # allowed_payment_methods always includes EMI options; Pine Labs shows
    # the EMI UI inline on the checkout page.
    payment_methods = ["CREDIT_EMI", "DEBIT_EMI", "CARD", "UPI", "NETBANKING", "WALLET"]

    payload: dict = {
        "merchant_order_reference": f"NL-{product_id}-{customer_id}",
        "order_amount": {
            "value": amount_paisa,
            "currency": "INR",
        },
        "allowed_payment_methods": payment_methods,
        "integration_mode": "REDIRECT",
        "callback_url": os.getenv("PAYMENT_CALLBACK_URL", "http://localhost:3000/payment-complete"),
        "purchase_details": {
            "customer": {
                "country_code": "+91",
            }
        },
    }

    async with httpx.AsyncClient(timeout=PineLabsConfig.TIMEOUT_SECONDS) as client:
        resp = await client.post(
            f"{PineLabsConfig.PLURAL_BASE_URL}{PineLabsConfig.Endpoints.HOSTED_CHECKOUT}",
            json=payload,
            headers=PineLabsConfig.plural_headers(token),
        )
        resp.raise_for_status()
        data = resp.json()

    return {
        "response_code": 1 if data.get("response_code") == 200 else 0,
        "response_message": data.get("response_message", "SUCCESS"),
        "order": {
            "order_id": data.get("order_id"),
            "status": "CREATED",
            "amount_paisa": amount_paisa,
        },
        "checkout": {
            # redirect_url from Pine Labs = Infinity Checkout page URL
            "checkout_url": data.get("redirect_url"),
            "checkout_token": data.get("token"),
        },
    }


# ── check_payment_status ───────────────────────────────────────────

async def check_payment_status(order_id: str) -> dict:
    """
    Poll Pine Labs order payment status.

    Returns dict with status: PENDING | SUCCESS | FAILED.
    """
    if _is_mock():
        return json.loads((MOCK_DIR / "payment_status.json").read_text())

    try:
        return await _live_payment_status(order_id)
    except Exception as e:
        print(f"[checkout] Status check failed ({e}), falling back to mock")
        return json.loads((MOCK_DIR / "payment_status.json").read_text())


async def _live_payment_status(order_id: str) -> dict:
    token = await get_pine_labs_token()
    path = PineLabsConfig.Endpoints.ORDER_STATUS.format(order_id=order_id)

    async with httpx.AsyncClient(timeout=PineLabsConfig.STATUS_TIMEOUT_SECONDS) as client:
        response = await client.get(
            f"{PineLabsConfig.PLURAL_BASE_URL}{path}",
            headers=PineLabsConfig.plural_headers(token),
        )
        response.raise_for_status()
        return response.json()


# ── get_order_details ──────────────────────────────────────────────

async def get_order_details(order_id: str) -> dict:
    """
    Get full Pine Labs order details. Used by Support Agent.

    Returns full order object including product, customer, payment details.
    """
    if _is_mock():
        return json.loads((MOCK_DIR / "order_details.json").read_text())

    try:
        return await _live_order_details(order_id)
    except Exception as e:
        print(f"[checkout] Order details failed ({e}), falling back to mock")
        return json.loads((MOCK_DIR / "order_details.json").read_text())


async def _live_order_details(order_id: str) -> dict:
    token = await get_pine_labs_token()
    path = PineLabsConfig.Endpoints.ORDER_DETAILS.format(order_id=order_id)

    async with httpx.AsyncClient(timeout=PineLabsConfig.STATUS_TIMEOUT_SECONDS) as client:
        response = await client.get(
            f"{PineLabsConfig.PLURAL_BASE_URL}{path}",
            headers=PineLabsConfig.plural_headers(token),
        )
        response.raise_for_status()
        return response.json()
