"""
Seed script — populates MongoDB with all demo data.

Run:
    cd backend
    python -m db.seed

Idempotent: uses upsert so it's safe to run multiple times.
Collections: products, accessories, customer_profiles, conversions, daily_summaries, weekly_stats
"""

import asyncio
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

PRODUCTS = [
    {
        "_id": "MBP-16-2024",
        "id": "MBP-16-2024",
        "name": 'Apple MacBook Pro 16" (M4 Pro)',
        "subtitle": '16.2" Liquid Retina XDR · Apple M4 Pro · 24GB RAM · 512GB SSD',
        "price_paisa": 24990000,
        "price_display": "₹2,49,900",
        "original_price_display": "₹2,79,900",
        "discount_display": "11% off",
        "category": "laptops",
        "brand": "Apple",
        "in_stock": True,
        "rating": 4.9,
        "review_count": 3847,
        "tags": ["DEMO PRODUCT", "IN STOCK"],
        "emi_from": "₹11,661",
        "emi_daily": "₹389",
        "specs_text": "Apple M4 Pro, 24GB unified memory, 512GB SSD, 16.2\" Liquid Retina XDR",
        "specs": [
            {"label": "Display", "value": '16.2" Liquid Retina XDR, 120Hz ProMotion, 1000 nits'},
            {"label": "Chip", "value": "Apple M4 Pro — 14-core CPU, 20-core GPU"},
            {"label": "RAM", "value": "24GB unified memory"},
            {"label": "Storage", "value": "512GB SSD"},
            {"label": "Battery", "value": "100Wh, up to 24 hrs"},
            {"label": "Ports", "value": "3x Thunderbolt 5, HDMI, SD, MagSafe 3"},
        ],
        "highlights": [
            "M4 Pro delivers 2x faster AI processing than M3 Pro",
            "Liquid Retina XDR — 1600 nits peak HDR, nano-texture option",
            "24GB unified memory — runs Xcode + simulator + browser without breaking a sweat",
            "MagSafe 3 + 3x Thunderbolt 5 — full connectivity, zero dongles needed",
        ],
    },
    {
        "_id": "DELL-XPS-15",
        "id": "DELL-XPS-15",
        "name": "Dell XPS 15 (2024)",
        "subtitle": '15.6" 3.5K OLED · Intel Core Ultra 7 · RTX 4060 · 32GB RAM',
        "price_paisa": 8999900,
        "price_display": "₹89,999",
        "original_price_display": "₹1,09,999",
        "discount_display": "18% off",
        "category": "laptops",
        "brand": "Dell",
        "in_stock": True,
        "rating": 4.7,
        "review_count": 2841,
        "tags": ["BESTSELLER", "IN STOCK"],
        "emi_from": "₹4,722",
        "emi_daily": "₹157",
        "specs_text": "Intel Core Ultra 7 185H, RTX 4060 8GB, 32GB LPDDR5X, 1TB SSD, 15.6\" 3.5K OLED",
        "specs": [
            {"label": "Display", "value": '15.6" 3.5K OLED, 120Hz, 100% DCI-P3'},
            {"label": "Processor", "value": "Intel Core Ultra 7 185H"},
            {"label": "Graphics", "value": "NVIDIA RTX 4060 8GB GDDR6"},
            {"label": "RAM", "value": "32GB LPDDR5X 6400MHz"},
            {"label": "Storage", "value": "1TB PCIe Gen 4 NVMe SSD"},
            {"label": "Battery", "value": "86Wh, MagSafe 130W Adapter"},
        ],
        "highlights": [
            "OLED display with 100% DCI-P3 color gamut — vibrant, true-to-life",
            "Dell AI Studio — on-device AI acceleration, privacy-first",
            "CNC machined aluminum chassis, just 1.86 kg",
            "Thunderbolt 4 x 2, USB-C, SD card reader",
        ],
    },
    {
        "_id": "SAMSUNG-S24",
        "id": "SAMSUNG-S24",
        "name": "Samsung Galaxy S24 Ultra",
        "subtitle": '6.8" QHD+ AMOLED · Snapdragon 8 Gen 3 · 12GB RAM · 256GB',
        "price_paisa": 12999900,
        "price_display": "₹1,29,999",
        "original_price_display": "₹1,54,999",
        "discount_display": "16% off",
        "category": "phones",
        "brand": "Samsung",
        "in_stock": True,
        "rating": 4.8,
        "review_count": 5123,
        "tags": ["HOT DEAL", "IN STOCK"],
        "emi_from": "₹6,111",
        "emi_daily": "₹204",
        "specs_text": "Snapdragon 8 Gen 3, 12GB LPDDR5X, 256GB UFS 4.0, 200MP camera, 6.8\" QHD+ AMOLED",
        "specs": [
            {"label": "Display", "value": '6.8" QHD+ AMOLED, 120Hz, 2600 nits'},
            {"label": "Processor", "value": "Snapdragon 8 Gen 3 for Galaxy"},
            {"label": "Camera", "value": "200MP + 50MP + 12MP + 10MP"},
            {"label": "RAM", "value": "12GB LPDDR5X"},
            {"label": "Storage", "value": "256GB UFS 4.0"},
            {"label": "Battery", "value": "5000mAh, 45W fast charge"},
        ],
        "highlights": [
            "Galaxy AI on-device — live translate, circle to search, edit suggestions",
            "200MP ProVisual Engine with optical 5x zoom",
            "Titanium frame, Corning Gorilla Armor 2",
            "IP68 water resistant, S Pen included",
        ],
    },
    {
        "_id": "LG-WASHER",
        "id": "LG-WASHER",
        "name": "LG WashTower (2024)",
        "subtitle": "24kg Washer · 16kg Dryer · AI Direct Drive · Inverter",
        "price_paisa": 4599900,
        "price_display": "₹45,999",
        "original_price_display": "₹59,999",
        "discount_display": "23% off",
        "category": "appliances",
        "brand": "LG",
        "in_stock": True,
        "rating": 4.5,
        "review_count": 1230,
        "tags": ["LIMITED OFFER", "IN STOCK"],
        "emi_from": "₹2,167",
        "emi_daily": "₹72",
        "specs_text": "AI Direct Drive, TurboWash 360, 5-star inverter, 44 dB noise level",
        "specs": [
            {"label": "Washer Capacity", "value": "24 kg Front Load"},
            {"label": "Dryer Capacity", "value": "16 kg Condenser Dryer"},
            {"label": "Technology", "value": "AI Direct Drive + TurboWash 360"},
            {"label": "Energy Rating", "value": "5 Star Inverter"},
            {"label": "Programs", "value": "14 wash programs"},
            {"label": "Noise", "value": "44 dB — whisper quiet"},
        ],
        "highlights": [
            "AI Direct Drive learns fabric type and adjusts wash motion",
            "TurboWash 360 — complete cycle in 39 minutes",
            "LG ThinQ app — start, monitor, diagnose remotely",
            "10-year motor warranty — industry leading",
        ],
    },
]

