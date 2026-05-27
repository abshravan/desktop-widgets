# theme.py — All Qt stylesheets and color tokens in one place.
# Edit COLORS to re-skin the entire app without touching widget code.

COLORS = {
    "bg_primary":    "#0d1117",
    "bg_secondary":  "#161b22",
    "bg_card":       "#1c2333",
    "accent":        "#58a6ff",
    "accent_green":  "#3fb950",
    "accent_yellow": "#d29922",
    "accent_red":    "#f85149",
    "text_primary":  "#e6edf3",
    "text_secondary":"#8b949e",
    "text_muted":    "#484f58",
    "border":        "#30363d",
    "separator":     "#21262d",
}

FONTS = {
    "family": "Inter, SF Pro Display, Segoe UI, sans-serif",
    "size_xl":   "28px",
    "size_lg":   "16px",
    "size_md":   "13px",
    "size_sm":   "11px",
    "size_xs":   "10px",
}

MAIN_WINDOW_STYLE = f"""
    QWidget#MainWidget {{
        background-color: {COLORS['bg_primary']};
        border-radius: 16px;
        border: 1px solid {COLORS['border']};
    }}
"""

CARD_STYLE = f"""
    QFrame {{
        background-color: {COLORS['bg_card']};
        border-radius: 12px;
        border: 1px solid {COLORS['border']};
    }}
"""

SECTION_LABEL_STYLE = f"""
    QLabel {{
        color: {COLORS['text_muted']};
        font-size: {FONTS['size_xs']};
        font-weight: 600;
        letter-spacing: 1.5px;
        text-transform: uppercase;
    }}
"""

CLOCK_TIME_STYLE = f"""
    QLabel {{
        color: {COLORS['text_primary']};
        font-size: {FONTS['size_xl']};
        font-weight: 700;
        letter-spacing: -1px;
    }}
"""

CLOCK_DATE_STYLE = f"""
    QLabel {{
        color: {COLORS['text_secondary']};
        font-size: {FONTS['size_md']};
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
        padding: 6px 4px;
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
        background: {COLORS['border']};
        border-radius: 2px;
        min-height: 20px;
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0;
    }}
"""
