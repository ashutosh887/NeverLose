# NeverLose

### The AI Agent That Converts Every Hesitant Buyer Into a Paying Customer

AI-powered cart abandonment recovery agent for Pine Labs merchants. Detects buyer hesitation in real-time and proactively presents stacked affordability deals (EMI + offers combined) before the customer leaves.

**Core concept:** Bring Pine Labs' full affordability stack (Affordability Suite, Offer Engine, Hosted Checkout) forward to the moment of hesitation — not after cart abandonment.

---

## How It Works

### Hesitation Detection — Every Signal, Not Just One

NeverLose monitors a full spectrum of buyer hesitation signals:

| Signal | Trigger | What the agent does |
|--------|---------|---------------------|
| **Exit intent** | Cursor moves toward close/back button | Opens proactively with stacked deal + daily cost |
| **Price shock prediction** | 25s dwell on page OR 3+ hovers near price zone | Intervenes before hesitation is even expressed |
| **Idle time** | No scroll/click for 15+ seconds | Gentle nudge: "Still thinking? Here's what others did" |
| **Scroll bounce** | Fast upward scroll (mobile) | Agent slides in from corner |
| **Cart stall** | Item in cart, no checkout action for 60s | "Your cart is waiting — here's the EMI breakdown" |
| **Checkout drop** | Reached payment page, no action for 30s | Cardless EMI pivot or offer reveal |
| **Return visit** | Same product viewed 2+ times in session | "Back again? Here's a deal we've saved for you" |
| **Price copy** | Customer copies the price text (clipboard) | "Comparing prices? We have exclusive Pine Labs offers" |
| **Wishlist add** | Product added to wishlist instead of cart | "Lock it in today with No-Cost EMI" |
| **Verbal hesitation** | Types "too expensive", "mehenga", "can't afford" | Immediate stacked deal in their language |
| **Long EMI dwell** | 10+ seconds on EMI section | Tenure slider opens automatically |

### Smart Features

**Negotiation Mode** — When customer asks "can you reduce the price?" or "kuch discount milega?", the agent never refuses. Instead: "I can't touch the MRP, but I found ₹7,000 in bank + brand offers you won't find elsewhere."

**Smart Timing Engine** — Agent tone adjusts based on time of day:
- Night (0–6am): Longest EMI tenure, calm tone
- Morning: Crisp daily cost number, quick CTA
- Evening: Instant cashback + mild urgency

**Customer Affordability Profile** — Agent loads purchase history, preferred tenure, card on file, and prior hesitation data. Instead of generic: "Based on your previous purchase, customers like you chose 12 months."

### The Full Flow

1. **Detects hesitation** — monitors all signals above; `PRICE_SHOCK_PREDICTED` fires before the customer even types anything
2. **Stacks the best deal** — chains Affordability Suite + Offer Engine in real-time; brand discounts and cashback applied before EMI is computed on the net price
3. **Presents in real-time** — surfaces "₹4,722/month (₹157/day)" with social proof and an interactive tenure slider
4. **Negotiates if needed** — handles "can you reduce price?" with offers instead of apologies
5. **Closes the sale** — customer chooses their channel: web checkout, WhatsApp payment link, or UPI QR code scanned directly in chat
6. **Confetti on success** — payment confirmation with animated confetti burst
7. **Smart upsell** — after EMI confirmed, suggests one complementary accessory ("Add the sleeve for ₹167/month more")

---

## Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js + Tailwind + Framer Motion (`:3000`) |
| Backend | Python FastAPI (`:8000`) |
| Real-time | WebSocket (chat) + SSE (dashboard) |
| LLM | Claude Sonnet 4.6 via AWS Bedrock CRIS (`us.anthropic.claude-sonnet-4-6`) |

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

---

## Pine Labs Integration

| Product | Role |
|---------|------|
| Affordability Suite | Card EMI, debit EMI, cardless EMI, brand EMI (replaces legacy EMI Calculator) |
| Offer Engine | Instant discounts, cashback, brand subvention |
| Hosted Checkout | Single-call checkout with all payment methods — `POST /api/checkout/v1/orders` |
| Payment Links | Shareable links for WhatsApp / SMS |
| UPI QR Code | Scannable in-chat QR — GPay, PhonePe, Paytm |
| Customers API | Customer profile for personalization (preferred tenure, card, history) |
| Convenience Fee API | Cost comparison across payment methods |

### Hosted Checkout Flow (new)

```
Bearer token → POST /api/checkout/v1/orders
  body: { merchant_order_reference, order_amount, allowed_payment_methods: [CREDIT_EMI, DEBIT_EMI, CARD, UPI, ...], callback_url }
  response: { token, order_id, redirect_url }
```

`redirect_url` opens Pine Labs' Infinity Checkout page — customer selects bank, tenure, and pays.

### Affordability Suite (EMI discovery)

