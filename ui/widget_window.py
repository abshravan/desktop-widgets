# widget_window.py — Frameless, chromeless window for a single widget.
#
# No drag bar, no title bar — the widget IS the window. The user drags by
# clicking anywhere on the widget body (handled by the QApplication event
# filter) and closes via the launcher toggle.
#
# Each widget already paints its own rounded card background, so the
# wrapper only adds a soft drop shadow on the outer margin.

from typing import Callable
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QApplication, QLineEdit, QCheckBox,
    QMenu,
)
from PyQt6.QtCore import Qt, QPoint, QEvent, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QBrush, QAction


class WidgetWindow(QWidget):
    """Frameless container that hosts a single widget with a drop shadow."""

    hidden = pyqtSignal(str)
    moved  = pyqtSignal(str, int, int)

    SHADOW_MARGIN = 8     # transparent border around the card for shadow
    SHADOW_RADIUS = 16    # rounded-corner radius (match the cards inside)

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
        self._setup_window(width, start_pos)
        self._build_ui(content_factory)
        QApplication.instance().installEventFilter(self)
        # Right-click on the widget body shows a small "Close" menu
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)

    # ── Window flags ──────────────────────────────────────────────────────────

    def _setup_window(self, width: int, start_pos: tuple[int, int]):
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint,
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedWidth(width + self.SHADOW_MARGIN * 2)
        self.move(*start_pos)
        self.setCursor(Qt.CursorShape.OpenHandCursor)

    # ── Layout: just the widget, framed by shadow margin ──────────────────────

    def _build_ui(self, content_factory: Callable[[], QWidget]):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            self.SHADOW_MARGIN, self.SHADOW_MARGIN,
            self.SHADOW_MARGIN, self.SHADOW_MARGIN,
        )
        layout.setSpacing(0)
        self._content = content_factory()
        layout.addWidget(self._content)

    # ── Right-click → close menu ──────────────────────────────────────────────

    def _show_context_menu(self, pos: QPoint):
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background: #2c2c2e;
                color: white;
                border: 1px solid #38383a;
                border-radius: 6px;
                padding: 4px;
            }
            QMenu::item {
                padding: 6px 16px;
                border-radius: 4px;
                font-size: 12px;
            }
            QMenu::item:selected { background: #0a84ff; }
        """)
        close_action = QAction("Close widget", self)
        close_action.triggered.connect(self._close_widget)
        menu.addAction(close_action)
        menu.exec(self.mapToGlobal(pos))

    def _close_widget(self):
        self.hide()
        self.hidden.emit(self.name)

    # ── Drop shadow ───────────────────────────────────────────────────────────

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        for i in range(self.SHADOW_MARGIN, 0, -1):
            alpha = int(55 * (i / self.SHADOW_MARGIN) ** 2)
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QBrush(QColor(0, 0, 0, alpha)))
            m = self.SHADOW_MARGIN - i
            p.drawRoundedRect(
                m, m,
                self.width() - m * 2,
                self.height() - m * 2,
                self.SHADOW_RADIUS + 2,
                self.SHADOW_RADIUS + 2,
            )

    # ── Drag (QApplication-level filter; Wayland-safe via startSystemMove) ────

    def eventFilter(self, obj, event):
        if not isinstance(obj, QWidget) or obj.window() is not self:
            return False

        etype = event.type()
        if etype == QEvent.Type.MouseButtonPress:
            if event.button() != Qt.MouseButton.LeftButton:
                return False
            # Interactive children keep working normally
            if isinstance(obj, (QPushButton, QLineEdit, QCheckBox)):
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

    # ── Persist position on every move ────────────────────────────────────────

    def moveEvent(self, event):
        super().moveEvent(event)
        if self.isVisible():
            self.moved.emit(self.name, self.x(), self.y())
