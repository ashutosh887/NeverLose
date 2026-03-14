"""
WebSocket Handler — Full streaming implementation.

Per-connection state:
  session_id            — unique ID for this chat session
  conversation_history  — list of {"role", "content"} dicts
  signal_type           — last received hesitation signal (consumed on next message)
  content_type          — last tool result type (drives frontend rich UI)
  last_tool_data        — last tool result payload (sent in message_end)

Client → Server protocol:
  { "type": "message", "content": "user text" }
  { "type": "signal",  "signal_type": "EXIT_INTENT_DETECTED" }
  { "type": "ping" }

Server → Client protocol:
  { "type": "token",       "content": "partial text" }
  { "type": "tool_start",  "tool": "check_emi_options", "status": "Checking EMI options..." }
  { "type": "tool_event",  "tool": "...", "content_type": "emi_schemes", "data": {...} }
  { "type": "message_end", "session_id": "...", "content_type": "text|emi_schemes|...", "data": {...} }
  { "type": "signal_ack",  "signal_type": "EXIT_INTENT_DETECTED" }
  { "type": "error",       "message": "..." }
  { "type": "pong" }
"""

import datetime
import json
import os
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import WebSocket, WebSocketDisconnect

_MOCK_DIR = Path(__file__).parent.parent / "mock"


def _get_timing_context() -> str:
    """Returns time-of-day context string for Smart Timing Engine."""
    hour = datetime.datetime.now().hour
    if hour < 6:
        return "late_night"
    elif hour < 12:
        return "morning"
    elif hour < 17:
        return "afternoon"
    elif hour < 21:
        return "evening"
    else:
        return "night"


_TIMING_TONE: Dict[str, str] = {
    "late_night": "Customer is browsing late at night — likely serious consideration. Lead with longest EMI tenure to minimise monthly cost. Calm, no-pressure tone.",
    "morning": "Morning browse — likely on their way to work. Be crisp, lead with the daily cost number. Quick CTA.",
    "afternoon": "Afternoon session — customer has time. Go deeper into stacked deal breakdown and tenure options.",
    "evening": "Evening peak shopping window. High intent. Lead with instant cashback + social proof. Create mild urgency: 'Offer ends tonight'.",
    "night": "Night browsing — relaxed, high purchase intent. Lead with longest EMI. 'Sleep on it with this deal locked in.'",
}


def _load_customer_profile() -> Optional[Dict[str, Any]]:
    """Load demo customer profile. In production this would come from Customers API."""
    try:
        use_mock = os.getenv("USE_MOCK", "true").lower() == "true"
        if use_mock:
            return json.loads((_MOCK_DIR / "customer_profile.json").read_text()).get("customer")
        return None
    except Exception:
        return None


def _build_customer_context(profile: Optional[Dict[str, Any]]) -> str:
    """Build a customer affordability profile context block for the system prompt."""
    if not profile:
        return ""

    lines = ["\n## CUSTOMER AFFORDABILITY PROFILE"]
    name = profile.get("name")
    if name:
        lines.append(f"Customer name: {name}")

    lang = profile.get("preferred_language")
    if lang and lang != "en":
        lines.append(f"Preferred language: {lang} — respond in this language.")

    cards = profile.get("cards_on_file", [])
    if cards:
        card = cards[0]
        lines.append(f"Card on file: {card.get('bank')} {card.get('card_type', 'credit')} ending {card.get('last_four', '****')}")
        tenures = card.get("eligible_tenures", [])
        if tenures:
            lines.append(f"Eligible EMI tenures: {', '.join(str(t) + 'm' for t in tenures)}")

    pref = profile.get("emi_preference", {})
    if pref:
        lines.append(f"Preferred tenure from history: {pref.get('preferred_tenure')} months via {pref.get('preferred_bank')}")
        lines.append("When presenting EMI options, lead with their preferred tenure first.")

    history = profile.get("purchase_history", [])
    if history:
        last = history[-1]
        lines.append(
            f"Last purchase: {last.get('product')} at {last.get('amount_paisa', 0) // 100:,} — "
            f"used {'EMI' if last.get('emi_used') else 'full payment'}"
        )
        lines.append("Reference prior EMI behaviour: 'Based on your previous purchase, customers like you chose X months.'")

    hesitation = profile.get("hesitation_history", [])
    if hesitation:
        product_ids = [h.get("product_id") for h in hesitation]
        lines.append(f"Previously hesitated on: {', '.join(str(p) for p in product_ids if p)}")

    return "\n".join(lines)

