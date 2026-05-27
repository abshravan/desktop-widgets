# weather_widget.py — Weather card. Spawns a WeatherWorker thread and
# updates the UI on success; shows an error message on failure.

from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout
)
from PyQt6.QtCore import Qt, QTimer
from styles.theme import (
    CARD_STYLE, SECTION_LABEL_STYLE,
    WEATHER_TEMP_STYLE, WEATHER_CITY_STYLE, WEATHER_DESC_STYLE,
    BATTERY_STATUS_STYLE, COLORS,
)
from services.weather_service import WeatherWorker
import config


class WeatherWidget(QFrame):
    def __init__(self, refresh_secs: int = 600, parent=None):
        super().__init__(parent)
        self.setStyleSheet(CARD_STYLE)
        self._worker = None
        self._build_ui()

        # Periodic refresh using a QTimer in seconds → convert to ms
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._fetch)
        self._timer.start(refresh_secs * 1000)
        self._fetch()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(6)

        section = QLabel("WEATHER")
        section.setStyleSheet(SECTION_LABEL_STYLE)
        layout.addWidget(section)

        # Primary row: emoji + temperature
        top = QHBoxLayout()
        top.setSpacing(8)

        self._emoji_label = QLabel("—")
        self._emoji_label.setStyleSheet("QLabel { font-size: 32px; }")
        top.addWidget(self._emoji_label)

        col = QVBoxLayout()
        col.setSpacing(0)
        self._temp_label = QLabel("—")
        self._temp_label.setStyleSheet(WEATHER_TEMP_STYLE)
        col.addWidget(self._temp_label)

        self._city_label = QLabel("—")
        self._city_label.setStyleSheet(WEATHER_CITY_STYLE)
        col.addWidget(self._city_label)

        top.addLayout(col)
        top.addStretch()
        layout.addLayout(top)

        self._desc_label = QLabel("")
        self._desc_label.setStyleSheet(WEATHER_DESC_STYLE)
        layout.addWidget(self._desc_label)

        # Details grid: feels like / humidity / wind
        grid = QGridLayout()
        grid.setSpacing(4)
        grid.setContentsMargins(0, 4, 0, 0)

        def _detail_pair(key, row):
            k = QLabel(key)
            k.setStyleSheet(f"QLabel {{ color: {COLORS['text_muted']}; font-size: 10px; }}")
            v = QLabel("—")
            v.setStyleSheet(f"QLabel {{ color: {COLORS['text_secondary']}; font-size: 11px; }}")
            grid.addWidget(k, row, 0)
            grid.addWidget(v, row, 1)
            return v

        self._feels_val  = _detail_pair("Feels like", 0)
        self._humid_val  = _detail_pair("Humidity",   1)
        self._wind_val   = _detail_pair("Wind",       2)

        layout.addLayout(grid)

        self._error_label = QLabel("")
        self._error_label.setStyleSheet(f"QLabel {{ color: {COLORS['accent_red']}; font-size: 10px; }}")
        self._error_label.setWordWrap(True)
        layout.addWidget(self._error_label)

    def _fetch(self):
        # Avoid stacking multiple threads if a previous one is still running
        if self._worker and self._worker.isRunning():
            return
        self._worker = WeatherWorker()
        self._worker.data_ready.connect(self._on_data)
        self._worker.error.connect(self._on_error)
        self._worker.start()

    def _on_data(self, data: dict):
        self._error_label.setText("")
        self._emoji_label.setText(data["emoji"])
        self._temp_label.setText(data["temp"])
        self._city_label.setText(data["city"])
        self._desc_label.setText(data["description"])
        self._feels_val.setText(data["feels_like"])
        self._humid_val.setText(data["humidity"])
        self._wind_val.setText(data["wind"])

    def _on_error(self, msg: str):
        self._error_label.setText(f"⚠ {msg}")
        # Keep showing last known good values
