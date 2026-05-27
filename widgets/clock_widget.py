# clock_widget.py — Nothing OS-inspired analogue clock card.
# Dot-matrix hour marks, red second hand, minimal white hour/minute hands.
# The face is painted manually with QPainter for full control.

from datetime import datetime
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel, QWidget
from PyQt6.QtCore import Qt, QTimer, QPointF, QRectF
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QFont
from styles.theme import (
    CARD_STYLE, SECTION_LABEL_STYLE, CLOCK_DATE_STYLE, COLORS,
)


class ClockFace(QWidget):
    """Pure-paint analogue face. No layout children — just QPainter output."""

    # Visual tokens — tweak here to retheme the face only.
    BG_COLOR          = QColor("#0a0d14")
    OUTER_RING_COLOR  = QColor("#1f2430")
    DOT_COLOR_MINOR   = QColor("#3d4555")
    DOT_COLOR_MAJOR   = QColor("#e6edf3")
    HAND_HOUR_COLOR   = QColor("#e6edf3")
    HAND_MINUTE_COLOR = QColor("#e6edf3")
    HAND_SECOND_COLOR = QColor("#ff4d4d")   # Nothing-style red accent
    CENTER_COLOR      = QColor("#ff4d4d")

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(180, 180)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._now = datetime.now()

    def set_time(self, t: datetime):
        self._now = t
        self.update()

    def paintEvent(self, event):
        side = min(self.width(), self.height())
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Move origin to centre and normalise to a 200x200 coordinate space
        p.translate(self.width() / 2, self.height() / 2)
        p.scale(side / 200.0, side / 200.0)

        self._draw_face(p)
        self._draw_ticks(p)
        self._draw_hands(p)
        self._draw_centre(p)
        p.end()

    # ── Face background + outer ring ─────────────────────────────────────────
    def _draw_face(self, p: QPainter):
        # Filled inner disc
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(self.BG_COLOR))
        p.drawEllipse(QPointF(0, 0), 95, 95)

        # Thin outer ring
        pen = QPen(self.OUTER_RING_COLOR)
        pen.setWidthF(1.2)
        p.setPen(pen)
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawEllipse(QPointF(0, 0), 92, 92)

    # ── Dot-matrix hour markers ──────────────────────────────────────────────
    def _draw_ticks(self, p: QPainter):
        # 60 minor dots around the circumference, every 6° = 1 minute
        for i in range(60):
            p.save()
            p.rotate(i * 6)
            is_major = (i % 5 == 0)
            radius = 2.4 if is_major else 1.0
            color = self.DOT_COLOR_MAJOR if is_major else self.DOT_COLOR_MINOR
            p.setBrush(QBrush(color))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawEllipse(QPointF(0, -82), radius, radius)
            p.restore()

    # ── Hour, minute, second hands ───────────────────────────────────────────
    def _draw_hands(self, p: QPainter):
        h = self._now.hour % 12
        m = self._now.minute
        s = self._now.second

        # Hour hand: thick & short, white. Includes minute fraction for smoothness.
        p.save()
        p.rotate((h + m / 60.0) * 30)
        pen = QPen(self.HAND_HOUR_COLOR)
        pen.setWidthF(3.5)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        p.setPen(pen)
        p.drawLine(QPointF(0, 6), QPointF(0, -45))
        p.restore()

        # Minute hand: thinner & longer
        p.save()
        p.rotate((m + s / 60.0) * 6)
        pen = QPen(self.HAND_MINUTE_COLOR)
        pen.setWidthF(2.2)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        p.setPen(pen)
        p.drawLine(QPointF(0, 8), QPointF(0, -70))
        p.restore()

        # Second hand: thin red, extends past centre with a tail
        p.save()
        p.rotate(s * 6)
        pen = QPen(self.HAND_SECOND_COLOR)
        pen.setWidthF(1.2)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        p.setPen(pen)
        p.drawLine(QPointF(0, 16), QPointF(0, -78))
        p.restore()

    # ── Centre pivot ─────────────────────────────────────────────────────────
    def _draw_centre(self, p: QPainter):
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(self.CENTER_COLOR))
        p.drawEllipse(QPointF(0, 0), 3.2, 3.2)
        p.setBrush(QBrush(self.BG_COLOR))
        p.drawEllipse(QPointF(0, 0), 1.2, 1.2)


class ClockWidget(QFrame):
    """Card containing the analogue face plus the date underneath."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(CARD_STYLE)
        self._build_ui()

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(1000)
        self._tick()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 16)
        layout.setSpacing(8)

        section = QLabel("CLOCK")
        section.setStyleSheet(SECTION_LABEL_STYLE)
        layout.addWidget(section)

        # Analogue face — centred horizontally inside the card
        self._face = ClockFace()
        layout.addWidget(self._face, alignment=Qt.AlignmentFlag.AlignHCenter)

        # Digital readout (small) + date
        self._digital_label = QLabel()
        self._digital_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['text_primary']};
                font-size: 16px;
                font-weight: 600;
                letter-spacing: 2px;
            }}
        """)
        self._digital_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(self._digital_label)

        self._date_label = QLabel()
        self._date_label.setStyleSheet(CLOCK_DATE_STYLE)
        self._date_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(self._date_label)

    def _tick(self):
        now = datetime.now()
        self._face.set_time(now)
        self._digital_label.setText(now.strftime("%H:%M:%S"))
        self._date_label.setText(now.strftime("%A, %B %-d %Y"))
