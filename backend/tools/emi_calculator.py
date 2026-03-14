"""
Tool: check_emi_options
Wraps Pine Labs EMI Calculator v3 (legacy API).

Auth: merchant_id + merchant_access_code in request body.
URL:  POST {PINE_LABS_LEGACY_URL}/api/v3/emi/calculator

DESIGN NOTES:
- Mock mode: loads scheme templates from mock/emi_options.json,
  computes actual EMI amounts for the given input amount_in_paisa.
- Real mode: posts to legacy API, returns raw response.
- All amounts in paisa throughout.
- Daily cost = monthly_installment_paisa // 30 (good enough for display).
"""

import json
import math
import os
from pathlib import Path
from typing import Optional

import httpx

MOCK_DIR = Path(__file__).parent.parent / "mock"


def _is_mock() -> bool:
    return os.getenv("USE_MOCK", "true").lower() == "true"


def _compute_monthly_emi(principal: int, annual_rate_pct: float, tenure_months: int) -> int:
    """
    Standard reducing-balance EMI formula.
    Returns monthly EMI in paisa (rounded up to nearest paisa).

    For no-cost EMI (annual_rate_pct == 0): principal / tenure.
    """
    if annual_rate_pct == 0:
        return math.ceil(principal / tenure_months)

    r = annual_rate_pct / 1200  # monthly rate
    emi = principal * r * (1 + r) ** tenure_months / ((1 + r) ** tenure_months - 1)
    return math.ceil(emi)


def _format_inr(paisa: int) -> str:
    """Convert paisa to ₹X,XX,XXX display string."""
    rupees = paisa // 100
    # Indian numbering: last 3 digits, then groups of 2
    s = str(rupees)
    if len(s) <= 3:
        return f"₹{s}"
    last3 = s[-3:]
    rest = s[:-3]
    groups = []
    while len(rest) > 2:
        groups.append(rest[-2:])
        rest = rest[:-2]
    if rest:
        groups.append(rest)
    formatted = ",".join(reversed(groups)) + "," + last3
    return f"₹{formatted}"


def _mock_emi_options(amount_in_paisa: int) -> dict:
    templates = json.loads((MOCK_DIR / "emi_options.json").read_text())
    schemes = []

    for scheme in templates["emi_schemes"]:
        tenure = scheme["tenure_months"]
        rate = scheme["annual_rate_percent"]
        monthly_paisa = _compute_monthly_emi(amount_in_paisa, rate, tenure)
        # No-cost EMI: bank/merchant absorbs interest. The ceil rounding creates
        # a tiny paisa artifact that must not show as "interest charged to customer."
        total_interest_paisa = 0 if rate == 0 else max(0, monthly_paisa * tenure - amount_in_paisa)
        daily_paisa = monthly_paisa // 30

        schemes.append(
            {
                **scheme,
                "amount_in_paisa": amount_in_paisa,
                "monthly_installment_paisa": monthly_paisa,
                "monthly_installment_display": _format_inr(monthly_paisa),
                "daily_cost_paisa": daily_paisa,
                "daily_cost_display": _format_inr(daily_paisa),
                "total_interest_paisa": total_interest_paisa,
                "total_payable_paisa": amount_in_paisa + total_interest_paisa,
                "total_payable_display": _format_inr(amount_in_paisa + total_interest_paisa),
            }
        )

    return {
        "response_code": 1,
        "response_message": "SUCCESS",
        "amount_in_paisa": amount_in_paisa,
        "emi_schemes": schemes,
    }


async def _live_emi_options(
    amount_in_paisa: int,
    merchant_id: Optional[str],
    card_type: Optional[str],
) -> dict:
    base_url = os.getenv("PINE_LABS_LEGACY_URL", "https://uat.pinepg.in")
    mid = merchant_id or os.getenv("PINE_LABS_MERCHANT_ID", "")
    access_code = os.getenv("PINE_LABS_ACCESS_CODE", "")

    payload: dict = {
        "merchant_data": {
            "merchant_id": int(mid),
            "merchant_access_code": access_code,
            "amount": amount_in_paisa,
        }
    }
    if card_type:
        payload["card_type"] = card_type

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{base_url}/api/v3/emi/calculator",
            json=payload,
        )
        response.raise_for_status()
        return response.json()


async def check_emi_options(
    amount_in_paisa: int,
    merchant_id: Optional[str] = None,
    card_type: Optional[str] = None,
) -> dict:
    """
    Query Pine Labs EMI Calculator v3.

    Args:
        amount_in_paisa: Order amount in paisa (e.g. 8499900 for ₹84,999).
        merchant_id:     Override merchant ID (uses env var if None).
        card_type:       Optional filter: "credit", "debit", "cardless".

    Returns dict with:
        emi_schemes: list of schemes, each with:
            bank_name, tenure_months, monthly_installment_paisa,
            monthly_installment_display, daily_cost_paisa, daily_cost_display,
            is_no_cost, label, badge, total_interest_paisa
    """
    if _is_mock():
        return _mock_emi_options(amount_in_paisa)

    try:
        return await _live_emi_options(amount_in_paisa, merchant_id, card_type)
    except Exception as e:
        # Fallback to mock on any live API failure
        print(f"[emi_calculator] Live API failed ({e}), falling back to mock")
        return _mock_emi_options(amount_in_paisa)
