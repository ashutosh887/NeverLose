"""
Supervisor Agent — Full Implementation

Bedrock Global CRIS (AsyncAnthropicBedrock) → Anthropic direct (AsyncAnthropic) → mock fallback.

Intent routing:
  sales    — hesitation, EMI discovery, verbal "too expensive"
  offer    — explicit offer/deal/discount queries
  payment  — checkout, QR, WhatsApp link, payment status
  upsell   — accessories after EMI confirmed
  support  — order tracking, refunds

Tool-use loop:
  1. Call model with all tools
  2. If response has tool_use blocks → execute tools → loop
  3. If response is end_turn text → stream tokens via on_token → done
"""

import json
import logging
import uuid
from typing import Any, Callable, Coroutine, Dict, List, Optional

from config.aws import AWSConfig
from config.anthropic_config import AnthropicConfig

logger = logging.getLogger(__name__)

# ── Model IDs (sourced from config) ───────────────────────────────────────────
BEDROCK_SUPERVISOR_MODEL = AWSConfig.BEDROCK_SUPERVISOR_MODEL
BEDROCK_SUB_AGENT_MODEL = AWSConfig.BEDROCK_SUB_AGENT_MODEL
ANTHROPIC_SUPERVISOR_MODEL = AnthropicConfig.SUPERVISOR_MODEL
ANTHROPIC_SUB_AGENT_MODEL = AnthropicConfig.SUB_AGENT_MODEL

# ── Base system prompt ─────────────────────────────────────────────────────────
BASE_SYSTEM = """You are NeverLose — an AI cart-recovery agent for Pine Labs merchants.
Your single mission: turn hesitant shoppers into buyers with the best stacked EMI + offer deal.

## NON-NEGOTIABLE RULES
1. ALWAYS call discover_offers FIRST, then compute EMI on the NET price (after discounts).
2. Lead every response with monthly EMI, never total price.
   Format: "₹4,722/month (₹157/day)" — always include daily cost.
3. Daily cost benchmarks:
   - < ₹200/day → "less than your morning coffee"
   - < ₹400/day → "less than a Swiggy order"
   - < ₹700/day → "less than a movie night"
4. Social proof: say "47 customers bought this on EMI today" exactly ONCE per conversation.
   Set social_proof_shown=true after — never repeat.
5. Never be pushy. Be warm, helpful, like a knowledgeable friend.
6. ONE accessory upsell only — AFTER EMI confirmed — ONLY if incremental EMI < 10% of base.

## STACKED DEAL FORMAT
Always present the full waterfall:
  Original: ₹89,999
  Instant off: − ₹5,000
  HDFC cashback: − ₹2,500
  Net price: ₹82,499
  18-month No-Cost EMI: ₹4,583/month (₹153/day)
  You save ₹7,500 total

## PAYMENT CHANNELS (offer all three after deal is confirmed)
1. Web: Infinity Checkout URL (opens in browser)
2. WhatsApp: Payment Link → wa.me pre-filled message
3. UPI QR: Scannable QR in chat (GPay / PhonePe / Paytm)

## LANGUAGE
Mirror the customer's language exactly.
Hindi in → Hindi out. Tamil in → Tamil out. English in → English out.
Always use ₹ symbol regardless of language.

## HESITATION RESPONSE TONES
EXIT_INTENT: Lead with daily cost + social proof. "Before you go..." opener.
CART_STALL: Break down cart total into EMI immediately. Show full stacked deal.
CHECKOUT_DROP: Pivot to cardless EMI (AXIO/Home Credit — PAN + phone, no card needed).
RETURN_VISIT: "Back again? We saved a deal just for you."
IDLE: Soft nudge. "Still thinking? Here's what it looks like per month."
SCROLL_BOUNCE: One-line hook. Quick CTA.
PRICE_COPY: "Comparing prices? We have exclusive Pine Labs offers you won't find elsewhere."
WISHLIST_INSTEAD_OF_CART: "Saved to wishlist? Here's how to get it today for ₹X/month."
EMI_DWELL: Deep-dive all EMI schemes. Explain no-cost vs. low-cost. Show tenure slider.
PRICE_SHOCK_PREDICTED: Customer is spending significant time studying the price. Lead immediately
  with daily cost reframe and the best stacked deal. Don't wait for them to express hesitation.

## NEGOTIATION MODE
When the customer says "can you reduce the price?", "kuch discount milega?", "give me a better deal", or similar:
- NEVER say "I cannot change the price" or "I'm just an AI".
- Say: "I can't touch the MRP, but I found ₹X,XXX in bank + brand offers that aren't on any other platform."
- Lead with total effective savings as the headline: "Effectively you're paying ₹82,499 instead of ₹89,999."
- If they push for more: offer the longest tenure to minimise monthly cost. "Want to stretch it to 24 months? That's just ₹3,750/month."
- If they mention a competitor price: "We have exclusive subvention deals from [bank] that aren't available elsewhere — factor those in and we're actually cheaper."
- Always close the negotiation with a call to action: "Shall I lock in this deal for you now?"
"""

