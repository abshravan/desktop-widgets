#!/usr/bin/env python3
# main.py — Application entry point.
#
# Wayland note: dragging a frameless window requires the compositor to
# honour startSystemMove(). GNOME on Wayland supports this; some others
# don't. If drag breaks on your setup, force the X11 backend:
#
#     QT_QPA_PLATFORM=xcb python3 main.py

import os
import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from ui.main_window import MainWindow


def main():
    # Quick session-type log so the user can see what they're on
    session = os.environ.get("XDG_SESSION_TYPE", "unknown")
    print(f"[startup] session type: {session}")
    print(f"[startup] Qt platform: {os.environ.get('QT_QPA_PLATFORM', '(auto)')}")

    app = QApplication(sys.argv)

    app.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    font = QFont("Inter")
    font.setStyleHint(QFont.StyleHint.SansSerif)
    font.setPixelSize(13)
    app.setFont(font)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
