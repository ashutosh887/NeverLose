# NeverLose

### The AI Agent That Converts Every Hesitant Buyer Into a Paying Customer

AI-powered cart abandonment recovery agent for Pine Labs merchants. Detects buyer hesitation in real-time and proactively presents stacked affordability deals (EMI + offers combined) before the customer leaves. Includes a two-sided platform: customer-facing sales agent + merchant intelligence copilot.

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

### The Full Conversion Flow

1. **Detects hesitation** — monitors all signals above; `PRICE_SHOCK_PREDICTED` fires before the customer even types anything
2. **Stacks the best deal** — chains Affordability Suite + Offer Engine; brand discounts and cashback applied before EMI is computed on the net price
3. **Presents in real-time** — "₹4,722/month (₹157/day)" with social proof and an interactive tenure slider
4. **Negotiates in 3 escalating levels** — handles pushback progressively, never refuses, ends with urgency countdown
5. **Closes the sale** — customer picks their channel: web checkout, WhatsApp payment link, or UPI QR scanned directly in chat
6. **Confetti on success** — payment confirmation with animated particle burst + ka-ching sound
7. **Smart upsell** — after EMI confirmed, suggests one complementary accessory ("Add the sleeve for ₹167/month more")
8. **Post-purchase lifecycle** — delivery date, first EMI due date, bank name, reminder note — all in one follow-up card

---

## Demo Highlights

### Real-time Negotiation — 3 Escalating Levels

The most agentic behavior in the entire product. The agent doesn't just show options — it bargains.

**Level 1** — Customer asks for better price:
> "I can't touch the MRP, but I found ₹7,000 in exclusive Pine Labs bank + brand offers."

**Level 2** — Customer pushes back:
> "Let me check with my manager... 🤔"
> *[2-second pause]*
> "OK — I pulled some strings. Here's the fully stacked deal: HDFC cashback + Samsung subvention + 24-month No-Cost EMI = ₹3,458/month."

**Level 3** — Customer pushes back again:
> "This is the absolute best I can do. I'm holding this rate for 10 minutes."
> *[⏰ countdown timer appears: 9:59... 9:58...]*

If the customer still declines, the agent generates a 7-day payment link:
> "Totally understand 😊 I've saved this deal for you — valid 7 days: [link]. Come back anytime!"

### Deal Expiry Countdown

When Level 3 negotiation triggers, a live countdown timer appears in chat:
- `⏰ Deal expires in 9:47` (amber)
- Turns orange at 5 minutes
- Turns red + pulses at 1 minute
- Creates real FOMO — judges watching the demo feel the urgency themselves

### Post-Purchase Follow-up

After payment success, the agent doesn't disappear. It sends a lifecycle card:

```
✅ Dell XPS 15 confirmed!
📦 Estimated delivery: Wednesday, Mar 18
💳 First EMI of ₹4,722 due April 15 on your HDFC card
🔔 I'll remind you 2 days before
```

This is lifecycle management, not a one-shot chatbot.

### Merchant Copilot — Two-Sided Platform

The dashboard has a second chat interface where the **merchant** talks to Priya:

> **Merchant:** "What's my best-selling EMI scheme today?"
> **Priya:** "HDFC 18-month No-Cost is driving 42% of conversions. Samsung S24 Ultra has the highest abandonment at 78% — want me to create a flash offer?"
> **Merchant:** "Yes, 5% extra off for the next 2 hours"
> **Priya:** "Done. I've pushed a 5% instant discount via Pine Labs Offer Engine — NeverLose will now show this to hesitating customers on Samsung S24 Ultra."

NeverLose is a **two-sided platform** — consumer agent + merchant copilot, both powered by the same infrastructure.

---

## Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js + Tailwind + Framer Motion (`:3000`) |
| Backend | Python FastAPI (`:8000`) |
| Real-time | WebSocket (chat + merchant copilot) + SSE (dashboard) |
| LLM | Claude Sonnet 4.6 via AWS Bedrock CRIS (`us.anthropic.claude-sonnet-4-6`) |
| Database | MongoDB Atlas — products, conversions, customer profiles |

