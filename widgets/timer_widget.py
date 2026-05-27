# timer_widget.py — Quick countdown timer.
# Preset buttons (1/5/10/15/30 min) plus start/pause/reset.
# Fires a desktop notification + plays a system bell on completion.

import subprocess
from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton,
    QApplication,
)
from PyQt6.QtCore import Qt, QTimer
from styles.theme import CARD_STYLE, SECTION_LABEL_STYLE, COLORS


def _notify(message: str):
    try:
        subprocess.run(
            ["notify-send", "-a", "Desktop Widget", "Timer", message],
            check=False, timeout=2,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass


class TimerWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(CARD_STYLE)
        self._remaining = 0      # seconds left in current countdown
        self._initial = 0        # total seconds for reset
        self._running = False
        self._build_ui()

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._update_display()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 14)
        layout.setSpacing(8)

        section = QLabel("TIMER")
        section.setStyleSheet(SECTION_LABEL_STYLE)
        layout.addWidget(section)

        self._display = QLabel("00:00")
        self._display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._display.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['text_primary']};
                font-size: 30px;
                font-weight: 600;
                letter-spacing: 2px;
            }}
        """)
        layout.addWidget(self._display)

        # Preset grid: 1 / 5 / 10 / 15 / 30 minutes
        presets = QGridLayout()
        presets.setSpacing(4)
        for i, mins in enumerate([1, 5, 10, 15, 30]):
            btn = self._make_btn(f"{mins}m", COLORS["bg_card_inner"], COLORS["text_primary"])
            btn.clicked.connect(lambda _, m=mins: self._set(m * 60))
            presets.addWidget(btn, i // 5, i % 5)
        layout.addLayout(presets)

        # Start/pause + reset row
        controls = QHBoxLayout()
        controls.setSpacing(6)
        self._start_btn = self._make_btn("Start", COLORS["accent"], "white")
        self._start_btn.clicked.connect(self._toggle)
        controls.addWidget(self._start_btn)

        reset = self._make_btn("Reset", COLORS["bg_card_inner"], COLORS["text_primary"])
        reset.clicked.connect(self._reset)
        controls.addWidget(reset)
        layout.addLayout(controls)

    def _make_btn(self, text: str, bg: str, fg: str) -> QPushButton:
        btn = QPushButton(text)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setFixedHeight(28)
        btn.setStyleSheet(f"""
            QPushButton {{
                background: {bg};
                color: {fg};
                border: none;
                border-radius: 6px;
                font-size: 11px;
                font-weight: 600;
            }}
            QPushButton:hover {{ background: {COLORS['accent_orange']}; color: white; }}
        """)
        return btn

    def _set(self, seconds: int):
        # Choosing a preset stops any current countdown and queues the new duration
        self._timer.stop()
        self._running = False
        self._initial = seconds
        self._remaining = seconds
        self._start_btn.setText("Start")
        self._update_display()

    def _toggle(self):
        if self._remaining <= 0:
            return     # nothing queued; require a preset first
        self._running = not self._running
        if self._running:
            self._timer.start(1000)
            self._start_btn.setText("Pause")
        else:
            self._timer.stop()
            self._start_btn.setText("Start")

    def _reset(self):
        self._timer.stop()
        self._running = False
        self._remaining = self._initial
        self._start_btn.setText("Start")
        self._update_display()

    def _tick(self):
        self._remaining -= 1
        if self._remaining <= 0:
            self._remaining = 0
            self._timer.stop()
            self._running = False
            self._start_btn.setText("Start")
            QApplication.beep()
            _notify("Time's up ⏰")
        self._update_display()

    def _update_display(self):
        m, s = divmod(self._remaining, 60)
        self._display.setText(f"{m:02d}:{s:02d}")
