"""
NeverLose — FastAPI Backend
AI-powered cart abandonment recovery agent for Pine Labs merchants.

Endpoints:
  GET  /health         — health check
  WS   /ws/chat        — bidirectional agent chat
  GET  /api/events     — SSE stream for merchant dashboard
  POST /api/chat       — REST fallback for chat
"""

import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from config.aws import AWSConfig

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"[NeverLose] Starting up — USE_MOCK={os.getenv('USE_MOCK', 'false')}")
    yield
    print("[NeverLose] Shutting down")


app = FastAPI(
    title="NeverLose",
    version="1.0.0",
    description="AI-powered cart abandonment recovery for Pine Labs merchants",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        os.getenv("FRONTEND_URL", "http://localhost:3000"),
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Health ────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "use_mock": os.getenv("USE_MOCK", "false").lower() == "true",
        "region": AWSConfig.REGION,
    }


# ── WebSocket Chat ────────────────────────────────────────────────

@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    from ws.handler import handle_websocket
    await handle_websocket(websocket)


# ── SSE Dashboard Events ──────────────────────────────────────────

@app.get("/api/events")
async def sse_events(request: Request):
    from sse.events import event_stream
    return StreamingResponse(
        event_stream(request),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


# ── Payment Status ────────────────────────────────────────────────

@app.get("/api/payment-status/{order_id}")
async def payment_status(order_id: str):
    """Poll UPI/payment status — used by QRCodeDisplay to check if payment completed."""
    use_mock = os.getenv("USE_MOCK", "false").lower() == "true"
    if use_mock:
        from pathlib import Path
        import json
        mock_file = Path(__file__).parent / "mock" / "payment_status.json"
        return json.loads(mock_file.read_text())
    try:
        from integrations.pine_labs import check_payment_status as pl_check
        return await pl_check(order_id)
    except Exception:
        return {"payment": {"order_id": order_id, "status": "PENDING"}}


# ── REST Chat Fallback ────────────────────────────────────────────

@app.post("/api/chat")
async def chat_rest(request: Request):
    """REST fallback when WebSocket is not available."""
    body = await request.json()
    message = body.get("message", "")
    session_id = body.get("session_id")
    signal_type = body.get("signal_type")

    from agents.supervisor import supervisor_agent
    response = await supervisor_agent(
        message=message,
        session_id=session_id,
        signal_type=signal_type,
    )
    return {"response": response, "session_id": session_id}