```
Bearer token → POST /api/affordability/v1/offer/discovery
  body: { merchant_id, order_amount: { value, currency } }
  response: offers[] with bank, tenure, rate, monthly_installment
```

---

## Agent Tools

| Tool | Purpose |
|------|---------|
| `check_emi_options` | Affordability Suite — all schemes with tenure, rate, savings |
| `discover_offers` | Offer Engine — stackable discounts / cashback |
| `calculate_stacked_deal` | Combine best EMI + offers into a single deal |
| `search_products` | Merchant product catalog search |
| `find_accessories` | Find complementary accessories for smart upsell / AOV optimization |
| `create_checkout` | Hosted Checkout — single API call returns redirect_url |
| `generate_payment_link` | Payment Link for WhatsApp / SMS delivery |
| `generate_qr_code` | UPI QR code for in-chat payment (GPay / PhonePe / Paytm) |
| `check_payment_status` | Poll order status |
| `get_order_details` | Full order info for support flows |
| `calculate_convenience_fee` | Compare fees across payment methods |

---

## Setup

```bash
cd backend
cp .env.example .env   # Fill in credentials
```

Required environment variables:

```
# Pine Labs Plural API (all endpoints) — auth via Bearer token
PINE_LABS_PLURAL_URL=https://pluraluat.v2.pinepg.in
PINE_LABS_MERCHANT_ID=111077
PINE_LABS_CLIENT_ID=<from Pine Labs dashboard>
PINE_LABS_CLIENT_SECRET=<from Pine Labs dashboard>

# AWS Bedrock (us-east-1 Workshop Studio)
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_SESSION_TOKEN=   # required for Workshop Studio STS credentials
AWS_REGION=us-east-1

# Bedrock model IDs — us-east-1 CRIS (us. prefix)
BEDROCK_SUPERVISOR_MODEL=us.anthropic.claude-sonnet-4-6
BEDROCK_SUB_AGENT_MODEL=us.anthropic.claude-haiku-4-5-20251001-v1:0

ANTHROPIC_API_KEY=      # fallback if Bedrock unavailable
USE_MOCK=false          # true = use mock data layer (safe for offline demo)
PAYMENT_CALLBACK_URL=http://localhost:3000/payment-complete
```

---

## Running Locally

**Backend**
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload   # http://localhost:8000
```

**Frontend**
```bash
cd frontend
npm install
npm run dev   # http://localhost:3000
```

**Tests**
```bash
cd backend
pytest tests/ -v
pytest tests/ -k "test_emi_calculator"
```

**Demo reset** — Press `Ctrl+Shift+R` in the chat widget to clear conversation and restart.

---

## Safety

Policy rules enforced before tool execution (`middleware/policy.py`):

- Cannot create orders above ₹2,00,000
- Cannot process payment without explicit `user_confirmed=true`
- Refunds above ₹50,000 require supervisor escalation

---

## Multilingual Support

Claude handles all Indian languages natively — no translation layer, no extra API, zero marginal cost.

**Supported:** Hindi, Tamil, Telugu, Kannada, Malayalam, Bengali, Marathi, Gujarati, Punjabi, Odia, English.

**Demo:** Customer says _"yeh laptop bahut mehenga hai, koi EMI option hai kya?"_ → NeverLose responds in Hindi with the stacked EMI + offer breakdown.

---

## Voice Input

Powered by the browser's Web Speech API — no backend changes required.

The customer speaks; the transcript goes through the same agent pipeline as typed text. Language is auto-detected from the browser locale (`hi-IN`, `ta-IN`, etc.).

---

## Key Design Decisions

- **Price Shock Prediction** — don't wait for exit intent; intervene after 25s dwell or 3+ price hovers
- **Negotiation Mode** — agent never says "I can't change the price"; always responds with stacked offers
- **Smart Timing Engine** — tone adjusts by time of day (night → longest EMI, evening → cashback urgency)
- **Customer Affordability Profile** — purchase history, preferred tenure, and card loaded at session start
- **Offer stacking is the differentiator** — always call `discover_offers` before showing EMI; combine into single stacked deal
- **Lead with monthly payment, not total price** — "₹4,722/month" not "₹84,999 with EMI"
- **Daily cost reframing** — "₹157/day — less than your Swiggy order"
- **Social proof on first touch** — "47 customers bought this on EMI today" injected once per conversation
- **Three payment channels** — web checkout (Hosted Checkout), WhatsApp link (Payment Links), UPI QR in chat
- **Confetti on payment success** — Framer Motion particle burst; no extra package required
- **Cardless EMI pivot** — when no eligible card, pivot to AXIO / Home Credit (PAN + phone only)
- **All amounts in paisa** internally; formatted as ₹X,XX,XXX for display
- **Fallback chain:** Bedrock CRIS → Anthropic direct API → mock responses (never fail the demo)