# Tool → frontend contentType for rich UI rendering
TOOL_CONTENT_TYPE: Dict[str, str] = {
    "check_emi_options": "emi_schemes",
    "calculate_stacked_deal": "stacked_deal",
    "create_checkout": "payment_options",
    "generate_payment_link": "payment_options",
    "generate_qr_code": "payment_options",
    "find_accessories": "accessory_upsell",
}

# Human-readable tool status messages shown while tool is running
TOOL_STATUS: Dict[str, str] = {
    "check_emi_options": "Checking EMI options...",
    "discover_offers": "Finding best offers...",
    "calculate_stacked_deal": "Calculating your stacked deal...",
    "search_products": "Searching products...",
    "find_accessories": "Finding accessories...",
    "create_checkout": "Creating your order...",
    "generate_payment_link": "Generating payment link...",
    "generate_qr_code": "Generating UPI QR code...",
    "check_payment_status": "Checking payment status...",
    "get_order_details": "Fetching order details...",
    "calculate_convenience_fee": "Comparing payment options...",
}


async def handle_websocket(websocket: WebSocket) -> None:
    """Accept and manage a full streaming WebSocket chat session."""
    await websocket.accept()

    session_id = str(uuid.uuid4())
    conversation_history: List[Dict[str, Any]] = []
    pending_signal: Optional[str] = None

    # Smart Timing Engine — built once per session at connection time
    timing_ctx = _get_timing_context()
    timing_note = _TIMING_TONE.get(timing_ctx, "")

    # Customer Affordability Profile — loaded once per session
    customer_profile = _load_customer_profile()
    customer_ctx = _build_customer_context(customer_profile)

    # Extra system additions (timing + customer) passed to supervisor
    _session_system_extra = (
        (f"\n## SMART TIMING: {timing_ctx.upper()}\n{timing_note}" if timing_note else "")
        + customer_ctx
    )

    async def send(data: Dict[str, Any]) -> None:
        try:
            await websocket.send_text(json.dumps(data))
        except Exception:
            pass

    try:
        while True:
            raw = await websocket.receive_text()

            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                await send({"type": "error", "message": "Invalid JSON"})
                continue

            msg_type = data.get("type")

            # ── Ping ─────────────────────────────────────────────────────────
            if msg_type == "ping":
                await send({"type": "pong"})
                continue

            # ── Hesitation signal ─────────────────────────────────────────────
            if msg_type == "signal":
                pending_signal = data.get("signal_type")
                await send({"type": "signal_ack", "signal_type": pending_signal})
                continue

            # ── Chat message ──────────────────────────────────────────────────
            if msg_type == "message":
                content = (data.get("content") or "").strip()
                if not content:
                    continue

                # Capture and consume the pending signal
                active_signal = pending_signal
                pending_signal = None

                # State for this response turn
                content_type = "text"
                last_tool_data: Optional[Any] = None
                token_buffer: List[str] = []

                # Callbacks for the agent
                async def on_token(chunk: str) -> None:
                    token_buffer.append(chunk)
                    await send({"type": "token", "content": chunk})

                async def on_tool_start(tool_name: str, tool_input: Dict[str, Any]) -> None:
                    nonlocal content_type, last_tool_data
                    status = TOOL_STATUS.get(tool_name, f"Running {tool_name}...")
                    await send({"type": "tool_start", "tool": tool_name, "status": status})

                # Monkey-patch _execute_tool to intercept results for frontend
                from agents import supervisor as sup
                original_execute = sup._execute_tool

                async def intercepting_execute(tool_name: str, tool_input: Dict[str, Any], _on_start=None) -> Any:
                    result = await original_execute(tool_name, tool_input, on_tool_start)
                    nonlocal content_type, last_tool_data
                    ct = TOOL_CONTENT_TYPE.get(tool_name)
                    if ct:
                        content_type = ct
                        last_tool_data = result
                        await send({
                            "type": "tool_event",
                            "tool": tool_name,
                            "content_type": ct,
                            "data": result,
                        })
                        # Publish payment events to SSE dashboard
                        if tool_name in ("create_checkout", "generate_qr_code", "generate_payment_link"):
                            await _publish_to_sse(result, tool_name, tool_input, active_signal)
                    return result

                sup._execute_tool = intercepting_execute  # type: ignore[assignment]

                try:
                    from agents.supervisor import supervisor_agent
                    response = await supervisor_agent(
                        message=content,
                        session_id=session_id,
                        signal_type=active_signal,
                        conversation_history=list(conversation_history),
                        on_token=on_token,
                        on_tool_start=on_tool_start,
                        system_extra=_session_system_extra,
                    )

                    # If Bedrock path (no streaming), tokens weren't sent — send full text now
                    full_text = "".join(token_buffer) or response
                    if not token_buffer and full_text:
                        await send({"type": "token", "content": full_text})

                    # Record in history
                    conversation_history.append({"role": "user", "content": content})
                    conversation_history.append({"role": "assistant", "content": full_text})

                    # Cap history
                    if len(conversation_history) > 20:
                        conversation_history = conversation_history[-20:]

                    await send({
                        "type": "message_end",
                        "session_id": session_id,
                        "content_type": content_type,
                        "data": last_tool_data,
                    })

                except Exception as exc:
                    await send({"type": "error", "message": str(exc)})
                finally:
                    sup._execute_tool = original_execute  # type: ignore[assignment]

    except WebSocketDisconnect:
        pass
    except Exception as exc:
        try:
            await websocket.send_text(json.dumps({"type": "error", "message": str(exc)}))
        except Exception:
            pass


