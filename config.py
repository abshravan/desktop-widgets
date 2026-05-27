# config.py — Central configuration for all API keys and app settings.
# Replace placeholder strings with your actual API keys before running.

import os

# --- API Keys ---
# Get a free key at: https://openweathermap.org/api
OPENWEATHER_API_KEY = os.environ.get("OPENWEATHER_API_KEY", "YOUR_OPENWEATHER_API_KEY")

# Get a free key at: https://newsapi.org  (fallback: https://gnews.io)
NEWS_API_KEY = os.environ.get("NEWS_API_KEY", "YOUR_NEWS_API_KEY")

# --- Weather Settings ---
WEATHER_CITY = os.environ.get("WEATHER_CITY", "London")
WEATHER_UNITS = "metric"          # "metric" = Celsius, "imperial" = Fahrenheit
WEATHER_REFRESH_INTERVAL = 600    # seconds (10 minutes)

# --- News Settings ---
NEWS_COUNTRY = "us"               # ISO 3166-1 alpha-2 country code
NEWS_MAX_HEADLINES = 5
NEWS_REFRESH_INTERVAL = 900       # seconds (15 minutes)

# --- Clock Settings ---
CLOCK_REFRESH_INTERVAL = 1000     # milliseconds

# --- Battery Settings ---
BATTERY_REFRESH_INTERVAL = 30000  # milliseconds (30 seconds)

# --- Window Settings ---
WINDOW_WIDTH = 320
WINDOW_HEIGHT = 720
WINDOW_X = 50          # initial X position (pixels from left)
WINDOW_Y = 50          # initial Y position (pixels from top)
WINDOW_OPACITY = 0.92  # 0.0 (invisible) to 1.0 (solid)
