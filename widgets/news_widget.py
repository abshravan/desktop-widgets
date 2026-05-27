# news_widget.py — News headlines card.
# Each headline is a clickable button that opens the article in the browser.

import webbrowser
from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QLabel, QPushButton,
    QScrollArea, QWidget,
)
from PyQt6.QtCore import Qt, QTimer
from styles.theme import (
    CARD_STYLE, SECTION_LABEL_STYLE,
    HEADLINE_BUTTON_STYLE, SEPARATOR_STYLE,
    SCROLLBAR_STYLE, COLORS,
)
from services.news_service import NewsWorker
import config


class NewsWidget(QFrame):
    def __init__(self, refresh_secs: int = 900, parent=None):
        super().__init__(parent)
        self.setStyleSheet(CARD_STYLE)
        self._worker = None
        self._articles: list[dict] = []
        self._build_ui()

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._fetch)
        self._timer.start(refresh_secs * 1000)
        self._fetch()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(6)

        section = QLabel("TOP HEADLINES")
        section.setStyleSheet(SECTION_LABEL_STYLE)
        layout.addWidget(section)

        # Scrollable area holds the dynamic headline list
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setStyleSheet(
            f"QScrollArea {{ background: transparent; border: none; }}"
            + SCROLLBAR_STYLE
        )
        scroll.setMaximumHeight(200)

        self._list_widget = QWidget()
        self._list_widget.setStyleSheet("background: transparent;")
        self._list_layout = QVBoxLayout(self._list_widget)
        self._list_layout.setContentsMargins(0, 0, 0, 0)
        self._list_layout.setSpacing(0)

        scroll.setWidget(self._list_widget)
        layout.addWidget(scroll)

        self._error_label = QLabel("")
        self._error_label.setStyleSheet(
            f"QLabel {{ color: {COLORS['accent_red']}; font-size: 10px; }}"
        )
        self._error_label.setWordWrap(True)
        layout.addWidget(self._error_label)

    def _fetch(self):
        if self._worker and self._worker.isRunning():
            return
        self._worker = NewsWorker()
        self._worker.data_ready.connect(self._on_data)
        self._worker.error.connect(self._on_error)
        self._worker.start()

    def _on_data(self, articles: list):
        self._error_label.setText("")
        self._articles = articles
        self._render_headlines()

    def _render_headlines(self):
        # Clear previous headlines
        while self._list_layout.count():
            item = self._list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for i, article in enumerate(self._articles):
            btn = QPushButton(f"• {article['title']}")
            btn.setStyleSheet(HEADLINE_BUTTON_STYLE)
            btn.setWordWrap(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)

            # Capture URL by default argument to avoid late-binding closure issue
            url = article["url"]
            btn.clicked.connect(lambda checked, u=url: webbrowser.open(u))
            self._list_layout.addWidget(btn)

            # Add a thin separator between items (not after the last one)
            if i < len(self._articles) - 1:
                sep = QFrame()
                sep.setFrameShape(QFrame.Shape.HLine)
                sep.setStyleSheet(SEPARATOR_STYLE)
                self._list_layout.addWidget(sep)

        self._list_layout.addStretch()

    def _on_error(self, msg: str):
        self._error_label.setText(f"⚠ {msg}")
