"""
Policy Middleware — Phase 4

Cedar-equivalent safety rules enforced BEFORE every tool execution.
These run outside LLM reasoning — the agent cannot bypass them.

Rules:
  1. Block create_checkout if amount_paisa > 20_000_000 (₹2,00,000)
  2. Block create_checkout if user_confirmed is not True
  3. Block refunds > 5_000_000 paisa (₹50,000) without supervisor_escalated=True

Usage:
  Wrap tool calls with @enforce_policy or call check_policy() before execution.
  Returns structured error dict (not exception) so agent can handle gracefully.

TODO (Phase 4):
  - [ ] @enforce_policy decorator
  - [ ] check_policy(tool_name, kwargs) function
  - [ ] Unit tests in tests/test_policy.py
"""

from typing import Any, Dict, Optional


MAX_CHECKOUT_AMOUNT_PAISA = 20_000_000   # ₹2,00,000
MAX_SELF_SERVE_REFUND_PAISA = 5_000_000  # ₹50,000


def check_policy(tool_name: str, kwargs: Dict[str, Any]) -> Optional[Dict]:
    """
    Check policy rules for a tool call.

    Returns None if allowed.
    Returns error dict if blocked — agent should relay this to the customer.
    """
    if tool_name == "create_checkout":
        amount = kwargs.get("amount_paisa", 0)
        confirmed = kwargs.get("user_confirmed", False)

        if not confirmed:
            return {
                "blocked": True,
                "reason": "CONFIRMATION_REQUIRED",
                "message": "Customer must explicitly confirm before checkout is created.",
            }

        if amount > MAX_CHECKOUT_AMOUNT_PAISA:
            return {
                "blocked": True,
                "reason": "AMOUNT_EXCEEDS_LIMIT",
                "message": f"Order amount ₹{amount // 100:,} exceeds the ₹2,00,000 agent limit. Escalate to human agent.",
            }

    if tool_name == "process_refund":
        amount = kwargs.get("refund_amount_paisa", 0)
        escalated = kwargs.get("supervisor_escalated", False)

        if amount > MAX_SELF_SERVE_REFUND_PAISA and not escalated:
            return {
                "blocked": True,
                "reason": "REFUND_ESCALATION_REQUIRED",
                "message": f"Refund of ₹{amount // 100:,} exceeds ₹50,000 limit. Escalating to supervisor.",
                "action": "ESCALATE_TO_SUPERVISOR",
            }

    return None  # allowed


def enforce_policy(tool_fn):
    """
    Decorator to enforce policy on async tool functions.

    Usage:
        @enforce_policy
        async def create_checkout(amount_paisa, ..., user_confirmed=False):
            ...
    """
    import functools

    @functools.wraps(tool_fn)
    async def wrapper(*args, **kwargs):
        policy_result = check_policy(tool_fn.__name__, kwargs)
        if policy_result:
            return policy_result
        return await tool_fn(*args, **kwargs)

    return wrapper
