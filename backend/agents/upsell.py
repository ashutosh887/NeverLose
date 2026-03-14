"""
Upsell Agent — ONE accessory suggestion after EMI is confirmed.
Model: Claude Haiku 4.5

Rules (all must be true to suggest):
  1. EMI already confirmed (checkout initiated or user said yes to deal)
  2. find_accessories returns an accessory for the product
  3. Accessory monthly EMI < 10% of base product monthly EMI
  4. Present as: "Add [accessory] for just ₹X/month more"
"""

from typing import Any, Callable, Dict, List, Optional

from agents.supervisor import (
    BEDROCK_SUB_AGENT_MODEL,
    ANTHROPIC_SUB_AGENT_MODEL,
    ALL_TOOLS,
    _run_tool_loop,
)

UPSELL_SYSTEM = """You are NeverLose Upsell — you suggest ONE high-value accessory after the main deal is done.

## STRICT RULES
1. ONLY suggest after the customer has confirmed their EMI deal
2. Call find_accessories with the product_id and base_monthly_emi_paisa
3. If accessory is returned: compute its monthly EMI = accessory_price / same_tenure
4. ONLY suggest if accessory_monthly_emi < 10% of base_monthly_emi
5. If threshold not met: do NOT suggest anything. Stay silent.
6. Never suggest more than ONE accessory

## PRESENTATION FORMAT
"One more thing — you can add the [Accessory Name] for just ₹X/month more.
That's [accessory price] bundled into your EMI.
Total becomes ₹Y/month — still less than ₹Z/day."

## DECLINE GRACEFULLY
If no accessories, or threshold not met:
"Your order is confirmed! Enjoy your [product]."
Never mention the upsell rule or threshold to the customer.

## LANGUAGE
Mirror customer's language. Always use ₹ symbol.
"""

UPSELL_TOOLS = [t for t in ALL_TOOLS if t["name"] in {"find_accessories"}]


async def run(
    message: str,
    history: List[Dict[str, Any]],
    product_id: Optional[str] = None,
    base_monthly_emi_paisa: Optional[int] = None,
    on_token: Optional[Callable] = None,
    on_tool_start: Optional[Callable] = None,
) -> str:
    """Run Upsell Agent after EMI confirmation."""
    # Enrich message with product context for the agent
    context_msg = message
    if product_id and base_monthly_emi_paisa:
        context_msg = (
            f"{message}\n\n"
            f"[Context: product_id={product_id}, "
            f"base_monthly_emi_paisa={base_monthly_emi_paisa}]"
        )

    messages = list(history)
    messages.append({"role": "user", "content": context_msg})

    return await _run_tool_loop(
        system=UPSELL_SYSTEM,
        messages=messages,
        model_bedrock=BEDROCK_SUB_AGENT_MODEL,
        model_direct=ANTHROPIC_SUB_AGENT_MODEL,
        tools=UPSELL_TOOLS,
        on_token=on_token,
        on_tool_start=on_tool_start,
    )
