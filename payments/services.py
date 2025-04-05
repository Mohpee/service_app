import requests
import base64
from datetime import datetime
from django.conf import settings
from requests.exceptions import RequestException
from typing import Dict, Any

class MpesaService:
    def __init__(self):
        self.business_shortcode = settings.MPESA_SHORTCODE
        self.passkey = settings.MPESA_PASSKEY
        self.consumer_key = settings.MPESA_CONSUMER_KEY
        self.consumer_secret = settings.MPESA_CONSUMER_SECRET
        self.access_token = self._get_access_token()
        self.base_url = "https://sandbox.safaricom.co.ke"

    def _get_access_token(self) -> str:
        """Get M-Pesa API access token."""
        try:
            url = f"{self.base_url}/oauth/v1/generate?grant_type=client_credentials"
            auth = base64.b64encode(
                f"{self.consumer_key}:{self.consumer_secret}".encode()
            ).decode()
            headers = {"Authorization": f"Basic {auth}"}
            
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            return response.json()["access_token"]
        except RequestException as e:
            raise ValueError(f"Failed to get access token: {str(e)}")

    def stk_push(self, phone_number: str, amount: float, order_ref: str) -> Dict[str, Any]:
        """Initiate STK push payment."""
        try:
            url = f"{self.base_url}/mpesa/stkpush/v1/processrequest"
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            password = base64.b64encode(
                f"{self.business_shortcode}{self.passkey}{timestamp}".encode()
            ).decode()
            
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json",
            }
            
            payload = {
                "BusinessShortCode": self.business_shortcode,
                "Password": password,
                "Timestamp": timestamp,
                "TransactionType": "CustomerPayBillOnline",
                "Amount": int(amount),
                "PartyA": phone_number,
                "PartyB": self.business_shortcode,
                "PhoneNumber": phone_number,
                "CallBackURL": f"{settings.BASE_URL}/api/payments/mpesa-callback/",
                "AccountReference": f"Order#{order_ref}",
                "TransactionDesc": f"Payment for Order#{order_ref}"
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            raise ValueError(f"STK push request failed: {str(e)}")