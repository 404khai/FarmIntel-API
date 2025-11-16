import os
import requests
from django.conf import settings

PAYSTACK_SECRET_KEY = getattr(settings, "PAYSTACK_SECRET_KEY", None)
PAYSTACK_BASE = "https://api.paystack.co"

HEADERS = {
    "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
    "Content-Type": "application/json",
}

def initialize_transaction(email, amount_kobo, callback_url=None, metadata=None):
    """
    Call Paystack initialize endpoint.
    amount_kobo: integer amount (kobo)
    returns dict (response)
    """
    url = f"{PAYSTACK_BASE}/transaction/initialize"
    payload = {
        "email": email,
        "amount": amount_kobo,
    }
    if callback_url:
        payload["callback_url"] = callback_url
    if metadata:
        payload["metadata"] = metadata

    resp = requests.post(url, json=payload, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    return resp.json()


def verify_transaction(reference):
    url = f"{PAYSTACK_BASE}/transaction/verify/{reference}"
    resp = requests.get(url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    return resp.json()
