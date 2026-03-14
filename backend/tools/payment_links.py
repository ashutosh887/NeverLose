"""
Tool: generate_payment_link
Wraps Pine Labs Payment Links API (new Plural API).

Returns a shareable payment link for WhatsApp/SMS delivery.
Frontend constructs the WhatsApp URL:
  https://wa.me/91{phone}?text={encodeURIComponent(whatsapp_message)}
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


def _build_whatsapp_message(
    product_name: str,
    monthly_display: str,
    is_no_cost: bool,
    tenure_months: int,
    payment_link_url: str,
) -> str:
    emi_label = f"No-Cost EMI, {tenure_months} months" if is_no_cost else f"EMI, {tenure_months} months"
    return (
        f"Your {product_name} is ready!\n\n"
        f"EMI: {monthly_display}/month ({emi_label})\n\n"
        f"Pay securely: {payment_link_url}\n\n"
        f"Powered by Pine Labs"
    )


async def generate_payment_link(
    order_id: str,
    amount_paisa: int,
    customer_phone: str,
    product_name: str = "your order",
    emi_scheme: Optional[dict] = None,
    expiry_minutes: int = 1440,
) -> dict:
    """
    Generate a Pine Labs Payment Link for WhatsApp/SMS delivery.

    Args:
        order_id:        Pine Labs order ID.
        amount_paisa:    Order amount in paisa.
        customer_phone:  Customer phone number (10 digits, no country code).
        product_name:    Product name for the WhatsApp message.
        emi_scheme:      Optional selected EMI scheme for message context.
        expiry_minutes:  Link expiry in minutes (default: 24 hours).

    Returns dict with payment_link_url, short_url, whatsapp_message, whatsapp_url.
    """
    if _is_mock():
        data = json.loads((MOCK_DIR / "payment_link.json").read_text())
        link_url = data["payment_link"]["payment_link_url"]

        monthly_display = "₹4,722"
        is_no_cost = True
        tenure_months = 18
        if emi_scheme:
            monthly_display = emi_scheme.get("monthly_installment_display", monthly_display)
            is_no_cost = emi_scheme.get("is_no_cost", True)
            tenure_months = emi_scheme.get("tenure_months", 18)

        whatsapp_msg = _build_whatsapp_message(
            product_name, monthly_display, is_no_cost, tenure_months, link_url
        )
        data["payment_link"]["whatsapp_message"] = whatsapp_msg
        data["payment_link"]["whatsapp_url"] = (
            f"https://wa.me/91{customer_phone}?text={_urlencode(whatsapp_msg)}"
        )
        return data

    try:
        return await _live_generate_link(
            order_id, amount_paisa, customer_phone, product_name, emi_scheme, expiry_minutes
        )
    except Exception as e:
        print(f"[payment_links] Live API failed ({e}), falling back to mock")
        return json.loads((MOCK_DIR / "payment_link.json").read_text())


def _urlencode(text: str) -> str:
    """Simple URL encoding for WhatsApp message."""
    from urllib.parse import quote
    return quote(text, safe="")


async def _live_generate_link(
    order_id: str,
    amount_paisa: int,
    customer_phone: str,
    product_name: str,
    emi_scheme: Optional[dict],
    expiry_minutes: int,
) -> dict:
    token = await get_pine_labs_token()

    payload: dict = {
        "order_id": order_id,
        "amount": amount_paisa,
        "customer_phone": f"91{customer_phone}",
        "expiry_in_minutes": expiry_minutes,
        "send_sms": False,
    }

    async with httpx.AsyncClient(timeout=PineLabsConfig.TIMEOUT_SECONDS) as client:
        response = await client.post(
            f"{PineLabsConfig.PLURAL_BASE_URL}{PineLabsConfig.Endpoints.PAYMENT_LINKS}",
            json=payload,
            headers=PineLabsConfig.plural_headers(token),
        )
        response.raise_for_status()
        data = response.json()

    link_url = data.get("payment_link_url", "")
    monthly_display = emi_scheme.get("monthly_installment_display", "") if emi_scheme else ""
    is_no_cost = emi_scheme.get("is_no_cost", False) if emi_scheme else False
    tenure_months = emi_scheme.get("tenure_months", 12) if emi_scheme else 12

    whatsapp_msg = _build_whatsapp_message(
        product_name, monthly_display, is_no_cost, tenure_months, link_url
    )

    return {
        "response_code": 1,
        "response_message": "SUCCESS",
        "payment_link": {
            **data,
            "whatsapp_message": whatsapp_msg,
            "whatsapp_url": f"https://wa.me/91{customer_phone}?text={_urlencode(whatsapp_msg)}",
        },
    }