ACCESSORIES = [
    {
        "_id": "APPLE-MAGIC-MOUSE",
        "id": "APPLE-MAGIC-MOUSE",
        "product_id": "MBP-16-2024",
        "name": "Apple Magic Mouse (USB-C)",
        "price_paisa": 690000,
        "description": "Wireless, rechargeable via USB-C. Multi-Touch surface for gestures.",
    },
    {
        "_id": "APPLE-USB-HUB",
        "id": "APPLE-USB-HUB",
        "product_id": "MBP-16-2024",
        "name": "Apple USB-C Digital AV Multiport Adapter",
        "price_paisa": 490000,
        "description": "HDMI, USB-A, and USB-C passthrough charging in one adapter.",
    },
    {
        "_id": "DELL-SLEEVE",
        "id": "DELL-SLEEVE",
        "product_id": "DELL-XPS-15",
        "name": "Dell Premier Sleeve 15",
        "price_paisa": 299900,
        "description": "Premium neoprene sleeve with extra accessory pocket",
    },
    {
        "_id": "DELL-MOUSE",
        "id": "DELL-MOUSE",
        "product_id": "DELL-XPS-15",
        "name": "Dell Wireless Mouse WM326",
        "price_paisa": 199900,
        "description": "Ergonomic wireless mouse, 3-year battery life",
    },
    {
        "_id": "SAM-CASE",
        "id": "SAM-CASE",
        "product_id": "SAMSUNG-S24",
        "name": "Samsung Clear Case S24 Ultra",
        "price_paisa": 299900,
        "description": "Official Samsung clear case with S Pen slot",
    },
    {
        "_id": "SAM-BUDS",
        "id": "SAM-BUDS",
        "product_id": "SAMSUNG-S24",
        "name": "Samsung Galaxy Buds3 Pro",
        "price_paisa": 1499900,
        "description": "360 audio, ANC, seamless Galaxy ecosystem integration",
    },
    {
        "_id": "LG-STAND",
        "id": "LG-STAND",
        "product_id": "LG-WASHER",
        "name": "LG Pedestal Stand WDP4V",
        "price_paisa": 499900,
        "description": "Raises washer to ergonomic height, adds storage drawer",
    },
]

