# clipboard_widget.py — Recent clipboard items. Click to copy back.
# Not persisted to disk (clipboards often contain sensitive data).

from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QApplication,
    QScrollArea, QWidget,
)
from PyQt6.QtCore import Qt
from styles.theme import CARD_STYLE, SECTION_LABEL_STYLE, SCROLLBAR_STYLE, COLORS

MAX_ITEMS  = 10
MAX_LENGTH = 60   # truncate long strings in the display


class ClipboardWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(CARD_STYLE)
        self._items: list[str] = []
        self._suppress_next = False     # avoid echoing when WE set clipboard
        self._build_ui()

        clipboard = QApplication.clipboard()
        clipboard.dataChanged.connect(self._capture)

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(6)

        head = QHBoxLayout()
        section = QLabel("CLIPBOARD")
        section.setStyleSheet(SECTION_LABEL_STYLE)
        head.addWidget(section)
        head.addStretch()

        clear = QPushButton("Clear")
        clear.setCursor(Qt.CursorShape.PointingHandCursor)
        clear.setFixedHeight(20)
        clear.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {COLORS['text_muted']};
                border: none;
                font-size: 10px;
                padding: 0 6px;
            }}
            QPushButton:hover {{ color: {COLORS['accent_red']}; }}
        """)
        clear.clicked.connect(self._clear)
        head.addWidget(clear)
        layout.addLayout(head)

        # Scrollable list of recent items
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet(
            f"QScrollArea {{ background: transparent; border: none; }}" + SCROLLBAR_STYLE
        )
        scroll.setMaximumHeight(180)

        self._list = QWidget()
        self._list.setStyleSheet("background: transparent;")
        self._list_layout = QVBoxLayout(self._list)
        self._list_layout.setContentsMargins(0, 4, 0, 0)
        self._list_layout.setSpacing(3)
        scroll.setWidget(self._list)
        layout.addWidget(scroll)

        self._empty_lbl = QLabel("No items yet — copy something")
        self._empty_lbl.setStyleSheet(f"QLabel {{ color: {COLORS['text_muted']}; font-size: 11px; }}")
        self._empty_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._list_layout.addWidget(self._empty_lbl)

    def _capture(self):
        if self._suppress_next:
            self._suppress_next = False
            return
        text = QApplication.clipboard().text()
        if not text or text in self._items:
            # Move existing entry to top instead of duplicating
            if text in self._items:
                self._items.remove(text)
                self._items.insert(0, text)
                self._render()
            return
        self._items.insert(0, text)
        self._items = self._items[:MAX_ITEMS]
        self._render()

    def _render(self):
        while self._list_layout.count():
            item = self._list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not self._items:
            self._empty_lbl = QLabel("No items yet — copy something")
            self._empty_lbl.setStyleSheet(f"QLabel {{ color: {COLORS['text_muted']}; font-size: 11px; }}")
            self._empty_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._list_layout.addWidget(self._empty_lbl)
            return

        for text in self._items:
            self._list_layout.addWidget(self._make_row(text))
        self._list_layout.addStretch()

    def _make_row(self, text: str) -> QPushButton:
        preview = text.replace("\n", " ⏎ ")
        if len(preview) > MAX_LENGTH:
            preview = preview[:MAX_LENGTH] + "…"

        btn = QPushButton(preview)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setToolTip(text[:300])
        btn.setStyleSheet(f"""
            QPushButton {{
                background: {COLORS['bg_card_inner']};
                color: {COLORS['text_primary']};
                border: none;
                border-radius: 6px;
                padding: 6px 8px;
                font-size: 11px;
                text-align: left;
            }}
            QPushButton:hover {{
                background: {COLORS['accent']};
                color: white;
            }}
        """)
        btn.clicked.connect(lambda _, t=text: self._copy_back(t))
        return btn

    def _copy_back(self, text: str):
        # Don't capture our own clipboard write
        self._suppress_next = True
        QApplication.clipboard().setText(text)
        # Move clicked item to the top
        if text in self._items:
            self._items.remove(text)
        self._items.insert(0, text)
        self._render()

    def _clear(self):
        self._items.clear()
        self._render()
