# pomodoro_widget.py — 25/5 work/break cycle with start, pause, reset.
# Sends a desktop notification (notify-send) when a phase ends.

import subprocess
from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
)
from PyQt6.QtCore import Qt, QTimer
from styles.theme import CARD_STYLE, SECTION_LABEL_STYLE, COLORS

WORK_SECS  = 25 * 60
BREAK_SECS = 5  * 60


def _notify(title: str, message: str):
    """Best-effort desktop notification via libnotify; ignored if missing."""
    try:
        subprocess.run(
            ["notify-send", "-a", "Desktop Widget", title, message],
            check=False, timeout=2,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass


class PomodoroWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(CARD_STYLE)
        self._phase = "work"            # "work" | "break"
        self._remaining = WORK_SECS
        self._running = False
        self._cycles = 0
        self._build_ui()

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._update_labels()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(6)

        head = QHBoxLayout()
        section = QLabel("POMODORO")
        section.setStyleSheet(SECTION_LABEL_STYLE)
        head.addWidget(section)
        head.addStretch()

        self._phase_lbl = QLabel()
        self._phase_lbl.setStyleSheet(f"QLabel {{ color: {COLORS['accent']}; font-size: 10px; font-weight: 600; }}")
        head.addWidget(self._phase_lbl)
        layout.addLayout(head)

        self._time_lbl = QLabel()
        self._time_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._time_lbl.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['text_primary']};
                font-size: 28px;
                font-weight: 600;
                letter-spacing: 2px;
            }}
        """)
        layout.addWidget(self._time_lbl)

        # Control row: start/pause and reset
        ctrl = QHBoxLayout()
        ctrl.setSpacing(6)

        self._start_btn = self._make_btn("Start", COLORS["accent"])
        self._start_btn.clicked.connect(self._toggle)
        ctrl.addWidget(self._start_btn)

        reset = self._make_btn("Reset", COLORS["bg_card_inner"])
        reset.clicked.connect(self._reset)
        ctrl.addWidget(reset)

        layout.addLayout(ctrl)

        self._cycle_lbl = QLabel("Cycles completed: 0")
        self._cycle_lbl.setStyleSheet(f"QLabel {{ color: {COLORS['text_muted']}; font-size: 10px; }}")
        self._cycle_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._cycle_lbl)

    def _make_btn(self, text: str, bg: str) -> QPushButton:
        btn = QPushButton(text)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setFixedHeight(26)
        btn.setStyleSheet(f"""
            QPushButton {{
                background: {bg};
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 11px;
                font-weight: 600;
            }}
            QPushButton:hover {{ background: {COLORS['accent_orange']}; }}
        """)
        return btn

    def _toggle(self):
        self._running = not self._running
        if self._running:
            self._timer.start(1000)
            self._start_btn.setText("Pause")
        else:
            self._timer.stop()
            self._start_btn.setText("Start")

    def _reset(self):
        self._running = False
        self._timer.stop()
        self._phase = "work"
        self._remaining = WORK_SECS
        self._start_btn.setText("Start")
        self._update_labels()

    def _tick(self):
        self._remaining -= 1
        if self._remaining <= 0:
            self._switch_phase()
        self._update_labels()

    def _switch_phase(self):
        if self._phase == "work":
            self._cycles += 1
            self._phase = "break"
            self._remaining = BREAK_SECS
            _notify("Pomodoro", "Work session complete — take a 5 min break ☕")
        else:
            self._phase = "work"
            self._remaining = WORK_SECS
            _notify("Pomodoro", "Break over — time to focus 🎯")

    def _update_labels(self):
        m, s = divmod(max(self._remaining, 0), 60)
        self._time_lbl.setText(f"{m:02d}:{s:02d}")
        self._phase_lbl.setText("FOCUS" if self._phase == "work" else "BREAK")
        self._cycle_lbl.setText(f"Cycles completed: {self._cycles}")