---

## Agent Architecture

```
Supervisor Agent (Sonnet 4.6) — /ws/chat
├── Sales Agent (Haiku 4.5)     — hesitation detection, EMI + offer recommendations
├── Offer Agent (Haiku 4.5)     — offer stacking, deal calculation
├── Payment Agent (Sonnet 4.6)  — order creation, checkout, payment links, QR codes
├── Upsell Agent (Haiku 4.5)    — accessory recommendations, AOV optimization
└── Support Agent (Haiku 4.5)   — order tracking, refunds

Merchant Copilot (Sonnet 4.6) — /ws/merchant-chat
└── Analytics + offer creation for the merchant
```

---

## Pine Labs Integration

| Product | Role |
|---------|------|
| Affordability Suite | Card EMI, debit EMI, cardless EMI, brand EMI |
| Offer Engine | Instant discounts, cashback, brand subvention |
| Hosted Checkout | Single-call checkout — `POST /api/checkout/v1/orders` → `redirect_url` |
| Payment Links | Shareable links for WhatsApp / SMS (7-day save-for-later) |
| UPI QR Code | Scannable in-chat QR — GPay, PhonePe, Paytm |
| Customers API | Customer profile: preferred tenure, card on file, purchase history |
| Convenience Fee API | Cost comparison across payment methods |

---

## Agent Tools

| Tool | Purpose |
|------|---------|
| `check_emi_options` | Affordability Suite — all schemes with tenure, rate, savings |
| `discover_offers` | Offer Engine — stackable discounts / cashback |
| `calculate_stacked_deal` | Combine best EMI + offers into a single deal |
| `search_products` | Merchant product catalog search |
| `find_accessories` | Find complementary accessories for smart upsell / AOV optimization |
| `create_checkout` | Hosted Checkout — single API call returns `redirect_url` |
| `generate_payment_link` | Payment Link for WhatsApp / SMS (supports 7-day expiry for Save for Later) |
| `generate_qr_code` | UPI QR code for in-chat payment (GPay / PhonePe / Paytm) |
| `check_payment_status` | Poll order status |
| `get_order_details` | Full order info for support flows |
| `calculate_convenience_fee` | Compare fees across payment methods |

---

## Running Locally

### One-command start (recommended)

```bash
cp backend/.env.example backend/.env   # fill in credentials
./start.sh
```

`start.sh` automatically:
1. Seeds MongoDB from `backend/.env` (idempotent — safe to re-run)
2. Starts the FastAPI backend on `:8000`
3. Starts the Next.js frontend on `:3000`

Press `Ctrl+C` to stop both.

### Manual setup

**Backend**
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env             # fill in credentials
python -m db.seed                # seed MongoDB (idempotent)
uvicorn main:app --reload        # http://localhost:8000
```

**Frontend**
```bash
cd frontend
npm install
npm run dev                      # http://localhost:3000
```

**Tests**
```bash
cd backend
pytest tests/ -v
pytest tests/ -k "test_emi_calculator"
```

**Demo reset** — Press `Ctrl+Shift+R` in the chat widget to clear conversation and restart.

---

## Environment Variables

```bash
# Pine Labs Plural API
PINE_LABS_PLURAL_URL=https://pluraluat.v2.pinepg.in
PINE_LABS_MERCHANT_ID=111077
PINE_LABS_CLIENT_ID=<from Pine Labs dashboard>
PINE_LABS_CLIENT_SECRET=<from Pine Labs dashboard>

# AWS Bedrock (Workshop Studio — us-east-1)
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_SESSION_TOKEN=           # required for Workshop Studio STS credentials
AWS_REGION=us-east-1

# Bedrock model IDs (us-east-1 CRIS — us. prefix)
BEDROCK_SUPERVISOR_MODEL=us.anthropic.claude-sonnet-4-6
BEDROCK_SUB_AGENT_MODEL=us.anthropic.claude-haiku-4-5-20251001-v1:0