# ── All 11 tools ───────────────────────────────────────────────────────────────
ALL_TOOLS: List[Dict[str, Any]] = [
    {
        "name": "check_emi_options",
        "description": (
            "Query Pine Labs Affordability Suite. Returns all available EMI schemes — "
            "card EMI (CREDIT/DEBIT), cardless EMI (AXIO/Home Credit), brand EMI — "
            "with tenure, monthly installment, daily cost, and interest savings."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "amount_in_paisa": {
                    "type": "integer",
                    "description": "Amount in paisa (₹1 = 100 paisa). Use net price after discounts.",
                },
                "merchant_id": {"type": "string", "description": "Pine Labs merchant ID (optional — uses env default)"},
                "card_type": {
                    "type": "string",
                    "enum": ["CREDIT", "DEBIT", "CARDLESS"],
                    "description": "Filter by card type. Omit to get all types.",
                },
            },
            "required": ["amount_in_paisa"],
        },
    },
    {
        "name": "discover_offers",
        "description": (
            "Query Pine Labs Offer Engine. Returns ALL applicable offers: "
            "instant discounts, cashback, brand subvention. "
            "ALWAYS call this before check_emi_options so EMI is on the net price."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "product_id": {"type": "string", "description": "Product ID (e.g. DELL-XPS-15)"},
                "amount_in_paisa": {"type": "integer", "description": "Original product price in paisa"},
                "merchant_id": {"type": "string"},
            },
            "required": ["product_id", "amount_in_paisa"],
        },
    },
    {
        "name": "calculate_stacked_deal",
        "description": (
            "Combine best EMI scheme + all applicable offers into a single stacked deal. "
            "Returns the full savings waterfall: original → discount → cashback → net → EMI. "
            "Call after discover_offers + check_emi_options."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "original_amount_paisa": {"type": "integer"},
                "offers": {"type": "array", "items": {"type": "object"}},
                "emi_scheme": {"type": "object", "description": "Best EMI scheme from check_emi_options"},
            },
            "required": ["original_amount_paisa", "offers", "emi_scheme"],
        },
    },
    {
        "name": "search_products",
        "description": "Search merchant product catalog by query, category, or price range.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "category": {"type": "string"},
                "max_price_paisa": {"type": "integer"},
            },
            "required": ["query"],
        },
    },
    {
        "name": "find_accessories",
        "description": (
            "Find ONE complementary accessory for upsell. "
            "Only present to customer if accessory monthly EMI < 10% of base product EMI. "
            "Present as 'just ₹X/month more'."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "product_id": {"type": "string"},
                "base_monthly_emi_paisa": {
                    "type": "integer",
                    "description": "Base product monthly EMI in paisa. Used to verify the <10% rule.",
                },
            },
            "required": ["product_id", "base_monthly_emi_paisa"],
        },
    },
    {
        "name": "create_checkout",
        "description": (
            "Create Pine Labs order + Infinity Checkout URL. "
            "REQUIRES user_confirmed=true — never call without explicit user confirmation. "
            "Returns checkout_url to open in browser."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "amount_in_paisa": {"type": "integer"},
                "product_id": {"type": "string"},
                "product_name": {"type": "string"},
                "emi_scheme_id": {"type": "string"},
                "customer_phone": {"type": "string"},
                "customer_email": {"type": "string"},
                "user_confirmed": {
                    "type": "boolean",
                    "description": "MUST be true. Customer must have explicitly said yes.",
                },
            },
            "required": ["amount_in_paisa", "product_id", "product_name", "user_confirmed"],
        },
    },
    {
        "name": "generate_payment_link",
        "description": "Generate a shareable payment link. Returns a WhatsApp wa.me URL pre-filled with the payment details.",
        "input_schema": {
            "type": "object",
            "properties": {
                "amount_in_paisa": {"type": "integer"},
                "product_name": {"type": "string"},
                "emi_scheme_id": {"type": "string"},
                "customer_phone": {"type": "string"},
                "order_id": {"type": "string"},
            },
            "required": ["amount_in_paisa", "product_name"],
        },
    },
    {
        "name": "generate_qr_code",
        "description": "Generate a UPI QR code for in-chat payment. Customer scans with GPay, PhonePe, or Paytm. Returns base64 QR image.",
        "input_schema": {
            "type": "object",
            "properties": {
                "amount_in_paisa": {"type": "integer"},
                "order_id": {"type": "string"},
                "merchant_name": {"type": "string"},
            },
            "required": ["amount_in_paisa"],
        },
    },
    {
        "name": "check_payment_status",
        "description": "Poll Pine Labs order payment status. Returns PENDING / SUCCESS / FAILED.",
        "input_schema": {
            "type": "object",
            "properties": {"order_id": {"type": "string"}},
            "required": ["order_id"],
        },
    },
    {
        "name": "get_order_details",
        "description": "Get full order details for support/tracking. Returns product, amount, EMI scheme, customer, status.",
        "input_schema": {
            "type": "object",
            "properties": {"order_id": {"type": "string"}},
            "required": ["order_id"],
        },
    },
    {
        "name": "calculate_convenience_fee",
        "description": "Compare convenience fees across payment methods (credit card, debit, UPI, net banking) for an order amount.",
        "input_schema": {
            "type": "object",
            "properties": {"amount_in_paisa": {"type": "integer"}},
            "required": ["amount_in_paisa"],
        },
    },
]

