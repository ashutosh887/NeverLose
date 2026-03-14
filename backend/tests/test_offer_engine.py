"""
Tests for tools/offer_engine.py — Phase 10

All tests use USE_MOCK=true.
"""

import os
import pytest

os.environ["USE_MOCK"] = "true"

from tools.offer_engine import discover_offers, calculate_stacked_deal
from tools.emi_calculator import check_emi_options


@pytest.mark.asyncio
async def test_discover_offers_returns_three_offers():
    result = await discover_offers(amount_in_paisa=8999900)
    assert result["response_code"] == 1
    assert len(result["offers"]) == 3


@pytest.mark.asyncio
async def test_discover_offers_has_instant_discount():
    result = await discover_offers(amount_in_paisa=8999900)
    types = [o["offer_type"] for o in result["offers"]]
    assert "instant_discount" in types


class TestCalculateStackedDeal:
    @pytest.fixture
    def hdfc_18m_scheme(self):
        return {
            "bank_name": "HDFC Bank",
            "bank_code": "HDFC",
            "tenure_months": 18,
            "annual_rate_percent": 0,
            "is_no_cost": True,
            "scheme_id": "HDFC_NOCOST_18M",
        }

    @pytest.fixture
    def offers(self):
        return [
            {
                "offer_id": "INST_DISC_5000",
                "offer_type": "instant_discount",
                "offer_name": "Instant ₹5,000 Off",
                "discount_amount_paisa": 500000,
                "min_order_paisa": 3000000,
                "max_discount_paisa": 500000,
                "is_stackable": True,
            }
        ]

    def test_stacked_deal_net_price(self, hdfc_18m_scheme, offers):
        """Net price = original − instant discount."""
        deal = calculate_stacked_deal(8999900, offers, hdfc_18m_scheme)
        assert deal["net_price_paisa"] == 8999900 - 500000  # 8499900

    def test_stacked_deal_monthly_emi_on_net_price(self, hdfc_18m_scheme, offers):
        """EMI computed on net price, not original price."""
        deal = calculate_stacked_deal(8999900, offers, hdfc_18m_scheme)
        # 8499900 / 18 = 472217
        assert deal["emi_on_net_price"]["monthly_installment_paisa"] == pytest.approx(472217, abs=1)

    def test_stacked_deal_daily_cost_matches_docs(self, hdfc_18m_scheme, offers):
        """Daily cost matches CLAUDE.md '₹157/day' example."""
        deal = calculate_stacked_deal(8999900, offers, hdfc_18m_scheme)
        daily = deal["emi_on_net_price"]["daily_cost_paisa"]
        assert daily // 100 == 157

    def test_headline_contains_monthly_and_daily(self, hdfc_18m_scheme, offers):
        """Headline message contains both monthly and daily amounts."""
        deal = calculate_stacked_deal(8999900, offers, hdfc_18m_scheme)
        assert "/month" in deal["headline"]
        assert "/day" in deal["headline"]

    def test_no_cost_zero_interest(self, hdfc_18m_scheme, offers):
        """No-cost EMI scheme produces zero interest."""
        deal = calculate_stacked_deal(8999900, offers, hdfc_18m_scheme)
        assert deal["emi_on_net_price"]["total_interest_paisa"] == 0
