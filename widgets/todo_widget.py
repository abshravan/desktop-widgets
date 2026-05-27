# todo_widget.py — Persistent todo list.
# Add items with the line edit; click checkbox to mark done; × removes.
# Saved to ~/.config/desktop-widget/todos.json on every change.

from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QCheckBox, QLineEdit, QWidget, QScrollArea,
)
from PyQt6.QtCore import Qt
from styles.theme import CARD_STYLE, SECTION_LABEL_STYLE, SCROLLBAR_STYLE, COLORS
from services import storage

STORAGE_KEY = "todos.json"


class TodoWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(CARD_STYLE)
        # Each item is {"text": str, "done": bool}
        self._items: list[dict] = storage.load(STORAGE_KEY, [])
        self._build_ui()
        self._render()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(6)

        head = QHBoxLayout()
        section = QLabel("TODO")
        section.setStyleSheet(SECTION_LABEL_STYLE)
        head.addWidget(section)
        head.addStretch()

        self._count_lbl = QLabel()
        self._count_lbl.setStyleSheet(f"QLabel {{ color: {COLORS['text_muted']}; font-size: 10px; }}")
        head.addWidget(self._count_lbl)
        layout.addLayout(head)

        # Input row
        row = QHBoxLayout()
        row.setSpacing(6)
        self._input = QLineEdit()
        self._input.setPlaceholderText("Add a task…")
        self._input.setStyleSheet(f"""
            QLineEdit {{
                background: {COLORS['bg_card_inner']};
                color: {COLORS['text_primary']};
                border: none;
                border-radius: 6px;
                padding: 5px 8px;
                font-size: 11px;
            }}
        """)
        self._input.returnPressed.connect(self._add)
        row.addWidget(self._input)

        add_btn = QPushButton("+")
        add_btn.setFixedSize(26, 26)
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.setStyleSheet(f"""
            QPushButton {{
                background: {COLORS['accent']};
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 16px;
                font-weight: 600;
            }}
            QPushButton:hover {{ background: #4a9eff; }}
        """)
        add_btn.clicked.connect(self._add)
        row.addWidget(add_btn)
        layout.addLayout(row)

        # Scrollable item list
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet(f"QScrollArea {{ background: transparent; border: none; }}" + SCROLLBAR_STYLE)
        scroll.setMaximumHeight(140)

        self._list_widget = QWidget()
        self._list_widget.setStyleSheet("background: transparent;")
        self._list_layout = QVBoxLayout(self._list_widget)
        self._list_layout.setContentsMargins(0, 4, 0, 0)
        self._list_layout.setSpacing(2)
        scroll.setWidget(self._list_widget)
        layout.addWidget(scroll)

    def _add(self):
        text = self._input.text().strip()
        if not text:
            return
        self._items.append({"text": text, "done": False})
        self._input.clear()
        self._save()
        self._render()

    def _toggle(self, index: int, checked: bool):
        self._items[index]["done"] = checked
        self._save()
        self._render()  # re-render to update strikethrough style

    def _remove(self, index: int):
        del self._items[index]
        self._save()
        self._render()

    def _save(self):
        storage.save(STORAGE_KEY, self._items)

    def _render(self):
        # Clear existing rows
        while self._list_layout.count():
            item = self._list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for i, todo in enumerate(self._items):
            self._list_layout.addWidget(self._make_row(i, todo))
        self._list_layout.addStretch()

        done = sum(1 for t in self._items if t["done"])
        total = len(self._items)
        self._count_lbl.setText(f"{done}/{total}")

    def _make_row(self, index: int, todo: dict) -> QWidget:
        row = QWidget()
        row.setStyleSheet("background: transparent;")
        h = QHBoxLayout(row)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(6)

        cb = QCheckBox()
        cb.setChecked(todo["done"])
        cb.setCursor(Qt.CursorShape.PointingHandCursor)
        cb.setStyleSheet(f"""
            QCheckBox::indicator {{
                width: 14px; height: 14px;
                border: 1.5px solid {COLORS['text_muted']};
                border-radius: 7px;
                background: transparent;
            }}
            QCheckBox::indicator:checked {{
                background: {COLORS['accent_green']};
                border-color: {COLORS['accent_green']};
            }}
        """)
        cb.toggled.connect(lambda checked, idx=index: self._toggle(idx, checked))
        h.addWidget(cb)

        decoration = "text-decoration: line-through;" if todo["done"] else ""
        color = COLORS["text_muted"] if todo["done"] else COLORS["text_primary"]
        label = QLabel(todo["text"])
        label.setWordWrap(True)
        label.setStyleSheet(f"QLabel {{ color: {color}; font-size: 11px; {decoration} }}")
        h.addWidget(label, 1)

        rm = QPushButton("×")
        rm.setFixedSize(18, 18)
        rm.setCursor(Qt.CursorShape.PointingHandCursor)
        rm.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {COLORS['text_muted']};
                border: none;
                font-size: 14px;
            }}
            QPushButton:hover {{ color: {COLORS['accent_red']}; }}
        """)
        rm.clicked.connect(lambda _, idx=index: self._remove(idx))
        h.addWidget(rm)
        return row
