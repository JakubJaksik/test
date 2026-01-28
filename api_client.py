"""
Binance API Client - connects to Binance Spot API
"""

import requests
import hmac
import hashlib
import time
from typing import Dict, Any


class BinanceClient:
    """Client for Binance Spot API v3."""

    BASE_URL = "https://api.binance.com/api/v3"

    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret

    def _sign_request(self, params: Dict[str, Any]) -> str:
        """Generate signature for authenticated requests."""
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature

    def create_order(self, symbol: str, side: str, quantity: float, price: float):
        """
        Create a new order on Binance.

        Uses POST /api/v3/order endpoint.

        Args:
            symbol: Trading pair (e.g., "BTCUSDT")
            side: "BUY" or "SELL"
            quantity: Order quantity
            price: Order price

        Returns:
            Order creation response
        """
        endpoint = f"{self.BASE_URL}/order"
        params = {
            "symbol": symbol,
            "side": side,
            "type": "LIMIT",
            "quantity": quantity,
            "price": price,
            "timeInForce": "GTC",  # Good Till Cancel
            "timestamp": int(time.time() * 1000)
        }

        # Sign request
        params["signature"] = self._sign_request(params)

        response = requests.post(
            endpoint,
            params=params,
            headers={"X-MBX-APIKEY": self.api_key}
        )
        response.raise_for_status()
        return response.json()

    def get_account_balance(self):
        """
        Get account balance.

        Uses GET /api/v3/account endpoint.

        Returns:
            Account information including balances
        """
        endpoint = f"{self.BASE_URL}/account"
        params = {
            "timestamp": int(time.time() * 1000)
        }

        # Sign request
        params["signature"] = self._sign_request(params)

        response = requests.get(
            endpoint,
            params=params,
            headers={"X-MBX-APIKEY": self.api_key}
        )
        response.raise_for_status()
        return response.json()

    def get_order_status(self, symbol: str, order_id: str):
        """
        Get status of an existing order.

        Args:
            symbol: Trading pair
            order_id: Order ID from create_order response

        Returns:
            Order status
        """
        endpoint = f"{self.BASE_URL}/order"
        params = {
            "symbol": symbol,
            "orderId": order_id,
            "timestamp": int(time.time() * 1000)
        }

        params["signature"] = self._sign_request(params)

        response = requests.get(
            endpoint,
            params=params,
            headers={"X-MBX-APIKEY": self.api_key}
        )
        response.raise_for_status()
        return response.json()