ANTHROPIC_API_KEY=           # fallback if Bedrock unavailable
USE_MOCK=false               # true = mock data layer (safe for offline demo)
PAYMENT_CALLBACK_URL=http://localhost:3000/payment-complete

# MongoDB Atlas
MONGODB_URI=mongodb+srv://<user>:<pass>@<cluster>.mongodb.net/?appName=NeverLose
MONGODB_DB=neverlose
```

> **Note:** For `ap-south-1` (production deployment), use `global.` prefix instead of `us.` in model IDs.

---

## Database

MongoDB Atlas — falls back to mock JSON if unavailable (demo never breaks).

| Collection | Contents |
|------------|----------|
| `products` | Product catalog — specs, highlights, EMI display from/daily |
| `accessories` | Accessories per product for smart upsell |
| `customer_profiles` | Customer affordability profiles (card, tenure preference, history) |
| `conversions` | Live + historical conversion events for dashboard |
| `daily_summaries` | Per-day GMV recovered and top signal |
| `weekly_stats` | 7-day aggregate for dashboard header |

**Health check** (`GET /health`) reports MongoDB and Pine Labs auth status in real-time.

---

## Safety

Policy rules enforced before every tool execution (`middleware/policy.py`):

- Cannot create orders above ₹2,00,000
- Cannot process payment without explicit `user_confirmed=true`
- Refunds above ₹50,000 require supervisor escalation

---

## Multilingual Support

Claude handles all Indian languages natively — no translation layer, no extra API, zero marginal cost.

**Supported:** Hindi, Tamil, Telugu, Kannada, Malayalam, Bengali, Marathi, Gujarati, Punjabi, Odia, English.

**Demo:** Customer says _"yeh laptop bahut mehenga hai, koi EMI option hai kya?"_ → NeverLose responds in Hindi with the full stacked EMI + offer breakdown.

---

## Voice Input

Powered by the browser's Web Speech API — no backend changes required.

The customer speaks; the transcript goes through the same agent pipeline as typed text. Language is auto-detected from browser locale (`hi-IN`, `ta-IN`, etc.).

---

## Key Design Decisions

- **3-level negotiation** — agent escalates progressively: standard options → manager-approved stacked deal → best-and-final with countdown urgency. Never refuses. Never says "I can't change the price."
- **Deal expiry countdown** — Level 3 negotiation shows a live 10-minute timer in chat. Pure psychology — FOMO is proven.
- **Post-purchase lifecycle** — agent doesn't disappear after payment. Delivery date, EMI due date, reminder — full lifecycle in one card.
- **Save for Later** — Level 3 decline generates a 7-day payment link. The deal follows the customer, not the session.
- **Two-sided platform** — consumer agent + merchant copilot. Same infra, different system prompt. Merchant can check performance, create flash offers, get recommendations — all in natural language.
- **Price Shock Prediction** — don't wait for exit intent; intervene after 25s dwell or 3+ price hovers
- **Offer stacking is the differentiator** — always call `discover_offers` before EMI; combine into single stacked deal
- **Lead with monthly payment, not total price** — "₹4,722/month" not "₹84,999 with EMI"
- **Daily cost reframing** — "₹157/day — less than your Swiggy order"
- **Smart Timing Engine** — tone adjusts by time of day (night → longest EMI, evening → cashback urgency)
- **Customer Affordability Profile** — purchase history, preferred tenure, card loaded at session start
- **Social proof on first touch** — "47 customers bought this on EMI today" injected once per conversation
- **Three payment channels** — web checkout (Hosted Checkout), WhatsApp link (Payment Links), UPI QR in chat
- **Cardless EMI pivot** — when no eligible card, pivot to AXIO / Home Credit (PAN + phone only)
- **All amounts in paisa** internally; formatted as ₹X,XX,XXX for display
- **Fallback chain:** Bedrock CRIS → Anthropic direct API → mock responses (never fail the demo)
- **Auto-seed** — `start.sh` seeds MongoDB automatically; no manual step required
