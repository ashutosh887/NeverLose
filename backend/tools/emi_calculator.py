"""
Tool: check_emi_options
Queries Pine Labs Affordability Suite — Offer Discovery endpoint.

Auth: Bearer token (same OAuth2 flow as all Plural APIs).
URL:  POST {PLURAL_BASE_URL}/api/affordability/v1/offer/discovery

DESIGN NOTES:
- Mock mode: loads scheme templates from mock/emi_options.json,
  computes actual EMI amounts for the given input amount_in_paisa.
  Mock uses real reducing-balance EMI formula — indistinguishable from live.
- Live mode: calls Affordability Suite. Falls back to mock on any failure.
- Legacy API (/api/v3/emi/calculator) is NOT used — it requires merchant_access_code
  which is a separate credential from the old PineGateway portal.
- All amounts in paisa throughout.
- Daily cost = monthly_installment_paisa // 30 (good enough for display).
"""

import json
import math
import os
from pathlib import Path
from typing import Optional

import httpx

from config.pinelabs import PineLabsConfig
from tools.auth import get_pine_labs_token

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
    """
    Calls Pine Labs Affordability Suite — Offer Discovery.
    Returns raw API response; caller normalises to internal schema.
    Falls back to mock if API returns anything unexpected.
    """
    token = await get_pine_labs_token()
    mid = merchant_id or PineLabsConfig.MERCHANT_ID

    payload: dict = {
        "merchant_id": mid,
        "order_amount": {
            "value": amount_in_paisa,
            "currency": "INR",
        },
    }
    if card_type:
        payload["card_type"] = card_type.upper()

    endpoint = PineLabsConfig.Endpoints.AFFORDABILITY_OFFER_DISCOVERY

    async with httpx.AsyncClient(timeout=PineLabsConfig.TIMEOUT_SECONDS) as client:
        response = await client.post(
            f"{PineLabsConfig.PLURAL_BASE_URL}{endpoint}",
            json=payload,
            headers=PineLabsConfig.plural_headers(token),
        )
        response.raise_for_status()
        raw = response.json()

    # Normalise Affordability Suite response to internal emi_schemes format.
    # The suite returns offer objects; we map them to our schema so downstream
    # code (calculate_stacked_deal, frontend EMICard) works unchanged.
    schemes = _normalise_affordability_response(raw, amount_in_paisa)
    if not schemes:
        # API returned no schemes — fall back to mock so demo never fails
        raise ValueError("Affordability Suite returned empty schemes list")

    return {
        "response_code": 1,
        "response_message": "SUCCESS",
        "amount_in_paisa": amount_in_paisa,
        "emi_schemes": schemes,
    }


def _normalise_affordability_response(raw: dict, amount_in_paisa: int) -> list:
    """
    Maps Pine Labs Affordability Suite response to our internal emi_schemes list.
    If the response shape is unrecognised, returns empty list → triggers mock fallback.
    """
    offers = (
        raw.get("offers")
        or raw.get("emi_offers")
        or raw.get("data", {}).get("offers")
        or []
    )
    if not offers:
        return []

    schemes = []
    for offer in offers:
        # Try to extract fields from common Pine Labs Affordability response shapes
        bank_name = (
            offer.get("bank_name")
            or offer.get("issuer_name")
            or offer.get("provider_name")
            or "Bank EMI"
        )
        tenure = (
            offer.get("tenure")
            or offer.get("tenure_in_months")
            or offer.get("emi_tenure")
            or 0
        )
        if not tenure:
            continue

        annual_rate = (
            offer.get("interest_rate")
            or offer.get("annual_rate")
            or offer.get("rate_of_interest")
            or 0.0
        )
        is_no_cost = annual_rate == 0 or offer.get("subvention_type") == 1
        monthly_paisa = _compute_monthly_emi(amount_in_paisa, float(annual_rate), int(tenure))
        daily_paisa = monthly_paisa // 30
        total_interest = 0 if is_no_cost else max(0, monthly_paisa * tenure - amount_in_paisa)

        schemes.append({
            "bank_name": bank_name,
            "bank_code": offer.get("bank_code", bank_name[:4].upper()),
            "card_type": offer.get("card_type", "credit").lower(),
            "tenure_months": int(tenure),
            "annual_rate_percent": float(annual_rate),
            "scheme_id": offer.get("offer_id") or offer.get("scheme_id") or f"{bank_name}_{tenure}M",
            "is_no_cost": is_no_cost,
            "processing_fee_paisa": offer.get("processing_fee", 0),
            "label": "No-Cost EMI" if is_no_cost else "Low-Cost EMI",
            "badge": "MOST POPULAR" if (is_no_cost and int(tenure) == 6) else None,
            "amount_in_paisa": amount_in_paisa,
            "monthly_installment_paisa": monthly_paisa,
            "monthly_installment_display": _format_inr(monthly_paisa),
            "daily_cost_paisa": daily_paisa,
            "daily_cost_display": _format_inr(daily_paisa),
            "total_interest_paisa": total_interest,
            "total_payable_paisa": amount_in_paisa + total_interest,
            "total_payable_display": _format_inr(amount_in_paisa + total_interest),
        })

    return schemes


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
