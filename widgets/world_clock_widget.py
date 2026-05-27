# world_clock_widget.py — Multiple timezones at a glance.
# Edit WORLD_CLOCK_ZONES in config.py to customise the city list.

from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt, QTimer
from styles.theme import CARD_STYLE, SECTION_LABEL_STYLE, COLORS
import config


# Default cities used if config doesn't override them
DEFAULT_ZONES = [
    ("New York", "America/New_York"),
    ("London",   "Europe/London"),
    ("Mumbai",   "Asia/Kolkata"),
    ("Tokyo",    "Asia/Tokyo"),
]


class WorldClockWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(CARD_STYLE)
        self._zones = getattr(config, "WORLD_CLOCK_ZONES", DEFAULT_ZONES)
        self._rows: list[tuple[QLabel, QLabel, str]] = []
        self._build_ui()

        # Refresh every 30 seconds — minute precision is fine here
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._refresh)
        self._timer.start(30_000)
        self._refresh()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(6)

        section = QLabel("WORLD CLOCK")
        section.setStyleSheet(SECTION_LABEL_STYLE)
        layout.addWidget(section)

        for city, tz in self._zones:
            row = QHBoxLayout()
            row.setSpacing(8)

            city_lbl = QLabel(city)
            city_lbl.setStyleSheet(f"QLabel {{ color: {COLORS['text_primary']}; font-size: 12px; font-weight: 600; }}")
            row.addWidget(city_lbl, 1)

            time_lbl = QLabel("--:--")
            time_lbl.setStyleSheet(f"QLabel {{ color: {COLORS['text_primary']}; font-size: 14px; font-weight: 500; }}")
            time_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
            row.addWidget(time_lbl)

            day_lbl = QLabel("")
            day_lbl.setStyleSheet(f"QLabel {{ color: {COLORS['text_muted']}; font-size: 10px; }}")
            day_lbl.setFixedWidth(34)
            day_lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            row.addWidget(day_lbl)

            self._rows.append((time_lbl, day_lbl, tz))
            layout.addLayout(row)

    def _refresh(self):
        local_day = datetime.now().day
        for time_lbl, day_lbl, tz in self._rows:
            try:
                now = datetime.now(ZoneInfo(tz))
                time_lbl.setText(now.strftime("%H:%M"))
                # Show ±1 day when the remote date differs from local
                delta_day = now.day - local_day
                day_lbl.setText(
                    "+1" if delta_day in (1, -27, -28, -29, -30)
                    else "−1" if delta_day in (-1, 27, 28, 29, 30)
                    else ""
                )
            except ZoneInfoNotFoundError:
                time_lbl.setText("?")
                day_lbl.setText("")
