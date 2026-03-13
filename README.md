# NeverLose

### The AI Agent That Converts Every Hesitant Buyer Into a Paying Customer

AI-powered cart abandonment recovery agent for Pine Labs merchants. Detects buyer hesitation in real-time and proactively presents stacked affordability deals (EMI + offers combined) before the customer leaves.

**Core concept:** Bring Pine Labs' full affordability stack (EMI Calculator, Offer Engine, Payment Links) forward to the moment of hesitation — not after cart abandonment.

---

## How It Works

### Hesitation Detection — Every Signal, Not Just One

NeverLose monitors a full spectrum of buyer hesitation signals and triggers the agent before the customer leaves:

| Signal | Trigger | What the agent does |
|--------|---------|---------------------|
| **Exit intent** | Cursor moves toward close/back button | Opens proactively with stacked deal + daily cost |
| **Idle time** | No scroll/click for 15+ seconds on product page | Gentle nudge: "Still thinking? Here's what others did" |
| **Scroll bounce** | Fast upward scroll (mobile) | Same as exit intent — agent slides in from corner |
| **Cart stall** | Item in cart, no checkout action for 60s | "Your cart is waiting — here's the EMI breakdown" |
| **Checkout drop** | Reached payment page, no action for 30s | Cardless EMI pivot or offer reveal at the critical moment |
| **Return visit** | Same product viewed 2+ times in session | "Back again? Here's a deal we've saved for you" |
| **Price copy** | Customer copies the price text (clipboard event) | "Comparing prices? We can make this ₹4,722/month" |
| **Wishlist add** | Product added to wishlist instead of cart | "Great taste — want to lock this in now with No-Cost EMI?" |
| **Verbal hesitation** | Customer types/says "too expensive", "mehenga", "can't afford" | Immediate stacked deal response in their language |
| **Long EMI page dwell** | 10+ seconds on EMI section without action | Tenure slider opens automatically |

### The Full Flow

1. **Detects hesitation** — monitors all cart signals above (idle time, exit intent, scroll behavior, cart stall, return visits)
2. **Stacks the best deal** — chains EMI Calculator v3 + Offer Engine in real-time; brand discounts and cashback applied before EMI is computed on the net price
3. **Presents in real-time** — surfaces "₹4,722/month (₹157/day)" before the customer bounces, with social proof and an interactive tenure slider
4. **Closes the sale** — customer chooses their channel: web checkout, WhatsApp payment link, or UPI QR code scanned directly in chat
5. **Smart upsell** — after EMI confirmed, suggests one complementary accessory as incremental monthly cost ("Add the sleeve for ₹167/month more")

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
├── Payment Agent (Sonnet 4.6)  — order creation, checkout, payment links, QR codes
├── Upsell Agent (Haiku 4.5)    — accessory recommendations, AOV optimization
└── Support Agent (Haiku 4.5)   — order tracking, refunds
```

Agents communicate via Bedrock's multi-agent orchestration. The Supervisor routes based on intent detected in each message.

---

## Pine Labs Integration

9 Pine Labs products used via the Pine Labs MCP Server:

| Product | Role |
|---------|------|
| EMI Calculator v3 | Card EMI, debit EMI, cardless EMI, brand EMI |
| Offer Engine | Instant discounts, cashback, brand subvention |
| Payment Gateway | Order creation |
| Infinity Checkout | Hosted checkout URL (one API call) |
| Payment Links | Shareable links for WhatsApp / SMS |
| UPI QR Code | Scannable in-chat QR — GPay, PhonePe, Paytm |
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
| `find_accessories` | Find complementary accessories for smart upsell / AOV optimization |
| `create_checkout` | Create Pine Labs order + Infinity Checkout URL |
| `generate_payment_link` | Payment Link for WhatsApp / SMS delivery |
| `generate_qr_code` | UPI QR code for in-chat payment (GPay / PhonePe / Paytm) |
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

## Multilingual Support

NeverLose works in 10+ Indian languages — because price shock doesn't speak only English.

India has 900M+ internet users. Only ~125M are comfortable in English. An EMI agent that only works in English misses 85% of the market.

Claude handles all Indian languages natively — no translation layer, no extra API, zero marginal cost. The agent detects the customer's language and responds in kind.

**Supported:** Hindi, Tamil, Telugu, Kannada, Malayalam, Bengali, Marathi, Gujarati, Punjabi, Odia, English.

**Demo:** Customer says _"yeh laptop bahut mehenga hai, koi EMI option hai kya?"_ → NeverLose responds in Hindi with the stacked EMI + offer breakdown.

---

## Voice Input

Powered by the browser's Web Speech API — no backend changes required.

The customer speaks; the transcript goes through the same agent pipeline as typed text. Language is auto-detected or set from the browser locale (`hi-IN`, `ta-IN`, etc.).

**Demo moment:** Speak into your phone mic in Hindi → NeverLose responds in Hindi with EMI options.

---

## Key Design Decisions

- **Offer stacking is the differentiator** — always call `discover_offers` before showing EMI; combine into a single stacked deal message
- **Lead with monthly payment, not total price** — "₹4,722/month" not "₹84,999 with EMI"
- **Daily cost reframing** — always append daily equivalent: "₹157/day — less than your Swiggy order"
- **Exit intent is the trigger** — agent opens proactively on cursor exit or mobile scroll-up; no customer action needed
- **Social proof on first touch** — "47 customers bought this on EMI today" injected once per conversation
- **Smart upsell** — one accessory suggested, only if its incremental EMI is <10% of base ("Add the sleeve for ₹167/month more")
- **Three payment channels** — web checkout, WhatsApp link, UPI QR in chat; customer picks
- **EMI tenure slider** — interactive component in chat; drag tenure, watch monthly/daily cost update live
- **Cardless EMI pivot** — when no eligible card, pivot to AXIO / Home Credit / SBI cardless (PAN + phone only)
- **All amounts in paisa** internally (Pine Labs API format); formatted as ₹X,XX,XXX for display
- **Multilingual by default** — agent mirrors the customer's language; no translation layer needed
- **Voice input via Web Speech API** — zero backend changes; transcript feeds the same agent pipeline
- **Fallback chain:** Bedrock CRIS → Anthropic direct API → mock responses
