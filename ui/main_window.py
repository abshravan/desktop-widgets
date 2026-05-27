# main_window.py — macOS-style floating widget, reliable native drag.
#
# Drag strategy: QWindow.startSystemMove() hands the move operation to the
# window manager (X11/Wayland) so child widgets can never steal it.
# Pure-Python delta tracking is kept as a fallback for older compositors.

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


# ── Drag bar ──────────────────────────────────────────────────────────────────

class DragBar(QWidget):
    """
    Dedicated 40 px drag zone at the top of the panel.
    No sub-layouts that could swallow events — only the close dot is a child
    (it sits in the top-left corner; the rest of the bar is empty surface).

    On press we call QWindow.startSystemMove() which delegates the entire
    drag gesture to the window manager.  This works on X11 and most Wayland
    compositors.  A Python-delta fallback handles the rare case it returns
    False (e.g. undecorated kwin on older configs).
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(40)
        self.setCursor(Qt.CursorShape.SizeAllCursor)
        self._drag_pos: QPoint | None = None
        self._dragging_native = False
        self._build_close_button()

    def _build_close_button(self):
        # Absolutely positioned — NOT in a layout so it never covers the drag area
        close = QPushButton(self)
        close.setFixedSize(14, 14)
        close.move(14, 13)           # left-aligned, vertically centred in 40px bar
        close.setCursor(Qt.CursorShape.PointingHandCursor)
        close.setToolTip("Close")
        close.setStyleSheet(f"""
            QPushButton {{
                background: {COLORS['accent_red']};
                border-radius: 7px;
                border: none;
            }}
            QPushButton:hover {{ background: #ff6159; }}
        """)
        close.clicked.connect(lambda: self.window().close())
        close.raise_()

    # ── Pill indicator ────────────────────────────────────────────────────────

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        active = self._drag_pos is not None or self._dragging_native
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(QColor("#6e6e73" if active else "#48484a")))
        pw, ph = 40, 4
        p.drawRoundedRect(
            (self.width() - pw) // 2,
            (self.height() - ph) // 2,
            pw, ph, 2, 2,
        )

    # ── Mouse events ──────────────────────────────────────────────────────────

    def mousePressEvent(self, event):
        if event.button() != Qt.MouseButton.LeftButton:
            return
        event.accept()

        win = self.window()
        handle = win.windowHandle()

        if handle:
            # Native WM drag: survives any Qt event re-routing on X11/Wayland
            self._dragging_native = handle.startSystemMove()
            if self._dragging_native:
                self.update()
                return

        # Fallback: manual tracking
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
        self._dragging_native = False
        self.setCursor(Qt.CursorShape.SizeAllCursor)
        self.update()

    def enterEvent(self, event):
        self.setCursor(Qt.CursorShape.SizeAllCursor)


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
        outer = QVBoxLayout(self)
        outer.setContentsMargins(10, 10, 10, 10)
        outer.setSpacing(0)

        # ── Panel ─────────────────────────────────────────────────────────────
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

        # Drag bar lives at the very top of the panel
        vbox.addWidget(DragBar(panel))

        # Content
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

    def paintEvent(self, event):
        # Multi-layer soft drop-shadow painted on the transparent outer margin
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        for i in range(8, 0, -1):
            alpha = int(55 * (i / 8) ** 2)
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QBrush(QColor(0, 0, 0, alpha)))
            m = 10 - i
            p.drawRoundedRect(m, m, self.width() - m * 2, self.height() - m * 2, 22, 22)
