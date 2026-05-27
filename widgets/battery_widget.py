# battery_widget.py — Battery status card using psutil.
# Color-codes the percentage: green ≥50%, yellow 20–49%, red <20%.

import psutil
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
from styles.theme import (
    CARD_STYLE, SECTION_LABEL_STYLE,
    BATTERY_VALUE_STYLE, BATTERY_STATUS_STYLE, COLORS,
)


def _battery_color(percent: float) -> str:
    if percent >= 50:
        return COLORS["accent_green"]
    if percent >= 20:
        return COLORS["accent_yellow"]
    return COLORS["accent_red"]


def _battery_emoji(percent: float, charging: bool) -> str:
    if charging:
        return "⚡"
    if percent >= 80:
        return "🔋"
    if percent >= 40:
        return "🔋"
    return "🪫"


class BatteryWidget(QFrame):
    def __init__(self, refresh_ms: int = 30_000, parent=None):
        super().__init__(parent)
        self.setStyleSheet(CARD_STYLE)
        self._build_ui()

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._refresh)
        self._timer.start(refresh_ms)
        self._refresh()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(6)

        section = QLabel("BATTERY")
        section.setStyleSheet(SECTION_LABEL_STYLE)
        layout.addWidget(section)

        # Top row: emoji + percentage
        row = QHBoxLayout()
        row.setSpacing(8)

        self._emoji_label = QLabel()
        self._emoji_label.setStyleSheet(BATTERY_VALUE_STYLE)
        row.addWidget(self._emoji_label)

        self._pct_label = QLabel()
        self._pct_label.setStyleSheet(BATTERY_VALUE_STYLE)
        row.addWidget(self._pct_label)
        row.addStretch()

        self._status_label = QLabel()
        self._status_label.setStyleSheet(BATTERY_STATUS_STYLE)
        row.addWidget(self._status_label)

        layout.addLayout(row)

        # Progress bar representing battery level
        self._bar = QProgressBar()
        self._bar.setRange(0, 100)
        self._bar.setTextVisible(False)
        self._bar.setFixedHeight(6)
        self._bar.setStyleSheet(f"""
            QProgressBar {{
                background: {COLORS['bg_secondary']};
                border-radius: 3px;
                border: none;
            }}
            QProgressBar::chunk {{
                border-radius: 3px;
            }}
        """)
        layout.addWidget(self._bar)

        self._time_label = QLabel()
        self._time_label.setStyleSheet(BATTERY_STATUS_STYLE)
        layout.addWidget(self._time_label)

    def _refresh(self):
        battery = psutil.sensors_battery()
        if battery is None:
            self._pct_label.setText("N/A")
            self._status_label.setText("No battery")
            self._emoji_label.setText("🔌")
            self._time_label.setText("")
            return

        pct = battery.percent
        charging = battery.power_plugged
        color = _battery_color(pct)

        self._emoji_label.setText(_battery_emoji(pct, charging))
        self._pct_label.setText(f"{pct:.0f}%")
        self._pct_label.setStyleSheet(f"QLabel {{ color: {color}; font-size: 16px; font-weight: 600; }}")
        self._status_label.setText("Charging" if charging else "Discharging")

        # Color the bar chunk to match percentage severity
        self._bar.setValue(int(pct))
        self._bar.setStyleSheet(f"""
            QProgressBar {{
                background: {COLORS['bg_secondary']};
                border-radius: 3px;
                border: none;
            }}
            QProgressBar::chunk {{
                background: {color};
                border-radius: 3px;
            }}
        """)

        # Show estimated time remaining / until full
        secs = battery.secsleft
        if secs == psutil.POWER_TIME_UNLIMITED or secs == psutil.POWER_TIME_UNKNOWN or secs < 0:
            self._time_label.setText("")
        else:
            h, m = divmod(secs // 60, 60)
            label = "until full" if charging else "remaining"
            self._time_label.setText(f"{h}h {m:02d}m {label}")
