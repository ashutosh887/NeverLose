"""
Tests for middleware/policy.py — Phase 10

Verifies the Cedar-equivalent safety rules.
"""

import os
import pytest

os.environ["USE_MOCK"] = "true"

from middleware.policy import check_policy, MAX_CHECKOUT_AMOUNT_PAISA, MAX_SELF_SERVE_REFUND_PAISA


class TestCreateCheckoutPolicy:
    def test_blocks_without_confirmation(self):
        result = check_policy("create_checkout", {"amount_paisa": 500000, "user_confirmed": False})
        assert result is not None
        assert result["reason"] == "CONFIRMATION_REQUIRED"

    def test_blocks_over_limit(self):
        """Order above ₹2,00,000 must be blocked."""
        result = check_policy(
            "create_checkout",
            {"amount_paisa": MAX_CHECKOUT_AMOUNT_PAISA + 1, "user_confirmed": True},
        )
        assert result is not None
        assert result["reason"] == "AMOUNT_EXCEEDS_LIMIT"

    def test_allows_at_limit(self):
        """Order exactly at ₹2,00,000 is allowed."""
        result = check_policy(
            "create_checkout",
            {"amount_paisa": MAX_CHECKOUT_AMOUNT_PAISA, "user_confirmed": True},
        )
        assert result is None

    def test_allows_normal_confirmed_order(self):
        result = check_policy(
            "create_checkout",
            {"amount_paisa": 8499900, "user_confirmed": True},
        )
        assert result is None


class TestRefundPolicy:
    def test_blocks_large_refund_without_escalation(self):
        result = check_policy(
            "process_refund",
            {"refund_amount_paisa": MAX_SELF_SERVE_REFUND_PAISA + 1, "supervisor_escalated": False},
        )
        assert result is not None
        assert result["reason"] == "REFUND_ESCALATION_REQUIRED"
        assert result["action"] == "ESCALATE_TO_SUPERVISOR"

    def test_allows_large_refund_with_escalation(self):
        result = check_policy(
            "process_refund",
            {"refund_amount_paisa": MAX_SELF_SERVE_REFUND_PAISA + 1, "supervisor_escalated": True},
        )
        assert result is None

    def test_allows_small_refund(self):
        result = check_policy(
            "process_refund",
            {"refund_amount_paisa": 100000, "supervisor_escalated": False},
        )
        assert result is None


class TestUnknownTool:
    def test_unknown_tool_allowed(self):
        """Unknown tools pass through — policy is whitelist-based."""
        result = check_policy("some_other_tool", {"foo": "bar"})
        assert result is None
