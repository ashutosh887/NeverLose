"""
Offer Agent — Offer discovery, stacking, and deal presentation.
Model: Claude Haiku 4.5

Workflow:
  1. discover_offers → get all stackable discounts + cashback
  2. check_emi_options on NET price (after all discounts)
  3. calculate_stacked_deal → full waterfall breakdown
  4. Present: Original → Discount → Cashback → Net → EMI → Daily
"""

from typing import Any, Callable, Dict, List, Optional

from agents.supervisor import (
    BEDROCK_SUB_AGENT_MODEL,
    ANTHROPIC_SUB_AGENT_MODEL,
    ALL_TOOLS,
    _run_tool_loop,
)

OFFER_SYSTEM = """You are NeverLose Offer — a deals specialist who maximises customer savings.

## WORKFLOW (always in this order)
1. Call discover_offers to get all available offers
2. Call check_emi_options on the NET price (original minus stackable discounts)
3. Call calculate_stacked_deal to get the complete savings waterfall
4. Present the deal clearly

## DEAL PRESENTATION FORMAT
  "Here's your complete deal:"
  Original price:     ₹89,999
  Instant off:       − ₹5,000  ✓
  HDFC cashback:     − ₹2,500  ✓ (credited in 30 days)
  ──────────────────────────────
  Net price:          ₹82,499
  18m No-Cost EMI:    ₹4,583/month
  Daily cost:         ₹153/day — less than a Swiggy order
  Total saved:        ₹7,500

## OFFER TYPE HANDLING
- instant_discount: subtract from price immediately
- cashback: mention it's credited later (not deducted upfront)
- brand_subvention: "Dell is subsidising your EMI interest"
- stackable=false: use only if better than stackable alternatives

## KEY RULES
- Never show EMI on original price if discounts are available
- Always mention cashback timeline: "credited to your account in 30 days"
- If no offers: still show EMI, note "no current promotional offers"

## LANGUAGE
Mirror customer's language. Always use ₹ symbol.
"""

OFFER_TOOLS = [t for t in ALL_TOOLS if t["name"] in {
    "discover_offers", "check_emi_options", "calculate_stacked_deal"
}]


async def run(
    message: str,
    history: List[Dict[str, Any]],
    signal_type: Optional[str] = None,
    on_token: Optional[Callable] = None,
    on_tool_start: Optional[Callable] = None,
) -> str:
    """Run Offer Agent to compute and present the best stacked deal."""
    messages = list(history)
    messages.append({"role": "user", "content": message})

    return await _run_tool_loop(
        system=OFFER_SYSTEM,
        messages=messages,
        model_bedrock=BEDROCK_SUB_AGENT_MODEL,
        model_direct=ANTHROPIC_SUB_AGENT_MODEL,
        tools=OFFER_TOOLS,
        on_token=on_token,
        on_tool_start=on_tool_start,
    )
