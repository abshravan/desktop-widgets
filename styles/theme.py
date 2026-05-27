# theme.py — macOS Sonoma dark-mode inspired color system.

COLORS = {
    # Panel backgrounds (matches macOS grouped UI layers)
    "bg_primary":    "#1c1c1e",   # system background dark
    "bg_secondary":  "#2c2c2e",   # secondary system bg (card fill)
    "bg_card":       "#2c2c2e",
    "bg_card_inner": "#3a3a3c",   # inset elements inside cards

    # macOS dark-mode system palette
    "accent":        "#0a84ff",   # system blue
    "accent_green":  "#30d158",   # system green
    "accent_yellow": "#ffd60a",   # system yellow
    "accent_red":    "#ff453a",   # system red (also traffic light)
    "accent_orange": "#ff9f0a",   # system orange

    # Typography — matches SF Pro hierarchy
    "text_primary":   "#ffffff",
    "text_secondary": "#98989e",  # ≈ rgba(235,235,245, 0.6)
    "text_muted":     "#48484a",  # ≈ rgba(235,235,245, 0.18)

    # Chrome
    "border":         "#38383a",  # very subtle separator / card border
    "separator":      "#38383a",
    "title_bar":      "#1c1c1e",
}

FONTS = {
    "family":   "SF Pro Display, Inter, Helvetica Neue, sans-serif",
    "size_xl":  "26px",
    "size_lg":  "16px",
    "size_md":  "13px",
    "size_sm":  "11px",
    "size_xs":  "10px",
}

# ── Qt stylesheets ────────────────────────────────────────────────────────────

CARD_STYLE = f"""
    QFrame {{
        background-color: {COLORS['bg_card']};
        border-radius: 14px;
        border: 1px solid {COLORS['border']};
    }}
"""

SECTION_LABEL_STYLE = f"""
    QLabel {{
        color: {COLORS['text_muted']};
        font-size: {FONTS['size_xs']};
        font-weight: 600;
        letter-spacing: 1.2px;
    }}
"""

CLOCK_TIME_STYLE = f"""
    QLabel {{
        color: {COLORS['text_primary']};
        font-size: {FONTS['size_xl']};
        font-weight: 600;
        letter-spacing: 1px;
    }}
"""

CLOCK_DATE_STYLE = f"""
    QLabel {{
        color: {COLORS['text_secondary']};
        font-size: {FONTS['size_sm']};
        font-weight: 400;
    }}
"""

BATTERY_VALUE_STYLE = f"""
    QLabel {{
        color: {COLORS['text_primary']};
        font-size: {FONTS['size_lg']};
        font-weight: 600;
    }}
"""

BATTERY_STATUS_STYLE = f"""
    QLabel {{
        color: {COLORS['text_secondary']};
        font-size: {FONTS['size_sm']};
    }}
"""

WEATHER_TEMP_STYLE = f"""
    QLabel {{
        color: {COLORS['text_primary']};
        font-size: {FONTS['size_xl']};
        font-weight: 700;
    }}
"""

WEATHER_CITY_STYLE = f"""
    QLabel {{
        color: {COLORS['accent']};
        font-size: {FONTS['size_md']};
        font-weight: 600;
    }}
"""

WEATHER_DESC_STYLE = f"""
    QLabel {{
        color: {COLORS['text_secondary']};
        font-size: {FONTS['size_sm']};
    }}
"""

HEADLINE_BUTTON_STYLE = f"""
    QPushButton {{
        color: {COLORS['text_primary']};
        background: transparent;
        border: none;
        text-align: left;
        font-size: {FONTS['size_sm']};
        padding: 5px 2px;
        font-weight: 400;
    }}
    QPushButton:hover {{
        color: {COLORS['accent']};
    }}
"""

SEPARATOR_STYLE = f"""
    QFrame {{
        background: {COLORS['separator']};
        border: none;
        max-height: 1px;
    }}
"""

SCROLLBAR_STYLE = f"""
    QScrollBar:vertical {{
        background: transparent;
        width: 4px;
        margin: 0;
    }}
    QScrollBar::handle:vertical {{
        background: {COLORS['bg_card_inner']};
        border-radius: 2px;
        min-height: 20px;
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0;
    }}
"""
