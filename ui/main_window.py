# main_window.py — macOS Sonoma-style floating widget.
# Drag is handled by a dedicated TitleBar widget — no eventFilter tricks.

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QFrame, QHBoxLayout, QLabel, QPushButton,
)
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QPainter, QColor, QBrush

from widgets.clock_widget   import ClockWidget
from widgets.battery_widget import BatteryWidget
from widgets.weather_widget import WeatherWidget
from widgets.news_widget    import NewsWidget
from styles.theme           import COLORS, SEPARATOR_STYLE
import config


# ── Dedicated drag handle ─────────────────────────────────────────────────────

class TitleBar(QWidget):
    """
    The ONLY draggable surface in the window.
    Owns its own mouse events — zero event-filter magic needed.
    Shows: macOS red close dot (left) | pill indicator (centre).
    """

    def __init__(self, close_cb, parent=None):
        super().__init__(parent)
        self.setFixedHeight(38)
        self._drag_pos: QPoint | None = None
        self.setCursor(Qt.CursorShape.SizeAllCursor)
        self._build(close_cb)

    def _build(self, close_cb):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 0, 14, 0)
        layout.setSpacing(0)

        # ── Traffic-light close button (macOS style) ──────────────────────────
        close = QPushButton()
        close.setFixedSize(14, 14)
        close.setCursor(Qt.CursorShape.PointingHandCursor)
        close.setToolTip("Close")
        close.setStyleSheet(f"""
            QPushButton {{
                background: {COLORS['accent_red']};
                border-radius: 7px;
                border: none;
            }}
            QPushButton:hover {{
                background: #ff6159;
            }}
        """)
        close.clicked.connect(close_cb)
        layout.addWidget(close)

        layout.addStretch()

        # Right spacer balances the close dot so the pill stays centred
        spacer = QWidget()
        spacer.setFixedSize(14, 1)
        spacer.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        layout.addWidget(spacer)

    def paintEvent(self, event):
        # Draw the iOS-style pill indicator in the vertical centre
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        active = self._drag_pos is not None
        p.setBrush(QBrush(QColor("#6e6e73" if active else "#48484a")))
        p.setPen(Qt.PenStyle.NoPen)
        pw, ph = 40, 4
        p.drawRoundedRect(
            (self.width() - pw) // 2,
            (self.height() - ph) // 2,
            pw, ph, 2, 2,
        )

    # ── Mouse events — all drag logic lives here ──────────────────────────────

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            self.update()

    def mouseMoveEvent(self, event):
        if self._drag_pos and event.buttons() & Qt.MouseButton.LeftButton:
            cur = event.globalPosition().toPoint()
            self.window().move(self.window().pos() + cur - self._drag_pos)
            self._drag_pos = cur

    def mouseReleaseEvent(self, event):
        self._drag_pos = None
        self.setCursor(Qt.CursorShape.SizeAllCursor)
        self.update()


# ── Main window ───────────────────────────────────────────────────────────────

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self._setup_window()
        self._build_ui()

    def _setup_window(self):
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool,
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedWidth(config.WINDOW_WIDTH)
        self.move(config.WINDOW_X, config.WINDOW_Y)
        self.setWindowOpacity(config.WINDOW_OPACITY)

    def _build_ui(self):
        # Outer layout adds a margin so the drop shadow (painted below) is visible
        outer = QVBoxLayout(self)
        outer.setContentsMargins(10, 10, 10, 10)
        outer.setSpacing(0)

        # ── Main panel ────────────────────────────────────────────────────────
        panel = QWidget(self)
        panel.setObjectName("Panel")
        panel.setStyleSheet(f"""
            QWidget#Panel {{
                background-color: {COLORS['bg_primary']};
                border-radius: 20px;
                border: 1px solid {COLORS['border']};
            }}
        """)
        outer.addWidget(panel)

        vbox = QVBoxLayout(panel)
        vbox.setContentsMargins(0, 0, 0, 14)
        vbox.setSpacing(0)

        # ── Title / drag bar ──────────────────────────────────────────────────
        vbox.addWidget(TitleBar(self.close, self))

        # ── Content area ──────────────────────────────────────────────────────
        content = QVBoxLayout()
        content.setContentsMargins(12, 0, 12, 0)
        content.setSpacing(10)

        content.addWidget(ClockWidget(self))
        content.addWidget(self._rule())
        content.addWidget(BatteryWidget(config.BATTERY_REFRESH_INTERVAL, self))
        content.addWidget(self._rule())
        content.addWidget(WeatherWidget(config.WEATHER_REFRESH_INTERVAL, self))
        content.addWidget(self._rule())
        content.addWidget(NewsWidget(config.NEWS_REFRESH_INTERVAL, self))

        vbox.addLayout(content)

    def _rule(self) -> QFrame:
        r = QFrame()
        r.setFrameShape(QFrame.Shape.HLine)
        r.setStyleSheet(SEPARATOR_STYLE)
        return r

    def paintEvent(self, event):
        # Soft drop shadow painted on the transparent outer margin
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        for i in range(8, 0, -1):
            alpha = int(60 * (i / 8) ** 2)
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QBrush(QColor(0, 0, 0, alpha)))
            p.drawRoundedRect(
                10 - i, 10 - i,
                self.width() - (10 - i) * 2,
                self.height() - (10 - i) * 2,
                22, 22,
            )
