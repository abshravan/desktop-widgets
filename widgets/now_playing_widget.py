# now_playing_widget.py — Current media via MPRIS (playerctl).
# Works with Spotify, browser tabs, Rhythmbox, anything that exposes MPRIS.
#
# Requires `playerctl` installed:  sudo apt install playerctl

import shutil
import subprocess
from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
)
from PyQt6.QtCore import Qt, QTimer
from styles.theme import CARD_STYLE, SECTION_LABEL_STYLE, COLORS


def _playerctl(*args: str) -> str | None:
    """Run a playerctl command; return stdout or None on any failure."""
    if not shutil.which("playerctl"):
        return None
    try:
        out = subprocess.run(
            ["playerctl", *args],
            capture_output=True, text=True, timeout=2,
        )
        return out.stdout.strip() if out.returncode == 0 else None
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return None


class NowPlayingWidget(QFrame):
    REFRESH_MS = 2000

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(CARD_STYLE)
        self._build_ui()

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._refresh)
        self._timer.start(self.REFRESH_MS)
        self._refresh()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(6)

        section = QLabel("NOW PLAYING")
        section.setStyleSheet(SECTION_LABEL_STYLE)
        layout.addWidget(section)

        self._title_lbl = QLabel("—")
        self._title_lbl.setWordWrap(True)
        self._title_lbl.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['text_primary']};
                font-size: 13px;
                font-weight: 600;
            }}
        """)
        layout.addWidget(self._title_lbl)

        self._artist_lbl = QLabel("")
        self._artist_lbl.setStyleSheet(f"QLabel {{ color: {COLORS['text_secondary']}; font-size: 11px; }}")
        self._artist_lbl.setWordWrap(True)
        layout.addWidget(self._artist_lbl)

        self._source_lbl = QLabel("")
        self._source_lbl.setStyleSheet(f"QLabel {{ color: {COLORS['text_muted']}; font-size: 10px; }}")
        layout.addWidget(self._source_lbl)

        # Transport controls
        ctrl = QHBoxLayout()
        ctrl.setSpacing(6)
        ctrl.addStretch()

        self._prev_btn  = self._make_btn("⏮", lambda: _playerctl("previous"))
        self._play_btn  = self._make_btn("⏯", lambda: _playerctl("play-pause"))
        self._next_btn  = self._make_btn("⏭", lambda: _playerctl("next"))

        ctrl.addWidget(self._prev_btn)
        ctrl.addWidget(self._play_btn)
        ctrl.addWidget(self._next_btn)
        ctrl.addStretch()
        layout.addLayout(ctrl)

    def _make_btn(self, glyph: str, action) -> QPushButton:
        btn = QPushButton(glyph)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setFixedSize(34, 28)
        btn.setStyleSheet(f"""
            QPushButton {{
                background: {COLORS['bg_card_inner']};
                color: {COLORS['text_primary']};
                border: none;
                border-radius: 6px;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background: {COLORS['accent']};
                color: white;
            }}
        """)
        # Run the action then immediately refresh display
        btn.clicked.connect(lambda: (action(), self._refresh()))
        return btn

    def _refresh(self):
        if not shutil.which("playerctl"):
            self._title_lbl.setText("playerctl not installed")
            self._artist_lbl.setText("sudo apt install playerctl")
            self._source_lbl.setText("")
            for btn in (self._prev_btn, self._play_btn, self._next_btn):
                btn.setEnabled(False)
            return

        status = _playerctl("status")
        if not status or status in ("No players found", ""):
            self._title_lbl.setText("Nothing playing")
            self._artist_lbl.setText("")
            self._source_lbl.setText("")
            return

        title  = _playerctl("metadata", "title")  or ""
        artist = _playerctl("metadata", "artist") or ""
        source = _playerctl("metadata", "--format", "{{playerName}}") or ""

        self._title_lbl.setText(title or "Untitled")
        self._artist_lbl.setText(artist)
        prefix = "▶ " if status == "Playing" else "⏸ "
        self._source_lbl.setText(prefix + source.capitalize() if source else prefix.strip())
