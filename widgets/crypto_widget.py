# crypto_widget.py — Live cryptocurrency prices from CoinGecko.
# Edit CRYPTO_COINS in config.py to track different coins.

from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt, QTimer
from styles.theme import CARD_STYLE, SECTION_LABEL_STYLE, COLORS
from services.crypto_service import CryptoWorker
import config


DEFAULT_COINS = [
    ("bitcoin",  "BTC"),
    ("ethereum", "ETH"),
    ("solana",   "SOL"),
]


class CryptoWidget(QFrame):
    REFRESH_MS = 120_000  # 2 minutes — CoinGecko free tier rate-limit friendly

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(CARD_STYLE)
        self._coins = getattr(config, "CRYPTO_COINS", DEFAULT_COINS)
        self._worker = None
        self._rows: dict[str, tuple[QLabel, QLabel]] = {}
        self._build_ui()

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._fetch)
        self._timer.start(self.REFRESH_MS)
        self._fetch()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(6)

        section = QLabel("CRYPTO")
        section.setStyleSheet(SECTION_LABEL_STYLE)
        layout.addWidget(section)

        for coin_id, ticker in self._coins:
            row = QHBoxLayout()
            row.setSpacing(8)

            sym = QLabel(ticker)
            sym.setStyleSheet(f"QLabel {{ color: {COLORS['text_primary']}; font-size: 12px; font-weight: 700; }}")
            sym.setFixedWidth(40)
            row.addWidget(sym)

            price = QLabel("—")
            price.setStyleSheet(f"QLabel {{ color: {COLORS['text_primary']}; font-size: 13px; font-weight: 500; }}")
            price.setAlignment(Qt.AlignmentFlag.AlignRight)
            row.addWidget(price, 1)

            change = QLabel("")
            change.setStyleSheet(f"QLabel {{ color: {COLORS['text_muted']}; font-size: 11px; }}")
            change.setFixedWidth(56)
            change.setAlignment(Qt.AlignmentFlag.AlignRight)
            row.addWidget(change)

            self._rows[coin_id] = (price, change)
            layout.addLayout(row)

        self._error_lbl = QLabel("")
        self._error_lbl.setStyleSheet(f"QLabel {{ color: {COLORS['accent_red']}; font-size: 10px; }}")
        self._error_lbl.setWordWrap(True)
        layout.addWidget(self._error_lbl)

    def _fetch(self):
        if self._worker and self._worker.isRunning():
            return
        coin_ids = [coin_id for coin_id, _ in self._coins]
        self._worker = CryptoWorker(coin_ids)
        self._worker.data_ready.connect(self._on_data)
        self._worker.error.connect(self._on_error)
        self._worker.start()

    def _on_data(self, items: list):
        self._error_lbl.setText("")
        for item in items:
            row = self._rows.get(item["id"])
            if not row:
                continue
            price_lbl, change_lbl = row
            price = item["price"]
            change = item["change"]

            # Format price: large coins with no decimals, small ones with up to 4
            if price >= 100:
                price_str = f"${price:,.0f}"
            elif price >= 1:
                price_str = f"${price:,.2f}"
            else:
                price_str = f"${price:.4f}"
            price_lbl.setText(price_str)

            color = COLORS["accent_green"] if change >= 0 else COLORS["accent_red"]
            arrow = "▲" if change >= 0 else "▼"
            change_lbl.setText(f"{arrow} {abs(change):.2f}%")
            change_lbl.setStyleSheet(f"QLabel {{ color: {color}; font-size: 11px; font-weight: 600; }}")

    def _on_error(self, msg: str):
        self._error_lbl.setText(f"⚠ {msg}")
