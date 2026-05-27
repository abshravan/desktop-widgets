# calculator_widget.py — Basic 4-function calculator with safe AST-based eval.
# Supports + − × ÷, parentheses, decimals, and a keyboard-accessible display.

import ast
import operator
from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QGridLayout, QLabel, QPushButton, QHBoxLayout,
)
from PyQt6.QtCore import Qt
from styles.theme import CARD_STYLE, SECTION_LABEL_STYLE, COLORS

# Map AST node types → operators. Anything outside this set is rejected.
_OPS = {
    ast.Add:      operator.add,
    ast.Sub:      operator.sub,
    ast.Mult:     operator.mul,
    ast.Div:      operator.truediv,
    ast.USub:     operator.neg,
    ast.UAdd:     operator.pos,
    ast.Mod:      operator.mod,
    ast.Pow:      operator.pow,
}


def _safe_eval(expr: str) -> float:
    """Evaluate a calculator expression without using `eval`."""
    node = ast.parse(expr, mode="eval").body
    return _eval_node(node)


def _eval_node(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval_node(node.left), _eval_node(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval_node(node.operand))
    raise ValueError("unsupported")


class CalculatorWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(CARD_STYLE)
        self._expr = ""
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 14)
        layout.setSpacing(8)

        section = QLabel("CALCULATOR")
        section.setStyleSheet(SECTION_LABEL_STYLE)
        layout.addWidget(section)

        # Display
        self._display = QLabel("0")
        self._display.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self._display.setStyleSheet(f"""
            QLabel {{
                background: {COLORS['bg_card_inner']};
                color: {COLORS['text_primary']};
                border-radius: 8px;
                padding: 10px 12px;
                font-size: 20px;
                font-weight: 500;
                min-height: 28px;
            }}
        """)
        layout.addWidget(self._display)

        # Number/operator pad
        grid = QGridLayout()
        grid.setSpacing(6)
        layout.addLayout(grid)

        rows = [
            [("C", "clr"), ("(", "("), (")", ")"), ("÷", "/")],
            [("7", "7"),   ("8", "8"), ("9", "9"), ("×", "*")],
            [("4", "4"),   ("5", "5"), ("6", "6"), ("−", "-")],
            [("1", "1"),   ("2", "2"), ("3", "3"), ("+", "+")],
            [("0", "0"),   (".", "."), ("⌫", "back"), ("=", "eq")],
        ]
        for r, row in enumerate(rows):
            for c, (label, key) in enumerate(row):
                grid.addWidget(self._make_btn(label, key), r, c)

    def _make_btn(self, label: str, key: str) -> QPushButton:
        btn = QPushButton(label)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setFixedHeight(34)
        # Colour-code special buttons
        if key in ("eq",):
            bg, fg = COLORS["accent"], "white"
        elif key in ("clr", "back"):
            bg, fg = COLORS["accent_red"], "white"
        elif key in ("+", "-", "*", "/", "(", ")"):
            bg, fg = COLORS["bg_card_inner"], COLORS["accent"]
        else:
            bg, fg = COLORS["bg_card_inner"], COLORS["text_primary"]
        btn.setStyleSheet(f"""
            QPushButton {{
                background: {bg};
                color: {fg};
                border: none;
                border-radius: 6px;
                font-size: 14px;
                font-weight: 600;
            }}
            QPushButton:hover {{ background: {COLORS['border']}; }}
            QPushButton:pressed {{ background: {COLORS['accent']}; color: white; }}
        """)
        btn.clicked.connect(lambda: self._on_key(key))
        return btn

    def _on_key(self, key: str):
        if key == "clr":
            self._expr = ""
        elif key == "back":
            self._expr = self._expr[:-1]
        elif key == "eq":
            self._evaluate()
            return
        else:
            self._expr += key
        self._refresh()

    def _evaluate(self):
        try:
            result = _safe_eval(self._expr)
            # Pretty integer display when applicable
            if isinstance(result, float) and result.is_integer():
                result = int(result)
            self._expr = str(result)
        except Exception:
            self._display.setText("Error")
            self._expr = ""
            return
        self._refresh()

    def _refresh(self):
        # Prettify operators for display
        display = (
            self._expr.replace("*", "×").replace("/", "÷").replace("-", "−")
            if self._expr else "0"
        )
        self._display.setText(display)
