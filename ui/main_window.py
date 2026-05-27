# main_window.py — Frameless, always-on-top floating widget window.
# Handles window dragging via mouse press/move events on the background.

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QFrame, QHBoxLayout,
    QLabel, QPushButton, QScrollArea,
)
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QPainter, QColor, QBrush, QPen

from widgets.clock_widget   import ClockWidget
from widgets.battery_widget import BatteryWidget
from widgets.weather_widget import WeatherWidget
from widgets.news_widget    import NewsWidget
from styles.theme           import COLORS, SEPARATOR_STYLE
import config


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self._drag_pos: QPoint | None = None
        self._setup_window()
        self._build_ui()

    # ── Window configuration ─────────────────────────────────────────────────

    def _setup_window(self):
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool,          # keeps widget off the taskbar
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedWidth(config.WINDOW_WIDTH)
        self.move(config.WINDOW_X, config.WINDOW_Y)
        self.setWindowOpacity(config.WINDOW_OPACITY)

    # ── UI construction ───────────────────────────────────────────────────────

    def _build_ui(self):
        # Outer container — gives us a surface to paint the rounded background on
        outer = QVBoxLayout(self)
        outer.setContentsMargins(8, 8, 8, 8)  # shadow padding
        outer.setSpacing(0)

        self._container = QWidget(self)
        self._container.setObjectName("MainWidget")
        self._container.setStyleSheet(f"""
            QWidget#MainWidget {{
                background-color: {COLORS['bg_primary']};
                border-radius: 16px;
                border: 1px solid {COLORS['border']};
            }}
        """)
        outer.addWidget(self._container)

        inner = QVBoxLayout(self._container)
        inner.setContentsMargins(12, 12, 12, 12)
        inner.setSpacing(10)

        # Title bar row (drag handle + close button)
        inner.addLayout(self._title_bar())

        # ── Widget cards ─────────────────────────────────────────────────────
        inner.addWidget(ClockWidget(self))
        inner.addWidget(self._separator())
        inner.addWidget(BatteryWidget(config.BATTERY_REFRESH_INTERVAL, self))
        inner.addWidget(self._separator())
        inner.addWidget(WeatherWidget(config.WEATHER_REFRESH_INTERVAL, self))
        inner.addWidget(self._separator())
        inner.addWidget(NewsWidget(config.NEWS_REFRESH_INTERVAL, self))

        inner.addStretch()

    def _title_bar(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setContentsMargins(4, 0, 4, 0)

        icon = QLabel("◈")
        icon.setStyleSheet(f"QLabel {{ color: {COLORS['accent']}; font-size: 14px; }}")
        row.addWidget(icon)

        title = QLabel("Desktop Widget")
        title.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['text_secondary']};
                font-size: 11px;
                font-weight: 600;
                letter-spacing: 0.5px;
            }}
        """)
        row.addWidget(title)
        row.addStretch()

        close_btn = QPushButton("✕")
        close_btn.setFixedSize(20, 20)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                color: {COLORS['text_muted']};
                background: transparent;
                border: none;
                font-size: 12px;
            }}
            QPushButton:hover {{ color: {COLORS['accent_red']}; }}
        """)
        close_btn.clicked.connect(self.close)
        row.addWidget(close_btn)
        return row

    def _separator(self) -> QFrame:
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(SEPARATOR_STYLE)
        return sep

    # ── Drag support ──────────────────────────────────────────────────────────

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self._drag_pos is not None and event.buttons() & Qt.MouseButton.LeftButton:
            delta = event.globalPosition().toPoint() - self._drag_pos
            self.move(self.pos() + delta)
            self._drag_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        self._drag_pos = None
