# clock_widget.py — Analogue clock styled after the reference image.
#
# Visual spec (from reference):
#   - square dark card with rounded corners (no section label, no digital readout)
#   - circular face filling the card with a soft bezel highlight at top
#   - 12 rectangular hour markers; cardinal positions (12/3/6/9) are
#     longer and thicker than the rest
#   - day-of-week abbreviation (e.g. "WED") in the upper area
#   - day-of-month number in a small circular outline in the lower area
#   - slim white hour & minute hands, orange second hand with tail counterweight
#   - red-orange dot at the centre pivot

from datetime import datetime
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt, QTimer, QPointF, QRectF
from PyQt6.QtGui import (
    QPainter, QColor, QPen, QBrush, QFont, QLinearGradient, QRadialGradient,
)


class ClockFace(QWidget):
    """Pure-paint analogue face matching the reference image."""

    # ── Colour tokens ─────────────────────────────────────────────────────────
    CARD_BG          = QColor("#2c2c2e")    # outer card surface
    BEZEL_HIGHLIGHT  = QColor("#5a5a5e")    # top edge highlight of bezel
    BEZEL_SHADOW     = QColor("#1a1a1c")    # bottom edge shadow of bezel
    FACE_BG          = QColor("#1f1f21")    # inner face
    FACE_BG_INNER    = QColor("#161618")    # inner face center (subtle vignette)
    MARKER_COLOR     = QColor("#e8e8ea")    # hour-mark rectangles
    HAND_COLOR       = QColor("#ffffff")    # hour & minute hands
    SECOND_COLOR     = QColor("#ff7a1f")    # orange second hand (reference)
    CENTER_COLOR     = QColor("#ff7a1f")
    TEXT_COLOR       = QColor("#ffffff")
    DATE_RING_COLOR  = QColor("#7a7a7e")

    def __init__(self, size: int = 200, parent=None):
        super().__init__(parent)
        self._size = size
        self.setFixedSize(size, size)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._now = datetime.now()

    def set_time(self, t: datetime):
        self._now = t
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Work in a normalised 200-unit coordinate space, origin at centre
        side = min(self.width(), self.height())
        p.translate(self.width() / 2, self.height() / 2)
        p.scale(side / 200.0, side / 200.0)

        self._draw_card_background(p)
        self._draw_bezel(p)
        self._draw_face(p)
        self._draw_markers(p)
        self._draw_day_text(p)
        self._draw_date_badge(p)
        self._draw_hands(p)
        self._draw_centre(p)
        p.end()

    # ── Background card with rounded corners ──────────────────────────────────
    def _draw_card_background(self, p: QPainter):
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(self.CARD_BG))
        # The card fills the square — rounded corners drawn here
        p.drawRoundedRect(QRectF(-100, -100, 200, 200), 22, 22)

    # ── Bezel ring with top-highlight / bottom-shadow gradient ────────────────
    def _draw_bezel(self, p: QPainter):
        grad = QLinearGradient(0, -94, 0, 94)
        grad.setColorAt(0.0, self.BEZEL_HIGHLIGHT)
        grad.setColorAt(0.5, QColor("#2e2e30"))
        grad.setColorAt(1.0, self.BEZEL_SHADOW)
        p.setBrush(QBrush(grad))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(QPointF(0, 0), 94, 94)

    # ── Inner face with subtle radial vignette ────────────────────────────────
    def _draw_face(self, p: QPainter):
        grad = QRadialGradient(QPointF(0, 0), 88)
        grad.setColorAt(0.0, self.FACE_BG)
        grad.setColorAt(1.0, self.FACE_BG_INNER)
        p.setBrush(QBrush(grad))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(QPointF(0, 0), 88, 88)

    # ── Rectangular hour markers (cardinal ones longer) ───────────────────────
    def _draw_markers(self, p: QPainter):
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(self.MARKER_COLOR))
        for i in range(12):
            p.save()
            p.rotate(i * 30)
            is_cardinal = (i % 3 == 0)
            length = 12 if is_cardinal else 7
            width  = 3 if is_cardinal else 2
            # Rectangle sits just inside the bezel, pointing inward
            top = -84
            p.drawRoundedRect(
                QRectF(-width / 2, top, width, length),
                width / 2, width / 2,
            )
            p.restore()

    # ── Day-of-week abbreviation (e.g. "WED") near the top ────────────────────
    def _draw_day_text(self, p: QPainter):
        text = self._now.strftime("%a").upper()  # MON / TUE / ...
        font = QFont()
        font.setPixelSize(10)
        font.setBold(True)
        font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 1.2)
        p.setFont(font)
        p.setPen(QPen(self.TEXT_COLOR))
        # Centred horizontally; sits below the top markers
        rect = QRectF(-30, -50, 60, 14)
        p.drawText(rect, Qt.AlignmentFlag.AlignCenter, text)

    # ── Day-of-month inside a thin ring ───────────────────────────────────────
    def _draw_date_badge(self, p: QPainter):
        day = self._now.strftime("%d")
        if day.startswith("0"):
            day = day[1:]
        # Ring outline
        pen = QPen(self.DATE_RING_COLOR)
        pen.setWidthF(1.0)
        p.setPen(pen)
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawEllipse(QPointF(0, 36), 10, 10)
        # Number inside
        font = QFont()
        font.setPixelSize(11)
        font.setBold(True)
        p.setFont(font)
        p.setPen(QPen(self.TEXT_COLOR))
        rect = QRectF(-10, 27, 20, 18)
        p.drawText(rect, Qt.AlignmentFlag.AlignCenter, day)

    # ── Hour, minute, second hands ────────────────────────────────────────────
    def _draw_hands(self, p: QPainter):
        h = self._now.hour % 12
        m = self._now.minute
        s = self._now.second

        # Hour hand
        p.save()
        p.rotate((h + m / 60.0) * 30)
        pen = QPen(self.HAND_COLOR)
        pen.setWidthF(4.0)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        p.setPen(pen)
        p.drawLine(QPointF(0, 6), QPointF(0, -42))
        p.restore()

        # Minute hand
        p.save()
        p.rotate((m + s / 60.0) * 6)
        pen = QPen(self.HAND_COLOR)
        pen.setWidthF(2.8)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        p.setPen(pen)
        p.drawLine(QPointF(0, 8), QPointF(0, -64))
        p.restore()

        # Second hand — orange, with a counterweight tail
        p.save()
        p.rotate(s * 6)
        pen = QPen(self.SECOND_COLOR)
        pen.setWidthF(1.4)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        p.setPen(pen)
        p.drawLine(QPointF(0, 18), QPointF(0, -72))
        p.restore()

    # ── Centre pivot ──────────────────────────────────────────────────────────
    def _draw_centre(self, p: QPainter):
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(self.CENTER_COLOR))
        p.drawEllipse(QPointF(0, 0), 3.6, 3.6)
        # Tiny darker dot in centre for depth
        p.setBrush(QBrush(QColor("#1a1a1c")))
        p.drawEllipse(QPointF(0, 0), 1.2, 1.2)


class ClockWidget(QFrame):
    """
    Card containing only the analogue clock face.
    The face renders day-of-week and date internally, so the surrounding
    QFrame is invisible — the face IS the visual card.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        # Make the wrapper transparent — the face draws its own card surface
        self.setStyleSheet("QFrame { background: transparent; border: none; }")
        self._build_ui()

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(1000)
        self._tick()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._face = ClockFace(size=210)
        layout.addWidget(self._face, alignment=Qt.AlignmentFlag.AlignHCenter)

    def _tick(self):
        self._face.set_time(datetime.now())
