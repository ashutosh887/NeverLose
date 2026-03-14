"""
Payment Agent — Order creation and all three payment channels.
Model: Claude Sonnet 4.6 (higher capability for payment flows)

Three channels (always offer all three after deal confirmation):
  1. Web Checkout   → create_checkout → Infinity Checkout URL (new tab)
  2. WhatsApp Link  → generate_payment_link → wa.me pre-filled message
  3. UPI QR         → generate_qr_code → scannable QR in chat

Safety:
  - NEVER call create_checkout without user_confirmed=True
  - Policy middleware (policy.py) provides second enforcement layer
  - Max order: ₹2,00,000 (₹20,000,000 paisa)
"""

from typing import Any, Callable, Dict, List, Optional

from agents.supervisor import (
    BEDROCK_SUPERVISOR_MODEL,
    ANTHROPIC_SUPERVISOR_MODEL,
    ALL_TOOLS,
    _run_tool_loop,
)

PAYMENT_SYSTEM = """You are NeverLose Payment — you complete sales securely across three channels.

## CONFIRMATION GATE
Before calling create_checkout, the customer MUST have said words like:
"yes", "confirm", "proceed", "let's do it", "haan", "theek hai", "okay"
Only then set user_confirmed=true.
If not confirmed: ask "Shall I confirm your order for ₹X,XXX/month on EMI?"

## THREE CHANNEL PRESENTATION (always offer all three)
After deal confirmed, say:
"How would you like to complete your purchase?"
  1. 🌐 Web Checkout — opens secure payment page in your browser
  2. 💬 WhatsApp — I'll send you the payment link on WhatsApp
  3. 📱 UPI QR — scan with GPay, PhonePe, or Paytm

Call all three in parallel: create_checkout + generate_payment_link + generate_qr_code

## CHECKOUT DROP HANDLING (signal: CHECKOUT_DROP_DETECTED)
Customer dropped at payment page. Possible reasons:
1. No card → pivot to cardless EMI: "No card needed — just PAN + phone for AXIO EMI"
2. Payment failed → offer alternative channel
3. Confused → simplify: "Just scan this QR with your UPI app"

## PAYMENT STATUS
After QR/link generated: poll check_payment_status every 3s
On SUCCESS: "Payment confirmed! Your order #XXXXX is placed. Delivery in 2-3 days."
On PENDING: keep polling silently
On FAILED: offer alternative channel immediately

## LANGUAGE
Mirror customer's language. Always use ₹ symbol.
"""

PAYMENT_TOOLS = [t for t in ALL_TOOLS if t["name"] in {
    "create_checkout", "generate_payment_link", "generate_qr_code",
    "check_payment_status", "calculate_convenience_fee"
}]


async def run(
    message: str,
    history: List[Dict[str, Any]],
    signal_type: Optional[str] = None,
    on_token: Optional[Callable] = None,
    on_tool_start: Optional[Callable] = None,
) -> str:
    """Run Payment Agent to handle checkout flow across all three channels."""
    system = PAYMENT_SYSTEM
    if signal_type == "CHECKOUT_DROP_DETECTED":
        system += "\n## ACTIVE: CHECKOUT DROP\nPivot to cardless EMI or alternative channel. Remove friction immediately."

    messages = list(history)
    messages.append({"role": "user", "content": message})

    return await _run_tool_loop(
        system=system,
        messages=messages,
        model_bedrock=BEDROCK_SUPERVISOR_MODEL,
        model_direct=ANTHROPIC_SUPERVISOR_MODEL,
        tools=PAYMENT_TOOLS,
        on_token=on_token,
        on_tool_start=on_tool_start,
    )
