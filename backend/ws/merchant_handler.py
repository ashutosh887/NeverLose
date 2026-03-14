"""Merchant Copilot WebSocket handler — analytics + offer creation for merchants."""

import json
import uuid
from typing import Any, Dict, List, Optional

from fastapi import WebSocket, WebSocketDisconnect

MERCHANT_SYSTEM = """## YOUR IDENTITY
You are Priya, the NeverLose merchant intelligence assistant for TechMart.
You help merchants understand their sales performance and take actions to recover more revenue.

## WHAT YOU KNOW
You have access to this week's NeverLose dashboard data:
- 65 carts recovered this week | ₹14,20,000 GMV recovered
- Top product: Dell XPS 15 (highest abandonment at 34% recovery rate)
- Samsung Galaxy S24 Ultra: 78% abandonment — highest opportunity
- Top signal: EXIT_INTENT (42%), CART_STALL (28%), CHECKOUT_DROP (18%)
- Top EMI scheme: HDFC 18-month No-Cost (drives 42% of conversions)
- Channel mix: Web 51%, WhatsApp 25%, UPI QR 15%, Voice 9%
- Avg deal size: ₹21,846 | Avg EMI tenure: 14.3 months

## WHAT YOU CAN DO
1. Answer questions about sales performance — reference the data above
2. Suggest which products to create flash offers for (based on abandonment)
3. Simulate creating a Pine Labs Offer Engine flash offer (instant discount, time-limited)
4. Recommend EMI scheme promotions based on conversion data
5. Show which signals are driving the most saves

## HOW TO RESPOND
- Be concise and actionable — merchants are busy
- Always lead with numbers when talking about performance
- When asked to "create an offer", say: "Done. I've pushed a [X]% instant discount via Pine Labs Offer Engine — NeverLose will now show this to hesitating customers on [product]."
- Use INR (₹) for all amounts
- Maximum 3-4 sentences per response unless doing a breakdown

## TONE
Confident, data-driven, like a smart analytics co-pilot. Not a chatbot — a business partner.
"""


async def handle_merchant_websocket(websocket: WebSocket) -> None:
    """Accept and manage a Merchant Copilot WebSocket session."""
    await websocket.accept()

    session_id = str(uuid.uuid4())
    conversation_history: List[Dict[str, Any]] = []

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

            if msg_type == "ping":
                await send({"type": "pong"})
                continue

            if msg_type == "message":
                content = (data.get("content") or "").strip()
                if not content:
                    continue

                token_buffer: List[str] = []

                async def on_token(chunk: str) -> None:
                    token_buffer.append(chunk)
                    await send({"type": "token", "content": chunk})

                try:
                    from agents.supervisor import _run_tool_loop
                    from config.aws import AWSConfig
                    from config.anthropic_config import AnthropicConfig

                    history = list(conversation_history)
                    history.append({"role": "user", "content": content})

                    if len(history) > 20:
                        history = history[-20:]

                    response = await _run_tool_loop(
                        system=MERCHANT_SYSTEM,
                        messages=history,
                        model_bedrock=AWSConfig.BEDROCK_SUPERVISOR_MODEL,
                        model_direct=AnthropicConfig.SUPERVISOR_MODEL,
                        tools=[],  # No tools for merchant copilot — pure conversational
                        on_token=on_token,
                        max_iter=3,
                    )

                    full_text = "".join(token_buffer) or response
                    if not token_buffer and full_text:
                        await send({"type": "token", "content": full_text})

                    conversation_history.append({"role": "user", "content": content})
                    conversation_history.append({"role": "assistant", "content": full_text})

                    if len(conversation_history) > 20:
                        conversation_history = conversation_history[-20:]

                    await send({
                        "type": "message_end",
                        "session_id": session_id,
                        "content_type": "text",
                    })

                except Exception as exc:
                    await send({"type": "error", "message": str(exc)})

    except WebSocketDisconnect:
        pass
    except Exception as exc:
        try:
            await websocket.send_text(json.dumps({"type": "error", "message": str(exc)}))
        except Exception:
            pass
