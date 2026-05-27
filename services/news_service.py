# news_service.py — Fetches top headlines from NewsAPI (newsapi.org).
# Falls back gracefully when the key is missing or network is unavailable.

import requests
from PyQt6.QtCore import QThread, pyqtSignal
import config

NEWSAPI_BASE = "https://newsapi.org/v2/top-headlines"


class NewsWorker(QThread):
    """Fetches headlines asynchronously and emits a list of article dicts."""

    data_ready = pyqtSignal(list)   # list of {"title": str, "url": str}
    error = pyqtSignal(str)

    def run(self):
        if config.NEWS_API_KEY == "YOUR_NEWS_API_KEY":
            self.error.emit("No API key — set NEWS_API_KEY")
            return
        try:
            resp = requests.get(
                NEWSAPI_BASE,
                params={
                    "country":  config.NEWS_COUNTRY,
                    "pageSize": config.NEWS_MAX_HEADLINES,
                    "apiKey":   config.NEWS_API_KEY,
                },
                timeout=10,
            )
            resp.raise_for_status()
            raw = resp.json()

            if raw.get("status") != "ok":
                self.error.emit(raw.get("message", "NewsAPI error"))
                return

            articles = [
                {"title": a["title"], "url": a["url"]}
                for a in raw.get("articles", [])
                if a.get("title") and a.get("url")
            ]
            self.data_ready.emit(articles[: config.NEWS_MAX_HEADLINES])
        except requests.exceptions.ConnectionError:
            self.error.emit("No internet connection")
        except requests.exceptions.Timeout:
            self.error.emit("News request timed out")
        except requests.exceptions.HTTPError as e:
            self.error.emit(f"HTTP {e.response.status_code}")
        except Exception as e:
            self.error.emit(str(e))