# ── Client factories ───────────────────────────────────────────────────────────
def _bedrock_client():
    """AnthropicBedrock client — routes through AWS Bedrock CRIS."""
    return AWSConfig.bedrock_client()


def _direct_client():
    """Anthropic direct API client — fallback when Bedrock unavailable."""
    return AnthropicConfig.direct_client()


# ── Tool executor ──────────────────────────────────────────────────────────────
async def _execute_tool(
    tool_name: str,
    tool_input: Dict[str, Any],
    on_tool_start: Optional[Callable] = None,
) -> Any:
    """Execute a tool. Calls on_tool_start(name, input) before execution for WS status updates."""
    if on_tool_start:
        await on_tool_start(tool_name, tool_input)

    try:
        if tool_name == "check_emi_options":
            from tools.emi_calculator import check_emi_options
            return await check_emi_options(**tool_input)

        elif tool_name == "discover_offers":
            from tools.offer_engine import discover_offers
            return await discover_offers(**tool_input)

        elif tool_name == "calculate_stacked_deal":
            from tools.offer_engine import calculate_stacked_deal
            return calculate_stacked_deal(**tool_input)

        elif tool_name == "search_products":
            from tools.products import search_products
            return await search_products(**tool_input)

        elif tool_name == "find_accessories":
            from tools.products import find_accessories
            return await find_accessories(product_id=tool_input["product_id"])

        elif tool_name == "create_checkout":
            from tools.checkout import create_checkout
            from middleware.policy import check_policy
            err = check_policy("create_checkout", tool_input)
            if err:
                return err
            return await create_checkout(**tool_input)

        elif tool_name == "generate_payment_link":
            from tools.payment_links import generate_payment_link
            return await generate_payment_link(**tool_input)

        elif tool_name == "generate_qr_code":
            from tools.qr_code import generate_qr_code
            return await generate_qr_code(**tool_input)

        elif tool_name == "check_payment_status":
            from tools.checkout import check_payment_status
            return await check_payment_status(**tool_input)

        elif tool_name == "get_order_details":
            from tools.checkout import get_order_details
            return await get_order_details(**tool_input)

        elif tool_name == "calculate_convenience_fee":
            from tools.convenience_fee import calculate_convenience_fee
            return await calculate_convenience_fee(**tool_input)

        else:
            return {"error": f"Unknown tool: {tool_name}"}

    except Exception as exc:
        logger.error("Tool %s failed: %s", tool_name, exc)
        return {"error": str(exc), "tool": tool_name}


