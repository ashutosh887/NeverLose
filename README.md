# NeverLose

### The AI Agent That Converts Every Hesitant Buyer Into a Paying Customer

AI-powered cart abandonment recovery agent for Pine Labs merchants. Detects buyer hesitation in real-time and proactively presents stacked affordability deals (EMI + offers combined) before the customer leaves.

**Core concept:** Bring Pine Labs' full affordability stack (EMI Calculator, Offer Engine, Payment Links) forward to the moment of hesitation — not after cart abandonment.

---

## How It Works

1. **Detects hesitation** — monitors cart signals (idle time, exit intent, scroll behavior)
2. **Stacks the best deal** — combines EMI options + live offers into a single compelling offer
3. **Presents in real-time** — surfaces "₹4,722/month" before the customer bounces
4. **Closes the sale** — generates a checkout URL or WhatsApp payment link instantly

---

## Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js + Tailwind + Framer Motion (`:3000`) |
| Backend | Python FastAPI (`:8000`) |
| Real-time | WebSocket (chat) + SSE (dashboard) |
| LLM | Claude Sonnet 4.6 via AWS Bedrock CRIS |

---

## Agent Architecture

```
Supervisor Agent (Sonnet 4.6)
├── Sales Agent (Haiku 4.5)     — hesitation detection, EMI + offer recommendations
├── Offer Agent (Haiku 4.5)     — offer stacking, deal calculation
├── Payment Agent (Sonnet 4.6)  — order creation, checkout, payment links
└── Support Agent (Haiku 4.5)   — order tracking, refunds
```

Agents communicate via Bedrock's multi-agent orchestration. The Supervisor routes based on intent detected in each message.

---

## Pine Labs Integration

8 Pine Labs products used via the Pine Labs MCP Server:

| Product | Role |
|---------|------|
| EMI Calculator v3 | Card EMI, debit EMI, cardless EMI, brand EMI |
| Offer Engine | Instant discounts, cashback, brand subvention |
| Payment Gateway | Order creation |
| Infinity Checkout | Hosted checkout URL (one API call) |
| Payment Links | Shareable links for WhatsApp / SMS |
| MCP Server | AI-native API execution layer |
| Customers API | Customer profile for personalization |
| Convenience Fee API | Cost comparison across payment methods |

---

## Agent Tools

| Tool | Purpose |
|------|---------|
| `check_emi_options` | Query EMI Calculator v3 — all schemes with tenure, rate, savings |
| `discover_offers` | Query Offer Engine — stackable discounts / cashback |
| `calculate_stacked_deal` | Combine best EMI + offers into a single deal |
| `search_products` | Merchant product catalog search |
| `create_checkout` | Create Pine Labs order + Infinity Checkout URL |
| `generate_payment_link` | Payment Link for WhatsApp / SMS delivery |
| `check_payment_status` | Poll order status |
| `get_order_details` | Full order info for support flows |
| `calculate_convenience_fee` | Compare fees across payment methods |

---

## Setup

```bash
cp .env.example .env   # Fill in credentials
```

Required environment variables:

```
PINE_LABS_MERCHANT_ID=
PINE_LABS_ACCESS_CODE=
PINE_LABS_SECRET=
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_REGION=
ANTHROPIC_API_KEY=      # fallback if Bedrock unavailable
USE_MOCK=true           # use mock data layer (no real API calls)
```

---

## Running Locally

**Frontend**
```bash
npm run dev        # http://localhost:3000
```

**Backend**
```bash
uvicorn main:app --reload   # http://localhost:8000
```

**Tests**
```bash
pytest tests/ -v
pytest tests/ -k "test_emi_calculator"
```

---

## Safety

Cedar policy rules enforced at infrastructure level (AgentCore):

- Cannot create orders above ₹2,00,000
- Cannot process payment without explicit `user_confirmed=true`
- Refunds above ₹50,000 require supervisor escalation

Equivalent middleware lives in `middleware/policy.py` when AgentCore is unavailable.

---

## Key Design Decisions

- **Offer stacking is the differentiator** — always call `discover_offers` before showing EMI; combine into a single stacked deal message
- **Lead with monthly payment, not total price** — "₹4,722/month" not "₹84,999 with EMI"
- **Cardless EMI pivot** — when no eligible card, pivot to AXIO / Home Credit / SBI cardless (PAN + phone only)
- **All amounts in paisa** internally (Pine Labs API format); formatted as ₹X,XX,XXX for display
- **Fallback chain:** Bedrock CRIS → Anthropic direct API → mock responses
