# network_widget.py — Live network up/down throughput with sparklines.
# Computes byte deltas between samples via psutil.net_io_counters().

import psutil
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt, QTimer
from styles.theme import CARD_STYLE, SECTION_LABEL_STYLE, COLORS
from widgets.system_monitor_widget import Sparkline   # reuse the sparkline


def _human_rate(bytes_per_sec: float) -> str:
    """Convert B/s to a short human-readable string."""
    for unit in ("B/s", "KB/s", "MB/s", "GB/s"):
        if bytes_per_sec < 1024:
            return f"{bytes_per_sec:.1f} {unit}"
        bytes_per_sec /= 1024
    return f"{bytes_per_sec:.1f} TB/s"


class NetworkWidget(QFrame):
    def __init__(self, refresh_ms: int = 1500, parent=None):
        super().__init__(parent)
        self.setStyleSheet(CARD_STYLE)
        self._interval = refresh_ms / 1000.0
        self._last = psutil.net_io_counters()
        self._max_seen = 1.0   # adaptive scaling so sparklines stay visible
        self._build_ui()

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._refresh)
        self._timer.start(refresh_ms)

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(8)

        section = QLabel("NETWORK")
        section.setStyleSheet(SECTION_LABEL_STYLE)
        layout.addWidget(section)

        self._down_row, self._down_spark, self._down_val = self._make_row(
            "↓", COLORS["accent"],
        )
        self._up_row, self._up_spark, self._up_val = self._make_row(
            "↑", COLORS["accent_green"],
        )
        layout.addLayout(self._down_row)
        layout.addLayout(self._up_row)

    def _make_row(self, arrow: str, color: str):
        row = QHBoxLayout()
        row.setSpacing(8)

        lbl = QLabel(arrow)
        lbl.setStyleSheet(f"QLabel {{ color: {color}; font-size: 13px; font-weight: 700; }}")
        lbl.setFixedWidth(14)
        row.addWidget(lbl)

        spark = Sparkline(color)
        row.addWidget(spark, 1)

        val = QLabel("0 B/s")
        val.setStyleSheet(f"QLabel {{ color: {COLORS['text_primary']}; font-size: 11px; font-weight: 600; }}")
        val.setFixedWidth(72)
        val.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        row.addWidget(val)
        return row, spark, val

    def _refresh(self):
        cur = psutil.net_io_counters()
        down_bps = (cur.bytes_recv - self._last.bytes_recv) / self._interval
        up_bps   = (cur.bytes_sent - self._last.bytes_sent) / self._interval
        self._last = cur

        # Auto-scale sparklines: track largest recent value, decay slowly
        self._max_seen = max(self._max_seen * 0.97, down_bps, up_bps, 1.0)
        scale = 100.0 / self._max_seen

        self._down_spark.push(min(down_bps * scale, 100))
        self._up_spark.push(min(up_bps * scale, 100))
        self._down_val.setText(_human_rate(down_bps))
        self._up_val.setText(_human_rate(up_bps))
