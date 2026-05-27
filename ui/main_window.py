# main_window.py — macOS-style floating panel.
# Drag handled by QApplication-level event filter + windowHandle().startSystemMove().

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QFrame, QHBoxLayout, QLabel, QPushButton,
    QApplication, QScrollArea,
)
from PyQt6.QtCore import Qt, QPoint, QEvent
from PyQt6.QtGui import QPainter, QColor, QBrush

from widgets.clock_widget          import ClockWidget
from widgets.battery_widget        import BatteryWidget
from widgets.weather_widget        import WeatherWidget
from widgets.news_widget           import NewsWidget
from widgets.system_monitor_widget import SystemMonitorWidget
from widgets.pomodoro_widget       import PomodoroWidget
from widgets.todo_widget           import TodoWidget
from styles.theme                  import COLORS, SEPARATOR_STYLE, SCROLLBAR_STYLE
from services                      import storage
import config

POSITION_KEY = "window.json"


# ── Visual drag handle (purely decorative — drag works everywhere) ────────────

class DragBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(38)
        self.setCursor(Qt.CursorShape.OpenHandCursor)

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
        QApplication.instance().installEventFilter(self)

    def _setup_window(self):
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint,
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedWidth(config.WINDOW_WIDTH)

        # Restore last position if we saved one, otherwise use config defaults
        saved = storage.load(POSITION_KEY, None)
        if saved and "x" in saved and "y" in saved:
            self.move(saved["x"], saved["y"])
        else:
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
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(0)

        vbox.addWidget(DragBar(panel))

        # Body wrapped in a scroll area so users can fit more cards in a smaller window
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet(
            f"QScrollArea {{ background: transparent; border: none; }}" + SCROLLBAR_STYLE
        )

        body = QWidget()
        body.setStyleSheet("background: transparent;")
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(12, 0, 12, 14)
        body_layout.setSpacing(10)

        body_layout.addWidget(ClockWidget())
        body_layout.addWidget(self._rule())
        body_layout.addWidget(SystemMonitorWidget())
        body_layout.addWidget(self._rule())
        body_layout.addWidget(BatteryWidget(config.BATTERY_REFRESH_INTERVAL))
        body_layout.addWidget(self._rule())
        body_layout.addWidget(PomodoroWidget())
        body_layout.addWidget(self._rule())
        body_layout.addWidget(TodoWidget())
        body_layout.addWidget(self._rule())
        body_layout.addWidget(WeatherWidget(config.WEATHER_REFRESH_INTERVAL))
        body_layout.addWidget(self._rule())
        body_layout.addWidget(NewsWidget(config.NEWS_REFRESH_INTERVAL))
        body_layout.addStretch()

        scroll.setWidget(body)
        vbox.addWidget(scroll, 1)

        # Give the window a sensible default height
        self.setFixedHeight(config.WINDOW_HEIGHT)

    def _rule(self) -> QFrame:
        r = QFrame()
        r.setFrameShape(QFrame.Shape.HLine)
        r.setStyleSheet(SEPARATOR_STYLE)
        return r

    # ── Drag via QApplication-level event filter ──────────────────────────────

    def eventFilter(self, obj, event):
        if not isinstance(obj, QWidget) or obj.window() is not self:
            return False

        etype = event.type()

        if etype == QEvent.Type.MouseButtonPress:
            if event.button() != Qt.MouseButton.LeftButton:
                return False
            # Skip interactive widgets so they keep working normally
            if isinstance(obj, QPushButton):
                return False
            # Skip text input and checkboxes (todo widget)
            from PyQt6.QtWidgets import QLineEdit, QCheckBox
            if isinstance(obj, (QLineEdit, QCheckBox)):
                return False

            handle = self.windowHandle()
            if handle is not None and handle.startSystemMove():
                return False

            self._drag_offset = event.globalPosition().toPoint() - self.pos()
            return False

        elif etype == QEvent.Type.MouseMove:
            if self._drag_offset is not None and (event.buttons() & Qt.MouseButton.LeftButton):
                self.move(event.globalPosition().toPoint() - self._drag_offset)
            return False

        elif etype == QEvent.Type.MouseButtonRelease:
            self._drag_offset = None

        return False

    # ── Save position on close ────────────────────────────────────────────────

    def closeEvent(self, event):
        storage.save(POSITION_KEY, {"x": self.x(), "y": self.y()})
        super().closeEvent(event)

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
