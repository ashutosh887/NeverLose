"""
Tests for tools/emi_calculator.py — Phase 10

All tests use USE_MOCK=true (no live API calls).
"""

import os
import pytest

os.environ["USE_MOCK"] = "true"

from tools.emi_calculator import check_emi_options, _compute_monthly_emi, _format_inr


class TestComputeMonthlyEmi:
    def test_no_cost_emi(self):
        """No-cost EMI = principal / tenure, rounded up."""
        result = _compute_monthly_emi(8499900, 0, 18)
        assert result == pytest.approx(472217, abs=1)

    def test_no_cost_emi_daily_cost(self):
        """Daily cost from the ₹84,999 / 18m case matches CLAUDE.md example."""
        monthly = _compute_monthly_emi(8499900, 0, 18)
        daily = monthly // 30
        # CLAUDE.md: "₹157/day"
        assert daily // 100 == 157  # 15740 paisa = ₹157.40

    def test_interest_bearing_emi_positive(self):
        """Interest-bearing EMI > no-cost EMI for same principal."""
        no_cost = _compute_monthly_emi(8499900, 0, 12)
        with_interest = _compute_monthly_emi(8499900, 14, 12)
        assert with_interest > no_cost


class TestFormatInr:
    def test_basic(self):
        assert _format_inr(8499900) == "₹84,999"

    def test_lakh(self):
        assert _format_inr(12999900) == "₹1,29,999"

    def test_small(self):
        assert _format_inr(29900) == "₹299"

    def test_paisa_truncation(self):
        """Paisa portion truncated — we show whole rupees only."""
        assert _format_inr(8999999) == "₹89,999"


@pytest.mark.asyncio
async def test_check_emi_options_mock_returns_schemes():
    """Mock mode returns all 7 schemes for any amount."""
    result = await check_emi_options(amount_in_paisa=8499900)
    assert result["response_code"] == 1
    assert len(result["emi_schemes"]) == 7


@pytest.mark.asyncio
async def test_check_emi_options_amounts_in_paisa():
    """All returned amounts are integers (paisa)."""
    result = await check_emi_options(amount_in_paisa=4599900)
    for scheme in result["emi_schemes"]:
        assert isinstance(scheme["monthly_installment_paisa"], int)
        assert isinstance(scheme["daily_cost_paisa"], int)


@pytest.mark.asyncio
async def test_no_cost_schemes_zero_interest():
    """No-cost schemes have total_interest_paisa == 0."""
    result = await check_emi_options(amount_in_paisa=8499900)
    for scheme in result["emi_schemes"]:
        if scheme["is_no_cost"]:
            assert scheme["total_interest_paisa"] == 0