CUSTOMER_PROFILES = [
    {
        "_id": "CUST-RAHUL-001",
        "customer_id": "CUST-RAHUL-001",
        "name": "Rahul Sharma",
        "phone": "9876543210",
        "email": "rahul.sharma@gmail.com",
        "city": "Mumbai",
        "preferred_language": "hi",
        "cards_on_file": [
            {
                "bank": "HDFC Bank",
                "card_type": "credit",
                "last_four": "4242",
                "is_emi_eligible": True,
                "eligible_tenures": [3, 6, 9, 12, 18, 24],
            }
        ],
        "purchase_history": [
            {
                "order_id": "NL-2025-110234",
                "product": "Samsung Galaxy S23",
                "amount_paisa": 7499900,
                "emi_used": True,
                "emi_tenure_months": 12,
                "date": "2025-11-02",
            }
        ],
        "emi_preference": {
            "preferred_tenure": 18,
            "preferred_bank": "HDFC Bank",
        },
        "hesitation_history": [
            {
                "product_id": "DELL-XPS-15",
                "signal": "RETURN_VISIT",
                "first_seen": "2026-03-12T14:23:00Z",
            }
        ],
    }
]

RECENT_CONVERSIONS = [
    {
        "_id": "SAVE-065",
        "id": "SAVE-065",
        "timestamp": "2026-03-14T09:23:00Z",
        "product": "Dell XPS 15",
        "product_id": "DELL-XPS-15",
        "amount_paisa": 8499900,
        "amount_display": "₹84,999",
        "emi_scheme": {
            "bank": "HDFC Bank",
            "tenure_months": 18,
            "monthly_installment_paisa": 472217,
            "monthly_display": "₹4,722",
            "is_no_cost": True,
        },
        "offers_used": ["INST_DISC_5000"],
        "channel": "web",
        "signal": "EXIT_INTENT_DETECTED",
        "pine_labs_products": ["Affordability Suite", "Offer Engine", "Hosted Checkout"],
        "customer_city": "Mumbai",
    },
    {
        "_id": "SAVE-064",
        "id": "SAVE-064",
        "timestamp": "2026-03-14T09:01:00Z",
        "product": "Samsung Galaxy S24 Ultra",
        "product_id": "SAMSUNG-S24",
        "amount_paisa": 12499900,
        "amount_display": "₹1,24,999",
        "emi_scheme": {
            "bank": "ICICI Bank",
            "tenure_months": 12,
            "monthly_installment_paisa": 1139900,
            "monthly_display": "₹11,399",
            "is_no_cost": False,
        },
        "offers_used": ["CASHBACK_5PCT_HDFC"],
        "channel": "whatsapp",
        "signal": "CART_STALL_DETECTED",
        "pine_labs_products": ["Affordability Suite", "Offer Engine", "Payment Links"],
        "customer_city": "Bengaluru",
    },
    {
        "_id": "SAVE-063",
        "id": "SAVE-063",
        "timestamp": "2026-03-14T08:47:00Z",
        "product": "LG WashTower (2024)",
        "product_id": "LG-WASHER",
        "amount_paisa": 4599900,
        "amount_display": "₹45,999",
        "emi_scheme": {
            "bank": "SBI Card",
            "tenure_months": 9,
            "monthly_installment_paisa": 511100,
            "monthly_display": "₹5,111",
            "is_no_cost": True,
        },
        "offers_used": [],
        "channel": "qr",
        "signal": "CHECKOUT_DROP_DETECTED",
        "pine_labs_products": ["Affordability Suite", "UPI QR Code"],
        "customer_city": "Delhi",
    },
    {
        "_id": "SAVE-062",
        "id": "SAVE-062",
        "timestamp": "2026-03-14T08:12:00Z",
        "product": "Dell XPS 15",
        "product_id": "DELL-XPS-15",
        "amount_paisa": 8499900,
        "amount_display": "₹84,999",
        "emi_scheme": {
            "bank": "AXIO (Cardless)",
            "tenure_months": 9,
            "monthly_installment_paisa": 1054400,
            "monthly_display": "₹10,544",
            "is_no_cost": False,
        },
        "offers_used": ["INST_DISC_5000"],
        "channel": "web",
        "signal": "RETURN_VISIT_DETECTED",
        "pine_labs_products": ["Affordability Suite", "Offer Engine", "Hosted Checkout"],
        "customer_city": "Hyderabad",
    },
    {
        "_id": "SAVE-061",
        "id": "SAVE-061",
        "timestamp": "2026-03-13T21:34:00Z",
        "product": "Samsung Galaxy S24 Ultra",
        "product_id": "SAMSUNG-S24",
        "amount_paisa": 12999900,
        "amount_display": "₹1,29,999",
        "emi_scheme": {
            "bank": "HDFC Bank",
            "tenure_months": 24,
            "monthly_installment_paisa": 541663,
            "monthly_display": "₹5,417",
            "is_no_cost": True,
        },
        "offers_used": ["CASHBACK_5PCT_HDFC", "INST_DISC_5000"],
        "channel": "whatsapp",
        "signal": "EXIT_INTENT_DETECTED",
        "pine_labs_products": ["Affordability Suite", "Offer Engine", "Payment Links"],
        "customer_city": "Chennai",
    },
    {
        "_id": "SAVE-060",
        "id": "SAVE-060",
        "timestamp": "2026-03-13T20:11:00Z",
        "product": "Dell XPS 15",
        "product_id": "DELL-XPS-15",
        "amount_paisa": 8499900,
        "amount_display": "₹84,999",
        "emi_scheme": {
            "bank": "HDFC Bank",
            "tenure_months": 18,
            "monthly_installment_paisa": 472217,
            "monthly_display": "₹4,722",
            "is_no_cost": True,
        },
        "offers_used": ["INST_DISC_5000"],
        "channel": "voice",
        "signal": "IDLE_DETECTED",
        "pine_labs_products": ["Affordability Suite", "Offer Engine", "Hosted Checkout"],
        "customer_city": "Pune",
    },
    {
        "_id": "SAVE-059",
        "id": "SAVE-059",
        "timestamp": "2026-03-13T19:02:00Z",
        "product": "LG WashTower (2024)",
        "product_id": "LG-WASHER",
        "amount_paisa": 4599900,
        "amount_display": "₹45,999",
        "emi_scheme": {
            "bank": "Home Credit (Cardless)",
            "tenure_months": 12,
            "monthly_installment_paisa": 429500,
            "monthly_display": "₹4,295",
            "is_no_cost": False,
        },
        "offers_used": [],
        "channel": "qr",
        "signal": "CART_STALL_DETECTED",
        "pine_labs_products": ["Affordability Suite", "UPI QR Code"],
        "customer_city": "Kolkata",
    },
    {
        "_id": "SAVE-058",
        "id": "SAVE-058",
        "timestamp": "2026-03-13T17:45:00Z",
        "product": "Samsung Galaxy S24 Ultra",
        "product_id": "SAMSUNG-S24",
        "amount_paisa": 11999900,
        "amount_display": "₹1,19,999",
        "emi_scheme": {
            "bank": "SBI Card",
            "tenure_months": 9,
            "monthly_installment_paisa": 1333322,
            "monthly_display": "₹13,333",
            "is_no_cost": True,
        },
        "offers_used": ["BRAND_SUBVENTION_DELL"],
        "channel": "web",
        "signal": "PRICE_COPY_DETECTED",
        "pine_labs_products": ["Affordability Suite", "Offer Engine", "Hosted Checkout"],
        "customer_city": "Ahmedabad",
    },
    {
        "_id": "SAVE-057",
        "id": "SAVE-057",
        "timestamp": "2026-03-13T16:22:00Z",
        "product": "Dell XPS 15",
        "product_id": "DELL-XPS-15",
        "amount_paisa": 8499900,
        "amount_display": "₹84,999",
        "emi_scheme": {
            "bank": "HDFC Bank",
            "tenure_months": 6,
            "monthly_installment_paisa": 1416650,
            "monthly_display": "₹14,167",
            "is_no_cost": True,
        },
        "offers_used": ["INST_DISC_5000", "CASHBACK_5PCT_HDFC"],
        "channel": "web",
        "signal": "EMI_DWELL_DETECTED",
        "pine_labs_products": ["Affordability Suite", "Offer Engine", "Hosted Checkout"],
        "customer_city": "Mumbai",
    },
    {
        "_id": "SAVE-056",
        "id": "SAVE-056",
        "timestamp": "2026-03-13T14:09:00Z",
        "product": "LG WashTower (2024)",
        "product_id": "LG-WASHER",
        "amount_paisa": 4599900,
        "amount_display": "₹45,999",
        "emi_scheme": {
            "bank": "HDFC Bank",
            "tenure_months": 12,
            "monthly_installment_paisa": 383325,
            "monthly_display": "₹3,833",
            "is_no_cost": True,
        },
        "offers_used": [],
        "channel": "voice",
        "signal": "EXIT_INTENT_DETECTED",
        "pine_labs_products": ["Affordability Suite", "Hosted Checkout"],
        "customer_city": "Jaipur",
    },
]

