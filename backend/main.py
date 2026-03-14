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
    from db.client import connect, disconnect
    await connect()
    print(f"[NeverLose] Starting — USE_MOCK={os.getenv('USE_MOCK', 'false')}")
    yield
    await disconnect()
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


@app.get("/health")
async def health():
    from db.client import ping as db_ping

    db_ok = await db_ping()

    pine_ok = False
    pine_error = None
    try:
        from tools.auth import get_pine_labs_token
        token = await get_pine_labs_token()
        pine_ok = bool(token)
    except Exception as exc:
        pine_error = str(exc)

    return {
        "status": "ok",
        "use_mock": os.getenv("USE_MOCK", "false").lower() == "true",
        "region": AWSConfig.REGION,
        "mongodb": {"connected": db_ok},
        "pine_labs_auth": {"ok": pine_ok, "error": pine_error},
    }


@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    from ws.handler import handle_websocket
    await handle_websocket(websocket)


@app.websocket("/ws/merchant-chat")
async def websocket_merchant_chat(websocket: WebSocket):
    from ws.merchant_handler import handle_merchant_websocket
    await handle_merchant_websocket(websocket)


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


@app.get("/api/products")
async def list_products(
    q: str = None,
    category: str = None,
    max_price: int = None,
):
    from tools.products import search_products
    return await search_products(
        query=q,
        category=category,
        max_price_paisa=max_price,
    )


@app.get("/api/products/{product_id}")
async def get_product(product_id: str):
    from tools.products import get_product as _get
    product = await _get(product_id)
    if product is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@app.get("/api/payment-status/{order_id}")
async def payment_status(order_id: str):
    use_mock = os.getenv("USE_MOCK", "false").lower() == "true"
    if use_mock:
        from pathlib import Path
        import json
        mock_file = Path(__file__).parent / "mock" / "payment_status.json"
        return json.loads(mock_file.read_text())
    try:
        from tools.checkout import check_payment_status
        return await check_payment_status(order_id=order_id)
    except Exception:
        return {"payment": {"order_id": order_id, "status": "PENDING"}}


@app.post("/api/chat")
async def chat_rest(request: Request):
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