_PRODUCT_NAMES: Dict[str, str] = {
    "MBP-16-2024": 'Apple MacBook Pro 16"',
    "DELL-XPS-15": "Dell XPS 15",
    "SAMSUNG-S24": "Samsung Galaxy S24 Ultra",
    "LG-WASHER": "LG 8kg Front Load Washer",
}

_CITIES = ["Mumbai", "Bengaluru", "Delhi", "Hyderabad", "Chennai", "Pune", "Kolkata", "Ahmedabad"]


async def _publish_to_sse(
    tool_result: Dict[str, Any],
    tool_name: str,
    tool_input: Optional[Dict[str, Any]] = None,
    signal_type: Optional[str] = None,
) -> None:
    """Publish a ConversionEvent to the SSE dashboard stream."""
    try:
        from sse.events import publish_event
        import datetime
        import random

        # Channel
        channel = "web"
        if tool_name == "generate_payment_link":
            channel = "whatsapp"
        elif tool_name == "generate_qr_code":
            channel = "qr"

        # Amount — try tool_input first, then tool_result.order
        amount_paisa: int = 8499900
        if tool_input and isinstance(tool_input.get("amount_paisa"), int):
            amount_paisa = tool_input["amount_paisa"]
        elif isinstance(tool_result.get("order", {}).get("amount_paisa"), int):
            amount_paisa = tool_result["order"]["amount_paisa"]

        rupees = amount_paisa // 100
        amount_display = f"₹{rupees:,}"

        # Product
        product_id = (tool_input or {}).get("product_id", "DELL-XPS-15")
        product = _PRODUCT_NAMES.get(product_id, product_id)

        # EMI scheme — best-effort extraction or sensible default
        tenure = (tool_input or {}).get("tenure_months", 18)
        bank = (tool_input or {}).get("bank_name", "HDFC Bank")
        monthly_paisa = amount_paisa // max(tenure, 1)
        emi_scheme = {
            "bank": bank,
            "tenure_months": tenure,
            "monthly_display": f"₹{monthly_paisa // 100:,}",
            "is_no_cost": True,
        }

        # Pine Labs products attributed
        pine_labs = ["EMI Calculator v3", "Offer Engine"]
        if tool_name == "create_checkout":
            pine_labs.append("Infinity Checkout")
        elif tool_name == "generate_payment_link":
            pine_labs.append("Payment Links")
        elif tool_name == "generate_qr_code":
            pine_labs.append("UPI QR Code")

        # Normalise signal — ensure _DETECTED suffix
        signal = signal_type or "EXIT_INTENT_DETECTED"
        if signal and not signal.endswith("_DETECTED") and signal != "WISHLIST_INSTEAD_OF_CART":
            signal = signal + "_DETECTED"

        event = {
            "type": "conversion",
            "data": {
                "id": f"SAVE-{random.randint(100, 999)}",
                "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
                "product": product,
                "product_id": product_id,
                "amount_paisa": amount_paisa,
                "amount_display": amount_display,
                "emi_scheme": emi_scheme,
                "channel": channel,
                "signal": signal,
                "pine_labs_products": pine_labs,
                "customer_city": random.choice(_CITIES),
            },
        }
        await publish_event(event)
    except Exception:
        pass
