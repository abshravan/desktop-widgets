# launcher.py — Rainmeter-style control panel.
#
# Each row in the launcher is a toggle that shows/hides a separate floating
# widget window. State (which widgets are visible + each window's position)
# is persisted to ~/.config/desktop-widget/state.json so the same set is
# restored on next launch.
#
# Closing the launcher quits the whole application.

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QCheckBox,
    QApplication, QFrame, QScrollArea,
)
from PyQt6.QtCore import Qt, QPoint, QEvent
from PyQt6.QtGui import QPainter, QColor, QBrush

from ui.widget_window   import WidgetWindow
from ui.widget_registry import WIDGET_REGISTRY
from styles.theme       import COLORS, SEPARATOR_STYLE, SCROLLBAR_STYLE
from services           import storage

STATE_FILE = "state.json"


class Launcher(QWidget):
    def __init__(self):
        super().__init__()
        self._windows: dict[str, WidgetWindow] = {}
        self._drag_offset: QPoint | None = None

        # Persistent state: {"visible": [names], "positions": {name: [x, y]}, "launcher": [x, y]}
        self._state = storage.load(STATE_FILE, {
            "visible":   [],
            "positions": {},
            "launcher":  [40, 40],
        })

        self._setup_window()
        self._build_ui()
        QApplication.instance().installEventFilter(self)

        # Auto-show any widgets the user had visible last session
        for name in self._state.get("visible", []):
            if name in WIDGET_REGISTRY:
                self._show_widget(name)
                # Reflect state in the checkbox
                if name in self._checkboxes:
                    cb = self._checkboxes[name]
                    cb.blockSignals(True)
                    cb.setChecked(True)
                    cb.blockSignals(False)

    # ── Window flags ──────────────────────────────────────────────────────────

    def _setup_window(self):
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint,
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedWidth(240)
        pos = self._state.get("launcher", [40, 40])
        self.move(pos[0], pos[1])
        self.setWindowOpacity(0.96)
        self.setWindowTitle("Widgets")

    # ── UI ────────────────────────────────────────────────────────────────────

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(8, 8, 8, 8)
        outer.setSpacing(0)

        panel = QWidget(self)
        panel.setObjectName("LauncherPanel")
        panel.setStyleSheet(f"""
            QWidget#LauncherPanel {{
                background-color: {COLORS['bg_primary']};
                border-radius: 14px;
                border: 1px solid {COLORS['border']};
            }}
        """)
        outer.addWidget(panel)

        v = QVBoxLayout(panel)
        v.setContentsMargins(14, 12, 14, 12)
        v.setSpacing(8)

        # Header row (drag handle + quit dot)
        head = QHBoxLayout()
        head.setSpacing(8)

        quit_btn = QPushButton()
        quit_btn.setFixedSize(12, 12)
        quit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        quit_btn.setToolTip("Quit")
        quit_btn.setStyleSheet(f"""
            QPushButton {{
                background: {COLORS['accent_red']};
                border-radius: 6px;
                border: none;
            }}
            QPushButton:hover {{ background: #ff6159; }}
        """)
        quit_btn.clicked.connect(QApplication.instance().quit)
        head.addWidget(quit_btn)

        title = QLabel("Widgets")
        title.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['text_primary']};
                font-size: 13px;
                font-weight: 600;
            }}
        """)
        head.addWidget(title)
        head.addStretch()
        v.addLayout(head)

        # Subtle separator
        rule = QFrame()
        rule.setFrameShape(QFrame.Shape.HLine)
        rule.setStyleSheet(SEPARATOR_STYLE)
        v.addWidget(rule)

        # Scrollable list so the launcher stays compact regardless of widget count
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet(
            f"QScrollArea {{ background: transparent; border: none; }}"
            + SCROLLBAR_STYLE
        )
        scroll.setMaximumHeight(440)

        list_container = QWidget()
        list_container.setStyleSheet("background: transparent;")
        list_layout = QVBoxLayout(list_container)
        list_layout.setContentsMargins(0, 0, 0, 0)
        list_layout.setSpacing(4)

        self._checkboxes: dict[str, QCheckBox] = {}
        for name, meta in WIDGET_REGISTRY.items():
            list_layout.addLayout(self._make_row(name, meta))
        list_layout.addStretch()

        scroll.setWidget(list_container)
        v.addWidget(scroll)

    def _make_row(self, name: str, meta: dict) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(8)

        icon = QLabel(meta["icon"])
        icon.setFixedWidth(20)
        icon.setStyleSheet(f"QLabel {{ font-size: 14px; color: {COLORS['text_primary']}; }}")
        row.addWidget(icon)

        label = QLabel(meta["label"])
        label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['text_primary']};
                font-size: 12px;
            }}
        """)
        row.addWidget(label)
        row.addStretch()

        cb = QCheckBox()
        cb.setCursor(Qt.CursorShape.PointingHandCursor)
        cb.setStyleSheet(f"""
            QCheckBox::indicator {{
                width: 36px;
                height: 20px;
                border-radius: 10px;
                background: {COLORS['bg_card_inner']};
                border: none;
            }}
            QCheckBox::indicator:checked {{
                background: {COLORS['accent_green']};
            }}
        """)
        cb.toggled.connect(lambda checked, n=name: self._on_toggle(n, checked))
        self._checkboxes[name] = cb
        row.addWidget(cb)
        return row

    # ── Toggle handler ────────────────────────────────────────────────────────

    def _on_toggle(self, name: str, checked: bool):
        if checked:
            self._show_widget(name)
        else:
            self._hide_widget(name)
        self._persist()

    def _show_widget(self, name: str):
        meta = WIDGET_REGISTRY[name]
        win = self._windows.get(name)
        if win is None:
            start = tuple(self._state.get("positions", {}).get(name) or meta["default"])
            win = WidgetWindow(
                name=name,
                content_factory=meta["factory"],
                width=meta["width"],
                start_pos=start,
            )
            win.hidden.connect(self._on_window_hidden)
            win.moved.connect(self._on_window_moved)
            self._windows[name] = win
        win.show()
        win.raise_()

    def _hide_widget(self, name: str):
        win = self._windows.get(name)
        if win is not None:
            win.hide()

    # ── Signal callbacks from widget windows ──────────────────────────────────

    def _on_window_hidden(self, name: str):
        # The window was closed via its red dot — update the launcher toggle
        cb = self._checkboxes.get(name)
        if cb and cb.isChecked():
            cb.blockSignals(True)
            cb.setChecked(False)
            cb.blockSignals(False)
        self._persist()

    def _on_window_moved(self, name: str, x: int, y: int):
        self._state.setdefault("positions", {})[name] = [x, y]
        # Debounce-light: just save on each move; volume is tiny

    # ── Persistence ───────────────────────────────────────────────────────────

    def _persist(self):
        self._state["visible"] = [
            name for name, win in self._windows.items() if win.isVisible()
        ]
        self._state["launcher"] = [self.x(), self.y()]
        storage.save(STATE_FILE, self._state)

    def moveEvent(self, event):
        super().moveEvent(event)
        if self.isVisible():
            self._state["launcher"] = [self.x(), self.y()]

    def closeEvent(self, event):
        self._persist()
        QApplication.instance().quit()
        super().closeEvent(event)

    # ── Drag (same Wayland-safe pattern as WidgetWindow) ──────────────────────

    def eventFilter(self, obj, event):
        if not isinstance(obj, QWidget) or obj.window() is not self:
            return False
        etype = event.type()
        if etype == QEvent.Type.MouseButtonPress:
            if event.button() != Qt.MouseButton.LeftButton:
                return False
            if isinstance(obj, (QPushButton, QCheckBox)):
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

    # ── Soft drop shadow ──────────────────────────────────────────────────────

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        for i in range(6, 0, -1):
            alpha = int(50 * (i / 6) ** 2)
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QBrush(QColor(0, 0, 0, alpha)))
            m = 8 - i
            p.drawRoundedRect(m, m, self.width() - m * 2, self.height() - m * 2, 16, 16)
