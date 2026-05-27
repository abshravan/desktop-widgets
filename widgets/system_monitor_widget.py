# system_monitor_widget.py — CPU and RAM usage with live sparkline charts.
# Keeps a rolling window of recent values and draws them as a smooth polyline.

from collections import deque
import psutil
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QWidget
from PyQt6.QtCore import Qt, QTimer, QPointF
from PyQt6.QtGui import QPainter, QColor, QPen, QPainterPath, QBrush, QLinearGradient
from styles.theme import CARD_STYLE, SECTION_LABEL_STYLE, COLORS


class Sparkline(QWidget):
    """A self-contained mini line chart that paints a rolling deque of values."""

    def __init__(self, color: str, max_points: int = 60, parent=None):
        super().__init__(parent)
        self._values: deque[float] = deque([0.0] * max_points, maxlen=max_points)
        self._color = QColor(color)
        self.setFixedHeight(32)

    def push(self, value: float):
        self._values.append(value)
        self.update()

    def paintEvent(self, event):
        if not self._values:
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()
        n = len(self._values)
        if n < 2:
            return

        step = w / (n - 1)
        pts = [
            QPointF(i * step, h - (v / 100.0) * (h - 2) - 1)
            for i, v in enumerate(self._values)
        ]

        # Filled gradient beneath the line
        path = QPainterPath()
        path.moveTo(pts[0])
        for pt in pts[1:]:
            path.lineTo(pt)
        fill = QPainterPath(path)
        fill.lineTo(w, h)
        fill.lineTo(0, h)
        fill.closeSubpath()

        grad = QLinearGradient(0, 0, 0, h)
        c = QColor(self._color)
        c.setAlpha(80)
        grad.setColorAt(0, c)
        c2 = QColor(self._color)
        c2.setAlpha(0)
        grad.setColorAt(1, c2)
        p.fillPath(fill, QBrush(grad))

        # The line itself
        pen = QPen(self._color)
        pen.setWidthF(1.5)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        p.setPen(pen)
        p.drawPath(path)


class SystemMonitorWidget(QFrame):
    def __init__(self, refresh_ms: int = 2000, parent=None):
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
        layout.setSpacing(8)

        section = QLabel("SYSTEM")
        section.setStyleSheet(SECTION_LABEL_STYLE)
        layout.addWidget(section)

        # CPU row
        cpu_row = QHBoxLayout()
        cpu_row.setSpacing(8)
        cpu_lbl = QLabel("CPU")
        cpu_lbl.setStyleSheet(f"QLabel {{ color: {COLORS['text_secondary']}; font-size: 11px; }}")
        cpu_lbl.setFixedWidth(28)
        cpu_row.addWidget(cpu_lbl)

        self._cpu_spark = Sparkline(COLORS["accent"])
        cpu_row.addWidget(self._cpu_spark, 1)

        self._cpu_val = QLabel("0%")
        self._cpu_val.setStyleSheet(f"QLabel {{ color: {COLORS['text_primary']}; font-size: 12px; font-weight: 600; }}")
        self._cpu_val.setFixedWidth(38)
        self._cpu_val.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        cpu_row.addWidget(self._cpu_val)
        layout.addLayout(cpu_row)

        # RAM row
        ram_row = QHBoxLayout()
        ram_row.setSpacing(8)
        ram_lbl = QLabel("RAM")
        ram_lbl.setStyleSheet(f"QLabel {{ color: {COLORS['text_secondary']}; font-size: 11px; }}")
        ram_lbl.setFixedWidth(28)
        ram_row.addWidget(ram_lbl)

        self._ram_spark = Sparkline(COLORS["accent_green"])
        ram_row.addWidget(self._ram_spark, 1)

        self._ram_val = QLabel("0%")
        self._ram_val.setStyleSheet(f"QLabel {{ color: {COLORS['text_primary']}; font-size: 12px; font-weight: 600; }}")
        self._ram_val.setFixedWidth(38)
        self._ram_val.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        ram_row.addWidget(self._ram_val)
        layout.addLayout(ram_row)

    def _refresh(self):
        # `interval=None` returns the average since last call — non-blocking
        cpu = psutil.cpu_percent(interval=None)
        ram = psutil.virtual_memory().percent
        self._cpu_spark.push(cpu)
        self._ram_spark.push(ram)
        self._cpu_val.setText(f"{cpu:.0f}%")
        self._ram_val.setText(f"{ram:.0f}%")
