#!/usr/bin/env python3
# main.py — Application entry point.
#
# Shows a Rainmeter-style launcher.  The user toggles individual widgets
# (clock, weather, todo, etc.) which then appear as separate floating
# windows on the desktop.  Each widget remembers its position and
# visibility across restarts.
#
# Wayland note: dragging frameless windows requires the compositor to
# honour startSystemMove().  If your compositor doesn't, force X11:
#
#     QT_QPA_PLATFORM=xcb python3 main.py

import os
import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from ui.launcher import Launcher


def main():
    print(f"[startup] session type: {os.environ.get('XDG_SESSION_TYPE', 'unknown')}")
    print(f"[startup] Qt platform: {os.environ.get('QT_QPA_PLATFORM', '(auto)')}")

    app = QApplication(sys.argv)
    # Quit only when explicitly told (not when last visible widget closes).
    app.setQuitOnLastWindowClosed(False)

    app.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    font = QFont("Inter")
    font.setStyleHint(QFont.StyleHint.SansSerif)
    font.setPixelSize(13)
    app.setFont(font)

    launcher = Launcher()
    launcher.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
