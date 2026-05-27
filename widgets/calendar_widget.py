# calendar_widget.py — Compact month-view calendar with today highlighted.
# Built on QCalendarWidget but heavily restyled to match the dark theme.

from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel, QCalendarWidget
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QTextCharFormat, QColor, QFont
from styles.theme import CARD_STYLE, SECTION_LABEL_STYLE, COLORS


class CalendarWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(CARD_STYLE)
        self._build_ui()
        self._apply_today_highlight()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 14)
        layout.setSpacing(6)

        section = QLabel("CALENDAR")
        section.setStyleSheet(SECTION_LABEL_STYLE)
        layout.addWidget(section)

        self._cal = QCalendarWidget()
        self._cal.setGridVisible(False)
        self._cal.setVerticalHeaderFormat(QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)
        self._cal.setNavigationBarVisible(True)
        self._cal.setFirstDayOfWeek(Qt.DayOfWeek.Monday)
        self._cal.setSelectedDate(QDate.currentDate())

        # Style the QCalendarWidget subcomponents
        self._cal.setStyleSheet(f"""
            QCalendarWidget QWidget {{
                background: transparent;
                color: {COLORS['text_primary']};
            }}
            /* Top navigation bar */
            QCalendarWidget QWidget#qt_calendar_navigationbar {{
                background: {COLORS['bg_card_inner']};
                border-radius: 6px;
            }}
            QCalendarWidget QToolButton {{
                color: {COLORS['text_primary']};
                background: transparent;
                border: none;
                margin: 4px;
                padding: 4px 6px;
                font-size: 12px;
                font-weight: 600;
            }}
            QCalendarWidget QToolButton:hover {{ color: {COLORS['accent']}; }}
            QCalendarWidget QMenu {{
                background: {COLORS['bg_card']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
            }}
            QCalendarWidget QSpinBox {{
                background: {COLORS['bg_card_inner']};
                color: {COLORS['text_primary']};
                border: none;
                border-radius: 4px;
                padding: 2px;
            }}
            /* Day grid */
            QCalendarWidget QAbstractItemView {{
                background: transparent;
                selection-background-color: {COLORS['accent']};
                selection-color: white;
                outline: none;
                font-size: 11px;
            }}
            /* Disabled (other-month) days */
            QCalendarWidget QAbstractItemView:disabled {{
                color: {COLORS['text_muted']};
            }}
        """)
        layout.addWidget(self._cal)

    def _apply_today_highlight(self):
        # Special format for today's cell: accent background, bold white
        fmt = QTextCharFormat()
        fmt.setBackground(QColor(COLORS["accent"]))
        fmt.setForeground(QColor("white"))
        fmt.setFontWeight(QFont.Weight.Bold)
        self._cal.setDateTextFormat(QDate.currentDate(), fmt)

        # Weekend headers: subtle grey instead of red
        weekend_fmt = QTextCharFormat()
        weekend_fmt.setForeground(QColor(COLORS["text_secondary"]))
        self._cal.setWeekdayTextFormat(Qt.DayOfWeek.Saturday, weekend_fmt)
        self._cal.setWeekdayTextFormat(Qt.DayOfWeek.Sunday, weekend_fmt)