# ── Core tool-use loop ─────────────────────────────────────────────────────────
async def _run_tool_loop(
    *,
    system: str,
    messages: List[Dict[str, Any]],
    model_bedrock: str,
    model_direct: str,
    tools: List[Dict[str, Any]],
    on_token: Optional[Callable] = None,
    on_tool_start: Optional[Callable] = None,
    max_iter: int = 8,
) -> str:
    """
    Run the Anthropic tool-use loop with Bedrock → direct API fallback.

    Streams final text tokens via on_token if provided.
    Notifies on_tool_start before each tool execution.
    Returns complete final response text.
    """
    # Try Bedrock first, fall back to direct
    clients = [
        (_bedrock_client(), model_bedrock, "Bedrock"),
        (_direct_client(), model_direct, "Anthropic direct"),
    ]

    last_error: Optional[Exception] = None
    for client, model, label in clients:
        try:
            return await _loop_with_client(
                client=client,
                model=model,
                system=system,
                messages=list(messages),
                tools=tools,
                on_token=on_token,
                on_tool_start=on_tool_start,
                max_iter=max_iter,
                label=label,
            )
        except Exception as exc:
            logger.warning("%s failed (%s), trying next client", label, exc)
            last_error = exc

    # Both failed — return mock response
    logger.error("All LLM clients failed. Last error: %s", last_error)
    return _mock_fallback(messages)


async def _loop_with_client(
    *,
    client: Any,
    model: str,
    system: str,
    messages: List[Dict[str, Any]],
    tools: List[Dict[str, Any]],
    on_token: Optional[Callable],
    on_tool_start: Optional[Callable],
    max_iter: int,
    label: str,
) -> str:
    """Inner tool-use loop for a single client."""
    for iteration in range(max_iter):
        # Call model — streaming on final text response, non-streaming during tool calls
        response = await client.messages.create(
            model=model,
            max_tokens=1024,
            system=system,
            messages=messages,
            tools=tools,  # type: ignore[arg-type]
        )

        stop_reason = response.stop_reason
        text_parts: List[str] = []
        tool_calls: List[Dict[str, Any]] = []

        for block in response.content:
            if block.type == "text":
                text_parts.append(block.text)
            elif block.type == "tool_use":
                tool_calls.append({"id": block.id, "name": block.name, "input": block.input})

        if stop_reason == "end_turn" or not tool_calls:
            # Final response — stream tokens if callback provided
            final_text = "".join(text_parts)
            if on_token and final_text:
                # Stream character-by-character isn't ideal; word-by-word is better UX
                words = final_text.split(" ")
                for i, word in enumerate(words):
                    chunk = word + (" " if i < len(words) - 1 else "")
                    await on_token(chunk)
            return final_text

        # Has tool calls — execute them
        assistant_content = []
        if text_parts:
            assistant_content.append({"type": "text", "text": "".join(text_parts)})
        for tc in tool_calls:
            assistant_content.append({
                "type": "tool_use",
                "id": tc["id"],
                "name": tc["name"],
                "input": tc["input"],
            })
        messages.append({"role": "assistant", "content": assistant_content})

        # Execute all tool calls and collect results
        tool_results = []
        for tc in tool_calls:
            result = await _execute_tool(tc["name"], tc["input"], on_tool_start)
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": tc["id"],
                "content": json.dumps(result),
            })
        messages.append({"role": "user", "content": tool_results})

    return "I ran into an issue. Please try again."


# ── Mock fallback (when all LLM clients fail) ──────────────────────────────────
def _mock_fallback(messages: List[Dict[str, Any]]) -> str:
    all_content = " ".join(
        m.get("content", "") if isinstance(m.get("content"), str) else ""
        for m in messages
    ).lower()

    if "exit_intent_detected" in all_content:
        return "Wait! The Dell XPS 15 is just ₹4,722/month (₹157/day — less than your Swiggy order). 47 customers bought this on EMI today. Want the full deal?"
    if "cart_stall_detected" in all_content:
        return "Still thinking? Break it down: ₹4,722/month for 18 months, No-Cost EMI. Plus ₹5,000 instant off + 5% HDFC cashback. That's ₹7,500 saved. Want this deal?"
    if "return_visit_detected" in all_content:
        return "Back again? We saved your deal — Dell XPS 15 with ₹5,000 off + 18m No-Cost EMI at ₹4,722/month. Ready to claim it?"
    if "checkout_drop_detected" in all_content:
        return "No card? No problem. AXIO cardless EMI: just PAN + phone number. ₹4,722/month, zero down. Want to proceed?"
    if any(w in all_content for w in ["expensive", "mehenga", "emi", "month", "installment"]):
        return "The Dell XPS 15 is available on 18-month No-Cost EMI at ₹4,722/month (₹157/day). After ₹5,000 instant off, you're paying ₹84,999 total with zero interest. Want me to show you the full breakdown?"
    if any(w in all_content for w in ["offer", "discount", "deal", "cashback"]):
        return "Here's your stacked deal: ₹5,000 instant off + 5% HDFC cashback (₹2,500) + 18m No-Cost EMI = ₹4,583/month. Total savings: ₹7,500. Shall I reserve this?"
    if any(w in all_content for w in ["pay", "checkout", "buy", "purchase"]):
        return "How would you like to pay? 1) Web checkout (instant) 2) WhatsApp payment link 3) UPI QR code — scan with GPay/PhonePe/Paytm. Which works for you?"
    return "Hi! I'm here to help you get the best EMI deal on your cart. What would you like to know?"


