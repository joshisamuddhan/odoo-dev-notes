"""Verify a webhook signature (Shopify/Stripe style) BEFORE trusting the payload."""
import base64
import hashlib
import hmac


def verify_hmac_hex(raw_body: bytes, secret: str, signature_hex: str) -> bool:
    expected = hmac.new(secret.encode(), raw_body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature_hex or "")  # constant-time compare


def verify_hmac_b64(raw_body: bytes, secret: str, signature_b64: str) -> bool:
    """Shopify sends base64 in X-Shopify-Hmac-Sha256."""
    digest = hmac.new(secret.encode(), raw_body, hashlib.sha256).digest()
    expected = base64.b64encode(digest).decode()
    return hmac.compare_digest(expected, signature_b64 or "")

# In an Odoo controller: use request.httprequest.get_data() (the RAW bytes) -
# never re-serialise parsed JSON, the bytes would differ and the signature fail.
