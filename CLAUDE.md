# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project: NeverLose

AI-powered cart abandonment recovery agent for Pine Labs merchants. Detects buyer hesitation in real-time and proactively presents stacked affordability deals (EMI + offers combined) before the customer leaves.

**Core concept:** Bring Pine Labs' full affordability stack (EMI Calculator, Offer Engine, Payment Links) forward to the moment of hesitation — not after cart abandonment.

---

## Dev Commands

### Frontend (Next.js)
```bash
npm run dev        # Start dev server on :3000
npm run build      # Production build
npm run lint       # ESLint
```

### Backend (Python FastAPI)
```bash
uvicorn main:app --reload          # Start dev server on :8000
uvicorn main:app --reload --port 8001  # Alternative port

# Run a single test
pytest tests/test_agent.py -v
pytest tests/ -k "test_emi_calculator"  # Filter by name
```

### Environment
```bash
cp .env.example .env   # Copy env template, then fill in credentials
```

Required env vars:
- `PINE_LABS_MERCHANT_ID`, `PINE_LABS_ACCESS_CODE`, `PINE_LABS_SECRET` — from dashboardv2.pluralonline.com
- `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION` — for Bedrock (provided at event)
- `ANTHROPIC_API_KEY` — fallback if Bedrock unavailable
- `USE_MOCK=true` — switches all Pine Labs API calls to mock data layer

---

## Architecture

### Stack
- **Frontend:** Next.js + Tailwind + Framer Motion, served at `:3000`
- **Backend:** Python FastAPI at `:8000`
- **Real-time:** WebSocket (bidirectional chat) + SSE (dashboard updates)
- **LLM:** Claude Sonnet 4.6 via AWS Bedrock CRIS (model ID: `us.anthropic.claude-sonnet-4-6-20251001-v1:0`); fallback to Anthropic direct API

### Agent Architecture (Multi-Agent)

```
Supervisor Agent (Sonnet 4.6)
├── Sales Agent (Haiku 4.5)     — hesitation detection, EMI + offer recommendations
├── Offer Agent (Haiku 4.5)     — offer stacking, deal calculation
├── Payment Agent (Sonnet 4.6)  — order creation, checkout, payment links
└── Support Agent (Haiku 4.5)   — order tracking, refunds
```

Agents communicate via Bedrock's multi-agent orchestration. The Supervisor routes based on intent detected in each message.

### Pine Labs Integration (via MCP Server)

All Pine Labs API calls go through the Pine Labs MCP Server in "API execution mode." The agent calls tools → MCP Gateway → Pine Labs MCP Server → Pine Labs REST APIs.

8 Pine Labs products used:
1. **EMI Calculator v3** — discovers card EMI, debit EMI, cardless EMI, brand EMI
2. **Offer Engine / Offer Discovery** — instant discounts, cashback, brand subvention
3. **Payment Gateway** — order creation
4. **Infinity Checkout** — hosted checkout URL generation (one API call)
5. **Payment Links** — shareable links for WhatsApp/SMS delivery
6. **MCP Server** — AI-native API execution layer
7. **Customers API** — customer profile for personalization
8. **Convenience Fee API** — cost comparison across payment methods

### Agent Tools

| Tool | Purpose |
|------|---------|
| `check_emi_options` | Query EMI Calculator v3 — returns all schemes with tenure, rate, savings |
| `discover_offers` | Query Offer Engine — returns stackable discounts/cashback |
| `calculate_stacked_deal` | Combine best EMI option + offers into single deal |
| `search_products` | Merchant product catalog search |
| `create_checkout` | Create Pine Labs order + Infinity Checkout URL (requires `user_confirmed=true`) |
| `generate_payment_link` | Generate Payment Link for WhatsApp/SMS delivery |
| `check_payment_status` | Poll order status |
| `get_order_details` | Full order info for support flows |
| `calculate_convenience_fee` | Compare fees across payment methods |

### Mock Data Layer

When `USE_MOCK=true`, all Pine Labs API calls are intercepted and return fixtures from `mock/` directory. Mock responses mirror exact API response format so the agent layer is unaffected. Toggle with env var — no code changes needed.

### Safety: AgentCore Policy

Cedar rules enforced at infrastructure level (outside LLM reasoning):
- Agent cannot create orders above ₹2,00,000
- Agent cannot process payment without `user_confirmed=true` in context
- Refunds above ₹50,000 require supervisor escalation

If AgentCore isn't available in the AWS account, equivalent logic lives in Python middleware (`middleware/policy.py`) — same semantics, applied before tool execution.

### Dashboard Real-Time Updates

Backend emits SSE events on each "save" (hesitation → conversion). Dashboard subscribes at `/api/events`. Events include: product, amount, EMI scheme used, offers stacked, channel (web/whatsapp), Pine Labs products attributed.

---

## Key Design Decisions

- **Offer stacking is the differentiator** — always call `discover_offers` before showing EMI; combine into a single "stacked deal" message with the breakdown
- **Lead with monthly payment, not total price** — "₹4,722/month" not "₹84,999 with EMI"
- **Cardless EMI pivot** — when customer has no eligible card, pivot immediately to AXIO/Home Credit/SBI cardless (PAN + phone only)
- **All amounts in paisa** internally (Pine Labs API format); format as ₹X,XX,XXX for display
- **Bedrock CRIS endpoint** for Mumbai region: `us.anthropic.claude-sonnet-4-6-20251001-v1:0` (cross-region inference)
- **Fallback chain:** Bedrock CRIS → Anthropic direct API → mock responses (never fail the demo)
