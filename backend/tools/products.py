import json
import os
from pathlib import Path
from typing import Dict, List, Optional

MOCK_DIR = Path(__file__).parent.parent / "mock"


def _load_products_json() -> List[Dict]:
    return json.loads((MOCK_DIR / "products.json").read_text())["products"]


def _load_accessories_json() -> dict:
    return json.loads((MOCK_DIR / "accessories.json").read_text())["accessories"]


async def search_products(
    query: Optional[str] = None,
    category: Optional[str] = None,
    max_price_paisa: Optional[int] = None,
) -> dict:
    from db.client import get_db
    db = get_db()

    if db is not None:
        filter_: Dict = {}
        if category:
            filter_["category"] = category
        if max_price_paisa is not None:
            filter_["price_paisa"] = {"$lte": max_price_paisa}
        if query:
            filter_["$text"] = {"$search": query}

        cursor = db["products"].find(filter_, {"_id": 0})
        products = await cursor.to_list(length=100)
    else:
        products = _load_products_json()
        if category:
            products = [p for p in products if p.get("category") == category]
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
    from db.client import get_db
    db = get_db()

    if db is not None:
        doc = await db["products"].find_one({"_id": product_id}, {"_id": 0})
        return doc

    for p in _load_products_json():
        if p["id"] == product_id:
            return p
    return None


async def find_accessories(product_id: str) -> dict:
    from db.client import get_db
    db = get_db()

    if db is not None:
        cursor = db["accessories"].find({"product_id": product_id}, {"_id": 0})
        product_accessories = await cursor.to_list(length=20)
    else:
        all_acc = _load_accessories_json()
        product_accessories = all_acc.get(product_id, [])

    if not product_accessories:
        return {
            "response_code": 0,
            "response_message": "No accessories found",
            "accessory": None,
        }

    best = min(product_accessories, key=lambda a: a["price_paisa"])

    return {
        "response_code": 1,
        "response_message": "SUCCESS",
        "accessory": best,
    }
