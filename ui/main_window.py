# main_window.py — Drag works from anywhere on the widget.
#
# Strategy: install an event filter on QApplication itself. That sees EVERY
# mouse event in the whole app before any widget can consume it. We filter
# for events on our own widget tree and move the window accordingly.
# QPushButton presses are ignored so close/headline buttons still work.
#
# Additional fixes from previous attempts:
#   - Dropped Qt.WindowType.Tool: on GNOME/Wayland it can make the window
#     unmoveable via standard means.
#   - Removed nested layout indirection — DragBar still exists as a visual
#     hint, but drag is global across the panel.

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QFrame, QHBoxLayout, QLabel, QPushButton,
    QApplication,
)
from PyQt6.QtCore import Qt, QPoint, QEvent
from PyQt6.QtGui import QPainter, QColor, QBrush

from widgets.clock_widget   import ClockWidget
from widgets.battery_widget import BatteryWidget
from widgets.weather_widget import WeatherWidget
from widgets.news_widget    import NewsWidget
from styles.theme           import COLORS, SEPARATOR_STYLE
import config


# ── Visual drag handle (purely decorative — drag works everywhere) ────────────

class DragBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(38)
        self.setCursor(Qt.CursorShape.OpenHandCursor)

        # Close dot in top-left
        close = QPushButton(self)
        close.setFixedSize(14, 14)
        close.move(14, 12)
        close.setCursor(Qt.CursorShape.PointingHandCursor)
        close.setStyleSheet(f"""
            QPushButton {{
                background: {COLORS['accent_red']};
                border-radius: 7px;
                border: none;
            }}
            QPushButton:hover {{ background: #ff6159; }}
        """)
        close.clicked.connect(lambda: self.window().close())

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(QColor("#6e6e73")))
        pw, ph = 44, 5
        p.drawRoundedRect(
            (self.width() - pw) // 2,
            (self.height() - ph) // 2,
            pw, ph, 2, 2,
        )


# ── Main window ───────────────────────────────────────────────────────────────

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self._drag_offset: QPoint | None = None
        self._setup_window()
        self._build_ui()

        # The KEY change: install the filter on QApplication. This catches
        # every mouse event before child widgets get a chance to swallow it.
        QApplication.instance().installEventFilter(self)

    # ── Window setup ──────────────────────────────────────────────────────────

    def _setup_window(self):
        # Note: Qt.WindowType.Tool is intentionally NOT used here — on
        # GNOME/Wayland it can prevent the window from being moved.
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint,
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedWidth(config.WINDOW_WIDTH)
        self.move(config.WINDOW_X, config.WINDOW_Y)
        self.setWindowOpacity(config.WINDOW_OPACITY)

    # ── UI ────────────────────────────────────────────────────────────────────

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(10, 10, 10, 10)
        outer.setSpacing(0)

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

        vbox.addWidget(DragBar(panel))

        body = QVBoxLayout()
        body.setContentsMargins(12, 0, 12, 0)
        body.setSpacing(10)

        body.addWidget(ClockWidget())
        body.addWidget(self._rule())
        body.addWidget(BatteryWidget(config.BATTERY_REFRESH_INTERVAL))
        body.addWidget(self._rule())
        body.addWidget(WeatherWidget(config.WEATHER_REFRESH_INTERVAL))
        body.addWidget(self._rule())
        body.addWidget(NewsWidget(config.NEWS_REFRESH_INTERVAL))

        vbox.addLayout(body)

    def _rule(self) -> QFrame:
        r = QFrame()
        r.setFrameShape(QFrame.Shape.HLine)
        r.setStyleSheet(SEPARATOR_STYLE)
        return r

    # ── Drag via QApplication-level event filter ──────────────────────────────

    def eventFilter(self, obj, event):
        # Only handle events for widgets that belong to THIS window.
        if not isinstance(obj, QWidget) or obj.window() is not self:
            return False

        etype = event.type()

        if etype == QEvent.Type.MouseButtonPress:
            if event.button() == Qt.MouseButton.LeftButton:
                # Let buttons handle their own clicks
                if isinstance(obj, QPushButton):
                    return False
                # Record offset between cursor and window top-left
                self._drag_offset = event.globalPosition().toPoint() - self.pos()
                print(f"[drag] press on {type(obj).__name__} — offset={self._drag_offset}")
                return False

        elif etype == QEvent.Type.MouseMove:
            if self._drag_offset is not None and (event.buttons() & Qt.MouseButton.LeftButton):
                new_pos = event.globalPosition().toPoint() - self._drag_offset
                self.move(new_pos)
                return False

        elif etype == QEvent.Type.MouseButtonRelease:
            if self._drag_offset is not None:
                print("[drag] release")
            self._drag_offset = None

        return False

    # ── Drop shadow ───────────────────────────────────────────────────────────

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        for i in range(8, 0, -1):
            alpha = int(55 * (i / 8) ** 2)
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QBrush(QColor(0, 0, 0, alpha)))
            m = 10 - i
            p.drawRoundedRect(m, m, self.width() - m * 2, self.height() - m * 2, 22, 22)
