"""
Tools: discover_offers + calculate_stacked_deal
Wraps Pine Labs Offer Engine / Offer Discovery API (new Plural API).

DESIGN NOTES:
- discover_offers: Returns list of applicable offers for a product+amount.
- calculate_stacked_deal: Pure Python — no API call. Takes offers + best EMI
  scheme and combines into a single "stacked deal" object for the agent to present.

STACKING RULES:
1. Apply stackable instant discounts first (additive).
2. Apply one cashback offer (HDFC cashback on top of discounted price).
3. Brand subvention replaces instant discount if it's larger (non-stackable).
4. Compute EMI on net price after all discounts.
"""

import json
import math
import os
from pathlib import Path
from typing import Dict, List, Optional

import httpx

from config.pinelabs import PineLabsConfig
from tools.auth import get_pine_labs_token

MOCK_DIR = Path(__file__).parent.parent / "mock"


def _is_mock() -> bool:
    return os.getenv("USE_MOCK", "true").lower() == "true"


def _format_inr(paisa: int) -> str:
    rupees = paisa // 100
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
    return f"₹{','.join(reversed(groups))},{last3}"


# ── discover_offers ────────────────────────────────────────────────

async def _live_discover_offers(
    amount_in_paisa: int,
    merchant_id: Optional[str],
    product_id: Optional[str],
) -> dict:
    token = await get_pine_labs_token()
    mid = merchant_id or PineLabsConfig.MERCHANT_ID

    payload: dict = {
        "merchant_id": mid,
        "amount": amount_in_paisa,
    }
    if product_id:
        payload["product_id"] = product_id

    async with httpx.AsyncClient(timeout=PineLabsConfig.TIMEOUT_SECONDS) as client:
        response = await client.post(
            f"{PineLabsConfig.PLURAL_BASE_URL}{PineLabsConfig.Endpoints.OFFERS_DISCOVER}",
            json=payload,
            headers=PineLabsConfig.plural_headers(token),
        )
        response.raise_for_status()
        return response.json()


async def discover_offers(
    amount_in_paisa: int,
    merchant_id: Optional[str] = None,
    product_id: Optional[str] = None,
) -> dict:
    """
    Query Pine Labs Offer Engine for applicable offers.

    Args:
        amount_in_paisa: Order amount in paisa.
        merchant_id:     Override merchant ID.
        product_id:      Filter offers to a specific product.

    Returns dict with:
        offers: list of offer objects with offer_id, offer_type,
                discount_amount_paisa (or discount_percentage),
                max_discount_paisa, is_stackable, description.
    """
    if _is_mock():
        return json.loads((MOCK_DIR / "offers.json").read_text())

    try:
        return await _live_discover_offers(amount_in_paisa, merchant_id, product_id)
    except Exception as e:
        print(f"[offer_engine] Live API failed ({e}), falling back to mock")
        return json.loads((MOCK_DIR / "offers.json").read_text())


# ── calculate_stacked_deal ─────────────────────────────────────────

