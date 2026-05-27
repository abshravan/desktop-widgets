# disk_widget.py — Per-mount disk usage with progress bars.
# Skips pseudo-filesystems (snap, loop, etc.) so only real volumes show.

import psutil
from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar,
)
from PyQt6.QtCore import Qt, QTimer
from styles.theme import CARD_STYLE, SECTION_LABEL_STYLE, COLORS

# Hide partitions whose mount point starts with one of these prefixes
SKIP_PREFIXES = ("/snap", "/var/lib/docker", "/proc", "/sys", "/run", "/dev")


def _human_size(num_bytes: float) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if num_bytes < 1024:
            return f"{num_bytes:.1f} {unit}"
        num_bytes /= 1024
    return f"{num_bytes:.1f} PB"


def _bar_color(percent: float) -> str:
    if percent >= 90:
        return COLORS["accent_red"]
    if percent >= 75:
        return COLORS["accent_yellow"]
    return COLORS["accent_green"]


class DiskWidget(QFrame):
    REFRESH_MS = 30_000

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(CARD_STYLE)
        self._rows: list[tuple[QLabel, QProgressBar, QLabel, str]] = []
        self._build_ui()

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._refresh)
        self._timer.start(self.REFRESH_MS)
        self._refresh()

    def _build_ui(self):
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(16, 14, 16, 14)
        self._layout.setSpacing(8)

        section = QLabel("DISK")
        section.setStyleSheet(SECTION_LABEL_STYLE)
        self._layout.addWidget(section)

        # Discover partitions once at startup; mounts rarely change
        for part in psutil.disk_partitions(all=False):
            if any(part.mountpoint.startswith(p) for p in SKIP_PREFIXES):
                continue
            self._add_row(part.mountpoint)

        if not self._rows:
            empty = QLabel("No mounted volumes")
            empty.setStyleSheet(f"QLabel {{ color: {COLORS['text_muted']}; font-size: 11px; }}")
            self._layout.addWidget(empty)

    def _add_row(self, mountpoint: str):
        # Two-line layout: name + percent on top, progress bar + size below
        top = QHBoxLayout()
        top.setSpacing(6)

        name = QLabel(mountpoint)
        name.setStyleSheet(f"QLabel {{ color: {COLORS['text_primary']}; font-size: 11px; font-weight: 600; }}")
        top.addWidget(name, 1)

        pct = QLabel("—")
        pct.setStyleSheet(f"QLabel {{ color: {COLORS['text_secondary']}; font-size: 10px; }}")
        pct.setAlignment(Qt.AlignmentFlag.AlignRight)
        top.addWidget(pct)

        bar = QProgressBar()
        bar.setRange(0, 100)
        bar.setTextVisible(False)
        bar.setFixedHeight(5)

        size_lbl = QLabel("")
        size_lbl.setStyleSheet(f"QLabel {{ color: {COLORS['text_muted']}; font-size: 10px; }}")

        wrapper = QVBoxLayout()
        wrapper.setSpacing(2)
        wrapper.addLayout(top)
        wrapper.addWidget(bar)
        wrapper.addWidget(size_lbl)
        self._layout.addLayout(wrapper)

        self._rows.append((pct, bar, size_lbl, mountpoint))

    def _refresh(self):
        for pct_lbl, bar, size_lbl, mountpoint in self._rows:
            try:
                u = psutil.disk_usage(mountpoint)
            except (PermissionError, OSError):
                pct_lbl.setText("?")
                continue
            pct_lbl.setText(f"{u.percent:.0f}%")
            bar.setValue(int(u.percent))
            color = _bar_color(u.percent)
            bar.setStyleSheet(f"""
                QProgressBar {{
                    background: {COLORS['bg_secondary']};
                    border-radius: 2.5px;
                    border: none;
                }}
                QProgressBar::chunk {{
                    background: {color};
                    border-radius: 2.5px;
                }}
            """)
            size_lbl.setText(f"{_human_size(u.used)} of {_human_size(u.total)}")