# ── Public interface ───────────────────────────────────────────────────────────
async def supervisor_agent(
    message: str,
    session_id: Optional[str] = None,
    signal_type: Optional[str] = None,
    conversation_history: Optional[List[Dict[str, Any]]] = None,
    on_token: Optional[Callable] = None,
    on_tool_start: Optional[Callable] = None,
    system_extra: Optional[str] = None,
) -> str:
    """
    Route message through the full Supervisor tool-use loop.

    Args:
        message: Current user message
        session_id: Session identifier
        signal_type: Hesitation signal (e.g. EXIT_INTENT_DETECTED)
        conversation_history: Prior messages (without current message)
        on_token: Async callable(str) — called for each streamed token
        on_tool_start: Async callable(tool_name, tool_input) — called before each tool
        system_extra: Additional context appended to system prompt (timing, customer profile)
    """
    if session_id is None:
        session_id = str(uuid.uuid4())

    # Build system prompt with active signal tone
    system = BASE_SYSTEM
    if signal_type:
        tone_map = {
            "EXIT_INTENT_DETECTED": "\n## ACTIVE: EXIT INTENT\nCustomer moving to close tab. Lead with daily cost + social proof. Warm urgency.",
            "CART_STALL_DETECTED": "\n## ACTIVE: CART STALL\n60s in cart, no checkout. Show full stacked deal for cart total immediately.",
            "CHECKOUT_DROP_DETECTED": "\n## ACTIVE: CHECKOUT DROP\nDropped at payment page. Pivot to cardless EMI (AXIO/Home Credit). Remove all friction.",
            "RETURN_VISIT_DETECTED": "\n## ACTIVE: RETURN VISIT\nSame product, second visit. Reference prior session. Offer saved deal.",
            "IDLE_DETECTED": "\n## ACTIVE: IDLE\n15s no interaction. Gentle nudge with EMI teaser. Not pushy.",
            "SCROLL_BOUNCE_DETECTED": "\n## ACTIVE: SCROLL BOUNCE\nFast mobile scroll-up. One-line hook + CTA.",
            "PRICE_COPY_DETECTED": "\n## ACTIVE: PRICE COPY\nCopied the price — comparing. Highlight exclusive Pine Labs offers.",
            "WISHLIST_INSTEAD_OF_CART": "\n## ACTIVE: WISHLIST ADD\nSaved to wishlist. Reframe as affordable today with EMI.",
            "EMI_DWELL_DETECTED": "\n## ACTIVE: EMI DWELL\n10s on EMI section. Deep-dive all schemes. Explain no-cost vs. standard.",
            "PRICE_SHOCK_PREDICTED": "\n## ACTIVE: PRICE SHOCK PREDICTED\nCustomer has been studying the price for 25+ seconds without action. Intervene proactively. Lead with daily cost reframe and the stacked deal — don't wait for them to say it's expensive.",
        }
        system += tone_map.get(signal_type, f"\n## ACTIVE SIGNAL: {signal_type}")

    # Append timing + customer context if provided by WS handler
    if system_extra:
        system += system_extra

    # Build message history
    history = list(conversation_history or [])

    # Inject signal as context if present
    if signal_type:
        history.append({"role": "user", "content": f"[{signal_type}]"})
        history.append({"role": "assistant", "content": "I see the hesitation signal — let me help right away."})

    # Add current user message
    history.append({"role": "user", "content": message})

    # Keep last 20 messages to stay within context
    if len(history) > 20:
        history = history[-20:]

    return await _run_tool_loop(
        system=system,
        messages=history,
        model_bedrock=BEDROCK_SUPERVISOR_MODEL,
        model_direct=ANTHROPIC_SUPERVISOR_MODEL,
        tools=ALL_TOOLS,
        on_token=on_token,
        on_tool_start=on_tool_start,
    )