DAILY_SUMMARIES = [
    {"_id": "2026-03-08", "date": "2026-03-08", "saves": 7, "gmv_recovered_paisa": 17500000, "gmv_recovered_display": "₹1,75,000", "top_signal": "CART_STALL"},
    {"_id": "2026-03-09", "date": "2026-03-09", "saves": 9, "gmv_recovered_paisa": 21000000, "gmv_recovered_display": "₹2,10,000", "top_signal": "EXIT_INTENT"},
    {"_id": "2026-03-10", "date": "2026-03-10", "saves": 8, "gmv_recovered_paisa": 18500000, "gmv_recovered_display": "₹1,85,000", "top_signal": "EXIT_INTENT"},
    {"_id": "2026-03-11", "date": "2026-03-11", "saves": 11, "gmv_recovered_paisa": 26000000, "gmv_recovered_display": "₹2,60,000", "top_signal": "RETURN_VISIT"},
    {"_id": "2026-03-12", "date": "2026-03-12", "saves": 12, "gmv_recovered_paisa": 28500000, "gmv_recovered_display": "₹2,85,000", "top_signal": "EXIT_INTENT"},
    {"_id": "2026-03-13", "date": "2026-03-13", "saves": 10, "gmv_recovered_paisa": 22500000, "gmv_recovered_display": "₹2,25,000", "top_signal": "CHECKOUT_DROP"},
    {"_id": "2026-03-14", "date": "2026-03-14", "saves": 8, "gmv_recovered_paisa": 19000000, "gmv_recovered_display": "₹1,90,000", "top_signal": "EXIT_INTENT"},
]

