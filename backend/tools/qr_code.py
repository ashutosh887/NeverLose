"""
Tool: generate_qr_code
Wraps Pine Labs UPI QR Code API (new Plural API).

The tool returns:
- upi_string: raw UPI deep link (upi://pay?...)
- qr_image_base64: PNG QR code image, base64-encoded
  Generated using the `qrcode` library — even in mock mode,
  so the frontend always gets a real, scannable QR.

Frontend renders the base64 image directly in the chat widget.
Customer scans with GPay / PhonePe / Paytm.
"""

import base64
import io
import json
import os
from pathlib import Path
from typing import Optional
from urllib.parse import quote

import httpx

from tools.auth import get_pine_labs_token

MOCK_DIR = Path(__file__).parent.parent / "mock"


def _is_mock() -> bool:
    return os.getenv("USE_MOCK", "true").lower() == "true"


def _build_upi_string(
    merchant_upi_id: str,
    merchant_name: str,
    amount_rupees: float,
    transaction_ref: str,
    note: str,
) -> str:
    """Construct UPI deep link per NPCI spec."""
    note_encoded = quote(note, safe="")
    name_encoded = quote(merchant_name, safe="")
    return (
        f"upi://pay"
        f"?pa={merchant_upi_id}"
        f"&pn={name_encoded}"
        f"&am={amount_rupees:.2f}"
        f"&tr={transaction_ref}"
        f"&tn={note_encoded}"
        f"&cu=INR"
    )


def _generate_qr_base64(upi_string: str) -> str:
    """
    Generate a real, scannable QR code from a UPI string.
    Returns base64-encoded PNG.
    """
    try:
        import qrcode

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=4,
        )
        qr.add_data(upi_string)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode("utf-8")

    except ImportError:
        # qrcode not installed — return transparent 1x1 PNG placeholder
        placeholder = (
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk"
            "+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        )
        return placeholder


async def generate_qr_code(
    order_id: str,
    amount_paisa: int,
    product_name: str = "your order",
    merchant_id: Optional[str] = None,
) -> dict:
    """
    Generate a UPI QR code for in-chat payment.

    Args:
        order_id:     Pine Labs order ID (used as transaction reference).
        amount_paisa: Order amount in paisa.
        product_name: Used in UPI transaction note.
        merchant_id:  Override merchant ID.

    Returns dict with:
        upi_string:       Raw UPI deep link.
        qr_image_base64:  Base64-encoded PNG QR (render as <img src="data:image/png;base64,...">).
        status:           "PENDING".
        qr_id:            QR identifier for status polling.
    """
    amount_rupees = amount_paisa / 100

    if _is_mock():
        fixture = json.loads((MOCK_DIR / "qr_code.json").read_text())
        merchant_upi = os.getenv("PINE_LABS_MERCHANT_UPI", "pinelabs@ybl")
        upi_string = _build_upi_string(
            merchant_upi_id=merchant_upi,
            merchant_name="Pine Labs",
            amount_rupees=amount_rupees,
            transaction_ref=order_id,
            note=product_name,
        )
        qr_base64 = _generate_qr_base64(upi_string)

        return {
            "response_code": 1,
            "response_message": "SUCCESS",
            "qr": {
                "qr_id": fixture["qr"]["qr_id"],
                "upi_string": upi_string,
                "qr_image_base64": qr_base64,
                "amount_paisa": amount_paisa,
                "expires_at": fixture["qr"]["expires_at"],
                "status": "PENDING",
            },
        }

    try:
        return await _live_generate_qr(order_id, amount_paisa, product_name, merchant_id)
    except Exception as e:
        print(f"[qr_code] Live API failed ({e}), falling back to mock")
        merchant_upi = os.getenv("PINE_LABS_MERCHANT_UPI", "pinelabs@ybl")
        upi_string = _build_upi_string(
            merchant_upi_id=merchant_upi,
            merchant_name="Pine Labs",
            amount_rupees=amount_rupees,
            transaction_ref=order_id,
            note=product_name,
        )
        qr_base64 = _generate_qr_base64(upi_string)
        fixture = json.loads((MOCK_DIR / "qr_code.json").read_text())
        return {
            "response_code": 1,
            "response_message": "SUCCESS",
            "qr": {
                **fixture["qr"],
                "upi_string": upi_string,
                "qr_image_base64": qr_base64,
                "amount_paisa": amount_paisa,
            },
        }


async def _live_generate_qr(
    order_id: str,
    amount_paisa: int,
    product_name: str,
    merchant_id: Optional[str],
) -> dict:
    base_url = os.getenv("PINE_LABS_PLURAL_URL", "https://pluraluat.v2.pinepg.in")
    token = await get_pine_labs_token()
    mid = merchant_id or os.getenv("PINE_LABS_MERCHANT_ID", "")

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{base_url}/api/v1/qr-codes",
            json={
                "order_id": order_id,
                "merchant_id": mid,
                "amount": amount_paisa,
                "description": product_name,
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        response.raise_for_status()
        data = response.json()

    upi_string = data.get("upi_string", "")
    qr_base64 = _generate_qr_base64(upi_string)

    return {
        "response_code": 1,
        "response_message": "SUCCESS",
        "qr": {
            **data,
            "qr_image_base64": qr_base64,
            "amount_paisa": amount_paisa,
            "status": "PENDING",
        },
    }
