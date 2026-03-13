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
├── Payment Agent (Sonnet 4.6)  — order creation, checkout, payment links, QR codes
├── Upsell Agent (Haiku 4.5)    — accessory recommendations, AOV optimization
└── Support Agent (Haiku 4.5)   — order tracking, refunds
```

Agents communicate via Bedrock's multi-agent orchestration. The Supervisor routes based on intent detected in each message.

### Pine Labs Integration (via MCP Server)

All Pine Labs API calls go through the Pine Labs MCP Server in "API execution mode." The agent calls tools → MCP Gateway → Pine Labs MCP Server → Pine Labs REST APIs.

9 Pine Labs products used:
1. **EMI Calculator v3** — discovers card EMI, debit EMI, cardless EMI, brand EMI
2. **Offer Engine / Offer Discovery** — instant discounts, cashback, brand subvention
3. **Payment Gateway** — order creation
4. **Infinity Checkout** — hosted checkout URL generation (one API call)
5. **Payment Links** — shareable links for WhatsApp/SMS delivery
6. **UPI QR Code** — scannable in-chat QR; customer pays with GPay/PhonePe/Paytm
7. **MCP Server** — AI-native API execution layer
8. **Customers API** — customer profile for personalization
9. **Convenience Fee API** — cost comparison across payment methods

### Agent Tools

| Tool | Purpose |
|------|---------|
| `check_emi_options` | Query EMI Calculator v3 — returns all schemes with tenure, rate, savings |
| `discover_offers` | Query Offer Engine — returns stackable discounts/cashback |
| `calculate_stacked_deal` | Combine best EMI option + offers into single deal |
| `search_products` | Merchant product catalog search |
| `find_accessories` | Find complementary accessories for smart upsell (AOV optimizer) |
| `create_checkout` | Create Pine Labs order + Infinity Checkout URL (requires `user_confirmed=true`) |
| `generate_payment_link` | Generate Payment Link for WhatsApp/SMS delivery |
| `generate_qr_code` | Generate UPI QR code for in-chat payment (GPay/PhonePe/Paytm) |
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
- **Daily cost reframing** — always include daily equivalent ("₹157/day — less than your Swiggy order"); calculated as `monthly_emi / 30`
- **Full hesitation signal stack** — monitor all of: exit intent (cursor to viewport top), idle time (15s no interaction), scroll bounce (fast mobile scroll-up), cart stall (60s in cart no checkout), checkout drop (30s on payment page), return visit (same product 2nd view), price copy (clipboard event), wishlist-instead-of-cart, verbal hesitation ("too expensive"/"mehenga"), long EMI dwell (10s on EMI section) — each maps to a specific `[SIGNAL_TYPE]` system message that changes agent tone
- **Exit intent system message** — `[EXIT_INTENT_DETECTED]`; agent leads with daily cost + social proof
- **Cart stall system message** — `[CART_STALL_DETECTED]`; agent leads with EMI breakdown for cart total
- **Checkout drop system message** — `[CHECKOUT_DROP_DETECTED]`; agent pivots immediately to cardless EMI or strongest offer
- **Return visit system message** — `[RETURN_VISIT_DETECTED]`; agent references prior session ("Back again? Here's a deal we saved for you")
- **Social proof on first message** — inject seeded stats ("47 customers bought this on EMI today") once per conversation; never repeat
- **Smart upsell / AOV optimizer** — suggest ONE accessory only if its incremental monthly EMI is <10% of the base product EMI; present as "just ₹167/month more"
- **Three payment channels** — always ask: web checkout (Infinity Checkout), WhatsApp link (Payment Links API), or UPI QR code (UPI QR API); meet the customer wherever they are
- **QR payment in chat** — `generate_qr_code` returns a UPI string; rendered as a scannable QR directly in the chat widget
- **EMI tenure slider** — when presenting EMI options, render an interactive slider component; dragging tenure shows live monthly/daily cost update
- **Cardless EMI pivot** — when customer has no eligible card, pivot immediately to AXIO/Home Credit/SBI cardless (PAN + phone only)
- **All amounts in paisa** internally (Pine Labs API format); format as ₹X,XX,XXX for display
- **Bedrock CRIS endpoint** for Mumbai region: `us.anthropic.claude-sonnet-4-6-20251001-v1:0` (cross-region inference)
- **Fallback chain:** Bedrock CRIS → Anthropic direct API → mock responses (never fail the demo)

---

## Multilingual Support

Claude handles all Indian languages natively — no translation layer, no extra API, zero marginal cost.

**System prompt addition** (one section in the agent system prompt):
```
## LANGUAGE
Always respond in the same language the customer uses.
If they speak Hindi, respond in Hindi. If Tamil, respond in Tamil. If Telugu, respond in Telugu.
Format EMI amounts with ₹ regardless of language.
```

**Supported languages (native Claude capability):** Hindi, Tamil, Telugu, Kannada, Malayalam, Bengali, Marathi, Gujarati, Punjabi, Odia, and English.

**Demo moment:** Customer types "yeh laptop bahut mehenga hai, koi EMI option hai kya?" → agent responds in Hindi with the stacked EMI + offer breakdown.

**Why it matters:** India has 900M+ internet users; only ~125M are comfortable in English. An EMI agent that only works in English misses 85% of the addressable market.

---

## Voice Input

Implemented via the browser's Web Speech API — no backend changes, no third-party service.

```javascript
const recognition = new webkitSpeechRecognition();
recognition.lang = 'hi-IN'; // or auto-detect from browser locale
recognition.interimResults = false;
recognition.onresult = (e) => {
  const text = e.results[0][0].transcript;
  sendToAgent(text); // same flow as typed input
};
```

**Demo moment:** Judge watches the presenter speak into their phone mic in Hindi → NeverLose responds in Hindi with EMI options. Goosebump territory for Indian judges.

**Implementation scope:**
| Feature | Effort | Demo Impact | Status |
|---------|--------|-------------|--------|
| Voice input (Web Speech API) | 30 min | HIGH | Included |
| Multilingual responses (system prompt) | 15 min | HIGH | Included |
| Voice output — ElevenLabs TTS | 2+ hrs | Negative | Excluded |
| Voice output — browser speechSynthesis | 20 min | Negative | Excluded |
| Sign language recognition | 4+ hours | Medium | Excluded |

**Why voice output is excluded:** The agent's responses are rich visual UI — animated EMI cards, stacked deal breakdowns, payment buttons, WhatsApp links. Audio output makes judges listen instead of look, hiding the most impressive part of the demo. ElevenLabs also adds 500ms–2s latency on top of Bedrock, is another API dependency that can fail at the venue, and browser speechSynthesis sounds robotic. Voice input wows; voice output adds risk for zero additional wow.
