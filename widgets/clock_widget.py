# clock_widget.py — Self-contained clock/date card.
# Uses a QTimer that fires every second to update labels in-place.

from datetime import datetime
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
from styles.theme import (
    CARD_STYLE, SECTION_LABEL_STYLE,
    CLOCK_TIME_STYLE, CLOCK_DATE_STYLE,
)


class ClockWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(CARD_STYLE)
        self._build_ui()

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(1000)  # update every second
        self._tick()             # populate immediately on startup

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(2)

        section = QLabel("CLOCK")
        section.setStyleSheet(SECTION_LABEL_STYLE)
        layout.addWidget(section)

        self._time_label = QLabel()
        self._time_label.setStyleSheet(CLOCK_TIME_STYLE)
        self._time_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self._time_label)

        self._date_label = QLabel()
        self._date_label.setStyleSheet(CLOCK_DATE_STYLE)
        layout.addWidget(self._date_label)

    def _tick(self):
        now = datetime.now()
        self._time_label.setText(now.strftime("%H:%M:%S"))
        self._date_label.setText(now.strftime("%A, %B %-d %Y"))
