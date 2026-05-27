# widget_window.py — Generic frameless window that wraps a single widget.
#
# Every Rainmeter-style floating panel uses one of these.  The wrapper
# provides:
#   - rounded macOS-style panel background
#   - drag bar with red close dot (hides the widget rather than quitting)
#   - per-widget position memory (saved to state.json on close/move)
#   - always-on-top floating behaviour
#
# The actual content widget (ClockWidget, TodoWidget, ...) is passed in
# via a factory callable, so a single class supports every widget type.

from typing import Callable
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QApplication, QLineEdit, QCheckBox,
)
from PyQt6.QtCore import Qt, QPoint, QEvent, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QBrush
from styles.theme import COLORS


# ── Drag handle (red close dot + pill grip) ───────────────────────────────────

class _DragBar(QWidget):
    closed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(28)
        self.setCursor(Qt.CursorShape.OpenHandCursor)

        close = QPushButton(self)
        close.setFixedSize(12, 12)
        close.move(10, 8)
        close.setCursor(Qt.CursorShape.PointingHandCursor)
        close.setStyleSheet(f"""
            QPushButton {{
                background: {COLORS['accent_red']};
                border-radius: 6px;
                border: none;
            }}
            QPushButton:hover {{ background: #ff6159; }}
        """)
        close.clicked.connect(self.closed.emit)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(QColor("#6e6e73")))
        pw, ph = 36, 4
        p.drawRoundedRect(
            (self.width() - pw) // 2,
            (self.height() - ph) // 2,
            pw, ph, 2, 2,
        )


# ── Generic widget window ─────────────────────────────────────────────────────

class WidgetWindow(QWidget):
    """Frameless, always-on-top container for a single widget."""

    # Emitted when the user closes this window via the red dot
    hidden = pyqtSignal(str)        # carries the widget name
    moved  = pyqtSignal(str, int, int)  # widget name, new x, y

    def __init__(
        self,
        name: str,
        content_factory: Callable[[], QWidget],
        width: int = 260,
        start_pos: tuple[int, int] = (60, 60),
        parent=None,
    ):
        super().__init__(parent)
        self.name = name
        self._drag_offset: QPoint | None = None
        self._moved_since_press = False
        self._setup_window(width, start_pos)
        self._build_ui(content_factory)
        QApplication.instance().installEventFilter(self)

    # ── Window flags ──────────────────────────────────────────────────────────

    def _setup_window(self, width: int, start_pos: tuple[int, int]):
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint,
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedWidth(width)
        self.move(*start_pos)

    # ── Layout ────────────────────────────────────────────────────────────────

    def _build_ui(self, content_factory: Callable[[], QWidget]):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(8, 8, 8, 8)  # space for drop shadow
        outer.setSpacing(0)

        panel = QWidget(self)
        panel.setObjectName("Panel")
        panel.setStyleSheet(f"""
            QWidget#Panel {{
                background-color: {COLORS['bg_primary']};
                border-radius: 16px;
                border: 1px solid {COLORS['border']};
            }}
        """)
        outer.addWidget(panel)

        inner = QVBoxLayout(panel)
        inner.setContentsMargins(0, 0, 0, 10)
        inner.setSpacing(0)

        drag = _DragBar(panel)
        drag.closed.connect(self._on_close_clicked)
        inner.addWidget(drag)

        # Content sits below the drag bar with side margins
        body = QVBoxLayout()
        body.setContentsMargins(10, 0, 10, 0)
        body.addWidget(content_factory())
        inner.addLayout(body)

    # ── Close → just hide; launcher reopens later ─────────────────────────────

    def _on_close_clicked(self):
        self.hide()
        self.hidden.emit(self.name)

    # ── Drop shadow ───────────────────────────────────────────────────────────

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        for i in range(6, 0, -1):
            alpha = int(50 * (i / 6) ** 2)
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QBrush(QColor(0, 0, 0, alpha)))
            m = 8 - i
            p.drawRoundedRect(m, m, self.width() - m * 2, self.height() - m * 2, 18, 18)

    # ── Drag (QApplication-level filter; Wayland-safe via startSystemMove) ────

    def eventFilter(self, obj, event):
        if not isinstance(obj, QWidget) or obj.window() is not self:
            return False

        etype = event.type()
        if etype == QEvent.Type.MouseButtonPress:
            if event.button() != Qt.MouseButton.LeftButton:
                return False
            if isinstance(obj, (QPushButton, QLineEdit, QCheckBox)):
                return False

            self._moved_since_press = False
            handle = self.windowHandle()
            if handle is not None and handle.startSystemMove():
                return False
            self._drag_offset = event.globalPosition().toPoint() - self.pos()
            return False

        elif etype == QEvent.Type.MouseMove:
            if self._drag_offset is not None and (event.buttons() & Qt.MouseButton.LeftButton):
                self.move(event.globalPosition().toPoint() - self._drag_offset)
                self._moved_since_press = True
            return False

        elif etype == QEvent.Type.MouseButtonRelease:
            self._drag_offset = None

        return False

    # ── Persist position whenever the window moves ────────────────────────────

    def moveEvent(self, event):
        super().moveEvent(event)
        # Skip the very first move that Qt fires during construction
        if self.isVisible():
            self.moved.emit(self.name, self.x(), self.y())
