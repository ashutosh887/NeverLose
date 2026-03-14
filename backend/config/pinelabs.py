"""
Pine Labs API Configuration
============================

Two distinct API families:

  LEGACY (EMI Calculator v3)
  ─────────────────────────
  Base URL : PINE_LABS_LEGACY_URL  (UAT: https://uat.pinepg.in)
  Auth     : merchant_id + merchant_access_code in request body
  Endpoint : POST /api/v3/emi/calculator

  PLURAL (new REST API — Orders, Checkout, Offers, QR, Payment Links, etc.)
  ──────────────────────────────────────────────────────────────────────────
  Base URL : PINE_LABS_PLURAL_URL  (UAT: https://pluraluat.v2.pinepg.in)
  Auth     : OAuth2 client_credentials Bearer token
             POST /api/auth/v1/token → access_token (TTL ~60 min)
  Endpoints: see PineLabsConfig.Endpoints below

Production swap (UAT → Prod):
  PINE_LABS_LEGACY_URL → https://www.pinepg.in
  PINE_LABS_PLURAL_URL → https://api.pluralpay.in

Credentials are sourced from .env — never hardcode them here.
"""

import os
import uuid
from datetime import datetime, timezone
from typing import Optional


class PineLabsConfig:
    # ── Legacy API (EMI Calculator v3) ──────────────────────────────────────
    # UAT:  https://uat.pinepg.in
    # Prod: https://www.pinepg.in
    LEGACY_BASE_URL: str = os.getenv("PINE_LABS_LEGACY_URL", "https://uat.pinepg.in")
    MERCHANT_ID: str = os.getenv("PINE_LABS_MERCHANT_ID", "")
    ACCESS_CODE: str = os.getenv("PINE_LABS_ACCESS_CODE", "")

    # ── Plural API (Orders / Checkout / Offers / QR / Payment Links) ────────
    # UAT:  https://pluraluat.v2.pinepg.in
    # Prod: https://api.pluralpay.in
    PLURAL_BASE_URL: str = os.getenv("PINE_LABS_PLURAL_URL", "https://pluraluat.v2.pinepg.in")
    CLIENT_ID: str = os.getenv("PINE_LABS_CLIENT_ID", "")
    CLIENT_SECRET: str = os.getenv("PINE_LABS_CLIENT_SECRET", "")

    # ── HTTP timeouts ────────────────────────────────────────────────────────
    TIMEOUT_SECONDS: float = 30.0        # standard API calls
    AUTH_TIMEOUT_SECONDS: float = 15.0   # token endpoint (should be fast)
    STATUS_TIMEOUT_SECONDS: float = 15.0 # payment status polls

    # ── Token cache ──────────────────────────────────────────────────────────
    # Pine Labs tokens expire in ~60 min; refresh 5 min early to avoid edge cases.
    TOKEN_TTL_MINUTES: int = 55

    class Endpoints:
        """All Pine Labs API endpoint paths (relative, append to base URL)."""

        # Legacy (EMI Calculator v3 — requires merchant_access_code, unused if ACCESS_CODE empty)
        EMI_CALCULATOR = "/api/v3/emi/calculator"

        # Plural — Auth
        AUTH_TOKEN = "/api/auth/v1/token"

        # Plural — Hosted Checkout (single-call: creates order + returns redirect_url)
        # POST body: merchant_order_reference, order_amount, allowed_payment_methods,
        #            integration_mode, callback_url, purchase_details
        # Response:  token, order_id, redirect_url, response_code, response_message
        HOSTED_CHECKOUT = "/api/checkout/v1/orders"

        # Plural — Affordability Suite (EMI offer discovery, no merchant_access_code needed)
        # POST /api/affordability/v1/offer/discovery — card-based EMI offers
        # POST /api/affordability/v1/offer/discovery/cardless — AXIO/Home Credit etc.
        AFFORDABILITY_OFFER_DISCOVERY = "/api/affordability/v1/offer/discovery"
        AFFORDABILITY_OFFER_DISCOVERY_CARDLESS = "/api/affordability/v1/offer/discovery/cardless"

        # Plural — Orders / Status (used for payment status polling + order details)
        ORDERS = "/api/v1/orders"
        ORDER_STATUS = "/api/v1/orders/{order_id}/status"  # GET, format before use
        ORDER_DETAILS = "/api/v1/orders/{order_id}"        # GET, format before use

        # Plural — Affordability Suite — legacy path (kept for offer_engine.py fallback)
        OFFERS_DISCOVER = "/api/v1/offers/discover"
        CONVENIENCE_FEE = "/api/v1/convenience-fee"

        # Plural — Payment channels
        PAYMENT_LINKS = "/api/v1/payment-links"
        QR_CODES = "/api/v1/qr-codes"

        # Plural — Customers
        CUSTOMERS = "/api/v1/customers/{lookup}"  # GET, format before use

    @classmethod
    def legacy_headers(cls) -> dict:
        """
        Headers for EMI Calculator v3 (no Authorization header — auth is in body).
        """
        return {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    @classmethod
    def plural_headers(cls, token: str) -> dict:
        """
        Headers for all Plural API calls.
        Always call get_pine_labs_token() from tools/auth.py to get the token.

        Request-Timestamp and Request-ID are optional per Pine Labs docs but
        included here for better traceability and API hygiene.
        """
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Request-Timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z",
            "Request-ID": str(uuid.uuid4()),
        }

    @classmethod
    def auth_payload(cls) -> dict:
        """OAuth2 client_credentials body for POST /api/auth/v1/token."""
        return {
            "client_id": cls.CLIENT_ID,
            "client_secret": cls.CLIENT_SECRET,
            "grant_type": "client_credentials",
        }

    @classmethod
    def legacy_emi_payload(cls, amount_paisa: int, card_type: Optional[str] = None) -> dict:
        """Request body for POST /api/v3/emi/calculator."""
        payload: dict = {
            "merchant_data": {
                "merchant_id": int(cls.MERCHANT_ID) if cls.MERCHANT_ID else 0,
                "merchant_access_code": cls.ACCESS_CODE,
                "amount": amount_paisa,
            }
        }
        if card_type:
            payload["card_type"] = card_type
        return payload

    @classmethod
    def is_configured(cls) -> bool:
        """
        True if all required credentials are present.
        Use this to decide whether to attempt live API calls or fall straight to mock.
        """
        return bool(
            cls.MERCHANT_ID
            and cls.ACCESS_CODE
            and cls.CLIENT_ID
            and cls.CLIENT_SECRET
        )
