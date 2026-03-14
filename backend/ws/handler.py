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

import json
import uuid
from typing import Any, Dict, List, Optional

from fastapi import WebSocket, WebSocketDisconnect

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
                            await _publish_to_sse(result, tool_name)
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


async def _publish_to_sse(tool_result: Dict[str, Any], tool_name: str) -> None:
    """Publish a conversion event to the SSE dashboard stream."""
    try:
        from sse.events import publish_event
        import datetime

        event = {
            "type": "conversion",
            "data": {
                "id": str(uuid.uuid4()),
                "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
                "tool": tool_name,
                "result_summary": {k: v for k, v in tool_result.items() if k != "qr_image_base64"},
            },
        }
        await publish_event(event)
    except Exception:
        pass
