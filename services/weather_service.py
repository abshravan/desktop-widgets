# weather_service.py — Fetches current weather from OpenWeatherMap.
# Runs in a background QThread so the UI never freezes on slow networks.

import requests
from PyQt6.QtCore import QThread, pyqtSignal
import config

# Maps OWM icon codes to Unicode emoji fallbacks (no internet required for icons).
WEATHER_EMOJI = {
    "01": "☀️",  "02": "⛅",  "03": "☁️",  "04": "☁️",
    "09": "🌧️", "10": "🌦️", "11": "⛈️", "13": "❄️",  "50": "🌫️",
}

OWM_BASE = "https://api.openweathermap.org/data/2.5/weather"


def _icon_to_emoji(icon_code: str) -> str:
    prefix = icon_code[:2]
    return WEATHER_EMOJI.get(prefix, "🌡️")


class WeatherWorker(QThread):
    """Fetches weather data asynchronously and emits result or error."""

    data_ready = pyqtSignal(dict)   # emitted on success
    error = pyqtSignal(str)         # emitted on failure

    def run(self):
        if config.OPENWEATHER_API_KEY == "YOUR_OPENWEATHER_API_KEY":
            self.error.emit("No API key — set OPENWEATHER_API_KEY")
            return
        try:
            resp = requests.get(
                OWM_BASE,
                params={
                    "q":     config.WEATHER_CITY,
                    "appid": config.OPENWEATHER_API_KEY,
                    "units": config.WEATHER_UNITS,
                },
                timeout=10,
            )
            resp.raise_for_status()
            raw = resp.json()

            unit_symbol = "°C" if config.WEATHER_UNITS == "metric" else "°F"
            icon_code = raw["weather"][0]["icon"]

            self.data_ready.emit({
                "city":        raw["name"],
                "temp":        f"{round(raw['main']['temp'])}{unit_symbol}",
                "feels_like":  f"{round(raw['main']['feels_like'])}{unit_symbol}",
                "description": raw["weather"][0]["description"].title(),
                "humidity":    f"{raw['main']['humidity']}%",
                "wind":        f"{round(raw['wind']['speed'])} m/s",
                "emoji":       _icon_to_emoji(icon_code),
            })
        except requests.exceptions.ConnectionError:
            self.error.emit("No internet connection")
        except requests.exceptions.Timeout:
            self.error.emit("Weather request timed out")
        except requests.exceptions.HTTPError as e:
            self.error.emit(f"HTTP {e.response.status_code}")
        except Exception as e:
            self.error.emit(str(e))
