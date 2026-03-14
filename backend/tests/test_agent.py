"""
Agent integration tests — Phase 10

Full conversation flow tests using mock data.
Tests the supervisor stub; will test real agents once Phase 2 is implemented.
"""

import os
import pytest

os.environ["USE_MOCK"] = "true"

from agents.supervisor import supervisor_agent


@pytest.mark.asyncio
async def test_supervisor_exit_intent_response():
    """Exit intent signal triggers daily cost + social proof response."""
    response = await supervisor_agent(
        message="",
        signal_type="EXIT_INTENT_DETECTED",
    )
    assert "₹4,722" in response or "month" in response


@pytest.mark.asyncio
async def test_supervisor_cart_stall_response():
    """Cart stall signal triggers EMI breakdown response."""
    response = await supervisor_agent(
        message="",
        signal_type="CART_STALL_DETECTED",
    )
    assert "EMI" in response or "month" in response


@pytest.mark.asyncio
async def test_supervisor_return_visit_response():
    """Return visit signal triggers 'back again' personalised response."""
    response = await supervisor_agent(
        message="",
        signal_type="RETURN_VISIT_DETECTED",
    )
    assert len(response) > 0


@pytest.mark.asyncio
async def test_supervisor_plain_message():
    """Plain message returns some response."""
    response = await supervisor_agent(message="What are the EMI options?")
    assert isinstance(response, str)
    assert len(response) > 0


@pytest.mark.asyncio
async def test_emi_then_offer_then_stacked_deal():
    """Full mock flow: EMI options + offers → stacked deal calculation."""
    from tools.emi_calculator import check_emi_options
    from tools.offer_engine import discover_offers, calculate_stacked_deal

    amount = 8999900  # Dell XPS 15

    emi_result = await check_emi_options(amount_in_paisa=amount)
    offers_result = await discover_offers(amount_in_paisa=amount)

    # Pick best no-cost EMI scheme
    no_cost_schemes = [s for s in emi_result["emi_schemes"] if s["is_no_cost"]]
    best_scheme = min(no_cost_schemes, key=lambda s: s["tenure_months"])

    deal = calculate_stacked_deal(
        original_amount_paisa=amount,
        offers=offers_result["offers"],
        emi_scheme=best_scheme,
    )

    # Net price must be less than original (discount applied)
    assert deal["net_price_paisa"] < amount

    # EMI must be computed on net price
    emi = deal["emi_on_net_price"]
    assert emi["monthly_installment_paisa"] > 0
    assert "₹" in emi["monthly_installment_display"]