WEEKLY_STATS = {
    "_id": "week-2026-03-08",
    "week": "2026-03-08",
    "saves": 65,
    "gmv_recovered_paisa": 142000000,
    "gmv_recovered_display": "₹14,20,000",
    "avg_emi_tenure_months": 14.3,
    "top_product": "Dell XPS 15",
    "top_pine_labs_product": "Affordability Suite",
    "channel_breakdown": {"web": 33, "whatsapp": 16, "qr": 10, "voice": 6},
}


async def seed() -> None:
    from motor.motor_asyncio import AsyncIOMotorClient

    uri = os.getenv("MONGODB_URI")
    if not uri:
        print("ERROR: MONGODB_URI not set")
        sys.exit(1)

    db_name = os.getenv("MONGODB_DB", "neverlose")
    client = AsyncIOMotorClient(uri, serverSelectionTimeoutMS=10000)
    db = client[db_name]

    try:
        await client.admin.command("ping")
        print(f"Connected to MongoDB: {db_name}")
    except Exception as exc:
        print(f"ERROR: Cannot connect to MongoDB: {exc}")
        sys.exit(1)

    async def upsert_all(collection_name: str, docs: list, id_field: str = "_id") -> None:
        col = db[collection_name]
        for doc in docs:
            await col.replace_one({"_id": doc["_id"]}, doc, upsert=True)
        print(f"  {collection_name}: {len(docs)} documents upserted")

    print("Seeding products...")
    await upsert_all("products", PRODUCTS)

    print("Seeding accessories...")
    await upsert_all("accessories", ACCESSORIES)

    print("Seeding customer profiles...")
    await upsert_all("customer_profiles", CUSTOMER_PROFILES)

    print("Seeding conversions...")
    await upsert_all("conversions", RECENT_CONVERSIONS)

    print("Seeding daily summaries...")
    await upsert_all("daily_summaries", DAILY_SUMMARIES)

    print("Seeding weekly stats...")
    col = db["weekly_stats"]
    await col.replace_one({"_id": WEEKLY_STATS["_id"]}, WEEKLY_STATS, upsert=True)
    print("  weekly_stats: 1 document upserted")

    await db["products"].create_index([("name", "text"), ("specs_text", "text"), ("brand", "text")])
    await db["products"].create_index("category")
    await db["products"].create_index("price_paisa")
    await db["accessories"].create_index("product_id")
    await db["conversions"].create_index([("timestamp", -1)])
    await db["customer_profiles"].create_index("phone")
    print("Indexes created")

    client.close()
    print("Seed complete.")


if __name__ == "__main__":
    asyncio.run(seed())
