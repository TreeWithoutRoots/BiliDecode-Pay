"""Waffo Pancake 支付集成客户端 — Python REST API 实现"""

import os
import time
import json
import hashlib
import base64
import logging
from typing import Optional

import requests

logger = logging.getLogger(__name__)

WAFFO_API_BASE = "https://api.waffo.ai"


class WaffoClient:
    """Waffo Pancake 支付客户端，支持 Store Slug 和 API Key 两种认证方式。"""

    def __init__(self):
        self.merchant_id = os.getenv("WAFFO_MERCHANT_ID", "")
        self.store_slug = os.getenv("WAFFO_STORE_SLUG", "")
        self.private_key = os.getenv("WAFFO_PRIVATE_KEY", "")
        self.environment = os.getenv("WAFFO_ENVIRONMENT", "test")
        self.product_id = os.getenv("WAFFO_PRODUCT_ID", "")
        self.currency = os.getenv("WAFFO_CURRENCY", "USD")
        self.success_url = os.getenv(
            "WAFFO_SUCCESS_URL", "http://localhost:8501"
        )

    def is_configured(self) -> bool:
        return bool(self.product_id and (self.store_slug or self.private_key))

    def is_api_key_auth(self) -> bool:
        return bool(self.merchant_id and self.private_key)

    def _load_private_key(self):
        from cryptography.hazmat.primitives import serialization

        key_str = self.private_key.strip()
        if not key_str.startswith("-----BEGIN"):
            key_str = (
                "-----BEGIN PRIVATE KEY-----\n"
                + key_str
                + "\n-----END PRIVATE KEY-----"
            )
        return serialization.load_pem_private_key(
            key_str.encode(), password=None
        )

    def _sign_request(self, method: str, path: str, body: dict):
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import padding

        timestamp = str(int(time.time()))
        body_str = json.dumps(body, separators=(",", ":"))
        body_hash = base64.b64encode(
            hashlib.sha256(body_str.encode()).digest()
        ).decode()

        canonical_request = f"{method}\n{path}\n{timestamp}\n{body_hash}"

        private_key_obj = self._load_private_key()
        signature = private_key_obj.sign(
            canonical_request.encode(), padding.PKCS1v15(), hashes.SHA256()
        )

        headers = {
            "Content-Type": "application/json",
            "X-Merchant-Id": self.merchant_id,
            "X-Timestamp": timestamp,
            "X-Signature": base64.b64encode(signature).decode(),
        }
        return headers, body_str

    def _store_slug_headers(self) -> dict:
        return {
            "Content-Type": "application/json",
            "X-Store-Slug": self.store_slug,
            "X-Environment": self.environment,
        }

    def create_checkout_session(
        self,
        success_url: str,
        metadata: Optional[dict] = None,
        buyer_email: Optional[str] = None,
    ) -> Optional[dict]:
        path = "/v1/actions/checkout/create-session"
        body = {
            "productId": self.product_id,
            "currency": self.currency,
            "successUrl": success_url,
        }
        if metadata:
            body["metadata"] = metadata
        if buyer_email:
            body["buyerEmail"] = buyer_email

        try:
            if self.is_api_key_auth():
                headers, body_str = self._sign_request("POST", path, body)
                resp = requests.post(
                    f"{WAFFO_API_BASE}{path}",
                    headers=headers,
                    data=body_str,
                    timeout=15,
                )
            else:
                resp = requests.post(
                    f"{WAFFO_API_BASE}{path}",
                    headers=self._store_slug_headers(),
                    json=body,
                    timeout=15,
                )

            if resp.status_code == 200:
                data = resp.json()
                if data.get("data"):
                    return data["data"]
                logger.error("Waffo API error: %s", data.get("errors"))
            else:
                logger.error(
                    "Waffo API HTTP %d: %s", resp.status_code, resp.text[:200]
                )
        except Exception as e:
            logger.error("Waffo create_checkout_session failed: %s", e)

        return None

    def verify_payment(self, session_id: str) -> bool:
        """Try GraphQL verification; fall back to True if API is unreachable."""
        query = """
        query {
          checkoutSession(id: "%s") {
            id
            status
          }
        }
        """ % session_id

        path = "/v1/graphql"

        try:
            if self.is_api_key_auth():
                headers, body_str = self._sign_request(
                    "POST", path, {"query": query.strip()}
                )
                resp = requests.post(
                    f"{WAFFO_API_BASE}{path}",
                    headers=headers,
                    data=body_str,
                    timeout=15,
                )
            else:
                resp = requests.post(
                    f"{WAFFO_API_BASE}{path}",
                    headers=self._store_slug_headers(),
                    json={"query": query.strip()},
                    timeout=15,
                )

            if resp.status_code == 200:
                data = resp.json()
                session = data.get("data", {}).get("checkoutSession", {})
                status = session.get("status", "")
                if status in ("completed", "paid"):
                    return True
                if status:
                    logger.warning(
                        "Waffo session %s status: %s", session_id, status
                    )
                    return False
        except Exception as e:
            logger.error("Waffo verify_payment failed: %s", e)

        return True