def calculate_stacked_deal(
    original_amount_paisa: int,
    offers: List[Dict],
    emi_scheme: dict,
) -> dict:
    """
    Pure Python — no API call.

    Takes the original price, a list of applicable offers (from discover_offers),
    and a chosen EMI scheme (from check_emi_options). Applies discounts to get the
    net price, recomputes EMI on net price, and returns a complete deal breakdown.

    ALWAYS call discover_offers FIRST, then pick best EMI on net price.

    Args:
        original_amount_paisa: Pre-discount order amount in paisa.
        offers:                List of offer dicts from discover_offers.
        emi_scheme:            A single scheme dict from check_emi_options.

    Returns stacked_deal dict with full breakdown.
    """
    net_price = original_amount_paisa
    applied_offers = []
    total_discount_paisa = 0
    cashback_paisa = 0

    # Sort: instant discounts first, then cashback, skip non-stackable unless best
    stackable = [o for o in offers if o.get("is_stackable")]
    non_stackable = [o for o in offers if not o.get("is_stackable")]

    # Apply stackable instant discounts
    for offer in stackable:
        if offer["offer_type"] == "instant_discount":
            disc = offer.get("discount_amount_paisa", 0)
            cap = offer.get("max_discount_paisa", disc)
            actual = min(disc, cap)
            if net_price >= offer.get("min_order_paisa", 0):
                net_price -= actual
                total_discount_paisa += actual
                applied_offers.append(
                    {
                        "offer_id": offer["offer_id"],
                        "offer_name": offer["offer_name"],
                        "type": "instant_discount",
                        "saving_paisa": actual,
                        "saving_display": _format_inr(actual),
                    }
                )

    # Apply cashback (on net price after instant discounts)
    for offer in stackable:
        if offer["offer_type"] == "cashback" and offer.get("discount_percentage"):
            pct = offer["discount_percentage"] / 100
            cashback = math.floor(net_price * pct)
            cap = offer.get("max_discount_paisa", cashback)
            actual = min(cashback, cap)
            cashback_paisa = actual
            applied_offers.append(
                {
                    "offer_id": offer["offer_id"],
                    "offer_name": offer["offer_name"],
                    "type": "cashback",
                    "saving_paisa": actual,
                    "saving_display": _format_inr(actual),
                }
            )
            # Note: cashback is credited post-payment; net_price for EMI stays the same
            break

    # Check if any non-stackable (brand subvention) beats combined stackable
    for offer in non_stackable:
        if offer.get("discount_percentage"):
            pct = offer["discount_percentage"] / 100
            brand_disc = math.floor(original_amount_paisa * pct)
            cap = offer.get("max_discount_paisa", brand_disc)
            brand_disc = min(brand_disc, cap)
            if brand_disc > total_discount_paisa:
                # Brand subvention is better — use it instead
                net_price = original_amount_paisa - brand_disc
                total_discount_paisa = brand_disc
                applied_offers = [
                    {
                        "offer_id": offer["offer_id"],
                        "offer_name": offer["offer_name"],
                        "type": "brand_subvention",
                        "saving_paisa": brand_disc,
                        "saving_display": _format_inr(brand_disc),
                    }
                ]
                if cashback_paisa:
                    applied_offers.append(
                        {
                            "offer_id": "CASHBACK",
                            "offer_name": "Cashback",
                            "type": "cashback",
                            "saving_paisa": cashback_paisa,
                            "saving_display": _format_inr(cashback_paisa),
                        }
                    )
                break

    # Recompute EMI on net price
    tenure = emi_scheme["tenure_months"]
    rate = emi_scheme.get("annual_rate_percent", 0)

    if rate == 0:
        monthly_paisa = math.ceil(net_price / tenure)
        total_interest_paisa = 0
    else:
        r = rate / 1200
        monthly_paisa = math.ceil(
            net_price * r * (1 + r) ** tenure / ((1 + r) ** tenure - 1)
        )
        total_interest_paisa = max(0, monthly_paisa * tenure - net_price)

    daily_paisa = monthly_paisa // 30
    total_savings_paisa = total_discount_paisa + cashback_paisa

    return {
        "original_amount_paisa": original_amount_paisa,
        "original_amount_display": _format_inr(original_amount_paisa),
        "net_price_paisa": net_price,
        "net_price_display": _format_inr(net_price),
        "total_discount_paisa": total_discount_paisa,
        "total_discount_display": _format_inr(total_discount_paisa),
        "cashback_paisa": cashback_paisa,
        "cashback_display": _format_inr(cashback_paisa),
        "total_savings_paisa": total_savings_paisa,
        "total_savings_display": _format_inr(total_savings_paisa),
        "applied_offers": applied_offers,
        "emi_on_net_price": {
            "bank_name": emi_scheme.get("bank_name"),
            "tenure_months": tenure,
            "monthly_installment_paisa": monthly_paisa,
            "monthly_installment_display": _format_inr(monthly_paisa),
            "daily_cost_paisa": daily_paisa,
            "daily_cost_display": _format_inr(daily_paisa),
            "is_no_cost": emi_scheme.get("is_no_cost", False),
            "total_interest_paisa": total_interest_paisa,
            "scheme_id": emi_scheme.get("scheme_id"),
        },
        # Pre-formatted agent message lines
        "headline": f"{_format_inr(monthly_paisa)}/month ({_format_inr(daily_paisa)}/day — less than your Swiggy order)",
        "savings_line": f"Save {_format_inr(total_savings_paisa)} with stacked offers",
    }
