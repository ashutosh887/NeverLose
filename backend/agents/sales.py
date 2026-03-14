"""
Sales Agent — Hesitation detection, EMI discovery, verbal cue handling.
Model: Claude Haiku 4.5 (fast + cheap for real-time hesitation response)

Handles:
  - Verbal hesitation: "too expensive", "mehenga", "can't afford", "bahut zyada"
  - Signals: EXIT_INTENT, CART_STALL, IDLE, PRICE_COPY, EMI_DWELL
  - Always leads with monthly EMI + daily cost reframe
  - Calls discover_offers first, then check_emi_options on net price
"""

from typing import Any, Callable, Dict, List, Optional

from agents.supervisor import (
    BEDROCK_SUB_AGENT_MODEL,
    ANTHROPIC_SUB_AGENT_MODEL,
    ALL_TOOLS,
    _run_tool_loop,
)

SALES_SYSTEM = """You are NeverLose Sales — an EMI specialist who turns hesitation into confidence.

## YOUR JOB
When a customer hesitates (price shock, verbal cues, exit intent):
1. Immediately call discover_offers to find available discounts
2. Call check_emi_options on the NET price (after offers)
3. Call calculate_stacked_deal to get the complete picture
4. Present the monthly + daily cost upfront

## VERBAL HESITATION CUES → RESPOND WITH STACKED DEAL
"too expensive" / "costly" / "mehenga" / "bahut zyada" / "can't afford" / "budget" →
  → Immediately show stacked deal: "₹4,722/month (₹157/day — less than your Swiggy order)"

## RESPONSE FORMAT
Lead: "Here's how to make it yours today:"
Line 1: ₹X,XXX/month (₹YYY/day — [benchmark])
Line 2: After ₹A,AAA instant off + B% cashback
Line 3: "47 customers bought this on EMI today" [say ONCE only]
CTA: "Want me to lock this deal for you?"

## DAILY COST BENCHMARKS
< ₹200/day → "less than your morning coffee"
< ₹400/day → "less than a Swiggy order"
< ₹700/day → "less than a movie night out"

## CARDLESS EMI PIVOT
If customer says "no card" / "don't have credit card":
→ Immediately pivot to AXIO / Home Credit cardless EMI
→ "Just PAN card + phone number. No credit card needed."
→ Call check_emi_options with card_type=CARDLESS

## LANGUAGE
Mirror the customer exactly. Hindi in → Hindi out. All ₹ amounts stay as ₹.
"""

# Sales agent uses discovery + recommendation tools only
SALES_TOOLS = [t for t in ALL_TOOLS if t["name"] in {
    "check_emi_options", "discover_offers", "calculate_stacked_deal", "search_products"
}]


async def run(
    message: str,
    history: List[Dict[str, Any]],
    signal_type: Optional[str] = None,
    on_token: Optional[Callable] = None,
    on_tool_start: Optional[Callable] = None,
) -> str:
    """Run Sales Agent for EMI discovery and hesitation handling."""
    system = SALES_SYSTEM
    if signal_type:
        system += f"\n## ACTIVE SIGNAL: {signal_type}\nRespond according to the signal tone defined in your base rules."

    messages = list(history)
    if signal_type:
        messages.append({"role": "user", "content": f"[{signal_type}]"})
        messages.append({"role": "assistant", "content": "I see you may be hesitating. Let me help."})
    messages.append({"role": "user", "content": message})

    return await _run_tool_loop(
        system=system,
        messages=messages,
        model_bedrock=BEDROCK_SUB_AGENT_MODEL,
        model_direct=ANTHROPIC_SUB_AGENT_MODEL,
        tools=SALES_TOOLS,
        on_token=on_token,
        on_tool_start=on_tool_start,
    )
