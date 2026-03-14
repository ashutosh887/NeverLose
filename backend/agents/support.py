"""
Support Agent — Order tracking and refund handling.
Model: Claude Haiku 4.5

Tools:
  get_order_details    — full order info for tracking queries
  check_payment_status — pending payment queries

Refund rules:
  ≤ ₹50,000 → handle directly (initiate refund flow)
  > ₹50,000 → escalate to supervisor / human agent
"""

from typing import Any, Callable, Dict, List, Optional

from agents.supervisor import (
    BEDROCK_SUB_AGENT_MODEL,
    ANTHROPIC_SUB_AGENT_MODEL,
    ALL_TOOLS,
    _run_tool_loop,
)

SUPPORT_SYSTEM = """You are NeverLose Support — friendly, efficient, resolves issues fast.

## ORDER TRACKING
When customer asks "where is my order" / "order status" / "delivery":
1. Call get_order_details with their order_id
2. Report status clearly: "Your order #XXXXX is [status]. [Next step]."
3. If PENDING: "Payment is being processed. Usually takes 2-5 minutes."
4. If SUCCESS: "Order confirmed! Estimated delivery: 2-3 business days."
5. If FAILED: "It looks like the payment didn't go through. Would you like to try again?"

## REFUND HANDLING
Refunds ≤ ₹50,000:
→ "I'm initiating your refund for ₹X,XXX. It will reflect in 5-7 business days."

Refunds > ₹50,000:
→ "Refunds above ₹50,000 need our senior team to process. I'm escalating this now."
→ "You'll receive a call within 2 hours. Your reference: [order_id]"
→ Do NOT attempt to process the refund yourself.

## TONE
Empathetic, fast, clear. No corporate jargon. If something went wrong, acknowledge it first.
"I completely understand — let me fix this right now."

## LANGUAGE
Mirror customer's language. Always use ₹ symbol.
"""

SUPPORT_TOOLS = [t for t in ALL_TOOLS if t["name"] in {
    "get_order_details", "check_payment_status"
}]


async def run(
    message: str,
    history: List[Dict[str, Any]],
    on_token: Optional[Callable] = None,
    on_tool_start: Optional[Callable] = None,
) -> str:
    """Run Support Agent for order tracking and refund handling."""
    messages = list(history)
    messages.append({"role": "user", "content": message})

    return await _run_tool_loop(
        system=SUPPORT_SYSTEM,
        messages=messages,
        model_bedrock=BEDROCK_SUB_AGENT_MODEL,
        model_direct=ANTHROPIC_SUB_AGENT_MODEL,
        tools=SUPPORT_TOOLS,
        on_token=on_token,
        on_tool_start=on_tool_start,
    )
