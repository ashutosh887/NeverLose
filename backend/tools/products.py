"""
Tools: search_products, find_accessories
Loads from mock/products.json and mock/accessories.json.

No live Pine Labs API for products — merchant catalog is local.
In production this would query the merchant's product catalogue API.

UPSELL RULE (enforced here):
  find_accessories returns only ONE accessory.
  The caller (Upsell Agent) must verify: accessory EMI < 10% of base product EMI.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional

MOCK_DIR = Path(__file__).parent.parent / "mock"


def _load_products() -> List[Dict]:
    return json.loads((MOCK_DIR / "products.json").read_text())["products"]


def _load_accessories() -> dict:
    return json.loads((MOCK_DIR / "accessories.json").read_text())["accessories"]


async def search_products(
    query: Optional[str] = None,
    category: Optional[str] = None,
    max_price_paisa: Optional[int] = None,
) -> dict:
    """
    Search merchant product catalog.

    Args:
        query:           Free-text search (matches name, specs, brand).
        category:        Filter by category: "laptops", "phones", "appliances".
        max_price_paisa: Filter by max price in paisa.

    Returns dict with products list.
    """
    products = _load_products()

    if category:
        products = [p for p in products if p["category"] == category]

    if max_price_paisa is not None:
        products = [p for p in products if p["price_paisa"] <= max_price_paisa]

    if query:
        q = query.lower()
        products = [
            p for p in products
            if q in p["name"].lower()
            or q in p.get("brand", "").lower()
            or q in p.get("specs", "").lower()
            or q in p.get("category", "").lower()
        ]

    return {
        "response_code": 1,
        "response_message": "SUCCESS",
        "products": products,
        "count": len(products),
    }


async def get_product(product_id: str) -> Optional[dict]:
    """Get a single product by ID."""
    products = _load_products()
    for p in products:
        if p["id"] == product_id:
            return p
    return None


async def find_accessories(product_id: str) -> dict:
    """
    Find ONE best accessory for a product.

    UPSELL RULE: Returns cheapest accessory so Upsell Agent can verify
    it meets the <10% incremental EMI threshold.

    Args:
        product_id: Product identifier (e.g. "DELL-XPS-15").

    Returns dict with ONE accessory (cheapest for the product).
    """
    accessories = _load_accessories()
    product_accessories = accessories.get(product_id, [])

    if not product_accessories:
        return {
            "response_code": 0,
            "response_message": "No accessories found",
            "accessory": None,
        }

    # Pick cheapest to maximise chance of passing the <10% incremental EMI rule
    best = min(product_accessories, key=lambda a: a["price_paisa"])

    return {
        "response_code": 1,
        "response_message": "SUCCESS",
        "accessory": best,
    }
