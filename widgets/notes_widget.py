# notes_widget.py — Free-form sticky note. Auto-saves debounced (500ms).
# All notes persist to ~/.config/desktop-widget/notes.txt.

from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel, QTextEdit, QHBoxLayout
from PyQt6.QtCore import Qt, QTimer
from styles.theme import CARD_STYLE, SECTION_LABEL_STYLE, COLORS, SCROLLBAR_STYLE
from services import storage

STORAGE_KEY = "notes.txt"


class NotesWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(CARD_STYLE)
        self._build_ui()

        # Debounced auto-save: timer fires 500 ms after the last keystroke
        self._save_timer = QTimer(self)
        self._save_timer.setSingleShot(True)
        self._save_timer.timeout.connect(self._save)

        # Load any existing note
        existing = storage.load(STORAGE_KEY, "")
        if isinstance(existing, str):
            self._editor.setPlainText(existing)
        self._editor.textChanged.connect(self._on_changed)

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(6)

        head = QHBoxLayout()
        section = QLabel("NOTES")
        section.setStyleSheet(SECTION_LABEL_STYLE)
        head.addWidget(section)
        head.addStretch()

        self._saved_lbl = QLabel("saved")
        self._saved_lbl.setStyleSheet(f"QLabel {{ color: {COLORS['text_muted']}; font-size: 10px; }}")
        head.addWidget(self._saved_lbl)
        layout.addLayout(head)

        self._editor = QTextEdit()
        self._editor.setPlaceholderText("Jot anything down…")
        self._editor.setStyleSheet(f"""
            QTextEdit {{
                background: {COLORS['bg_card_inner']};
                color: {COLORS['text_primary']};
                border: none;
                border-radius: 8px;
                padding: 8px;
                font-size: 12px;
                selection-background-color: {COLORS['accent']};
            }}
            {SCROLLBAR_STYLE}
        """)
        self._editor.setMinimumHeight(140)
        layout.addWidget(self._editor)

    def _on_changed(self):
        self._saved_lbl.setText("editing…")
        self._save_timer.start(500)

    def _save(self):
        storage.save(STORAGE_KEY, self._editor.toPlainText())
        self._saved_lbl.setText("saved")
