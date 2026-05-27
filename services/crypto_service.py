# crypto_service.py — Async fetch of crypto prices from CoinGecko.
# Public endpoint, no API key required.

import requests
from PyQt6.QtCore import QThread, pyqtSignal

COINGECKO_URL = "https://api.coingecko.com/api/v3/simple/price"


class CryptoWorker(QThread):
    """Fetch latest USD prices + 24h change for a list of coin IDs."""

    data_ready = pyqtSignal(list)   # list of {"id", "price", "change"}
    error = pyqtSignal(str)

    def __init__(self, coin_ids: list[str], parent=None):
        super().__init__(parent)
        self._coin_ids = coin_ids

    def run(self):
        try:
            resp = requests.get(
                COINGECKO_URL,
                params={
                    "ids":                 ",".join(self._coin_ids),
                    "vs_currencies":       "usd",
                    "include_24hr_change": "true",
                },
                timeout=10,
                headers={"Accept": "application/json"},
            )
            resp.raise_for_status()
            data = resp.json()
            out = [
                {
                    "id":     coin,
                    "price":  data[coin]["usd"],
                    "change": data[coin].get("usd_24h_change", 0.0),
                }
                for coin in self._coin_ids if coin in data
            ]
            self.data_ready.emit(out)
        except requests.exceptions.ConnectionError:
            self.error.emit("No internet connection")
        except requests.exceptions.Timeout:
            self.error.emit("Request timed out")
        except Exception as e:
            self.error.emit(str(e))
