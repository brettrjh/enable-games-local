from __future__ import annotations

from typing import Iterable

from PyQt6 import QtCore, QtWidgets

WINDOW_SIZE = QtCore.QSize(900, 700)

BUTTON_HEIGHT = 44
BUTTON_RADIUS = 10

SPACING_SM = 8
SPACING_MD = 12
SPACING_LG = 20

FONT_FAMILY = "Segoe UI"
FONT_SIZE_BASE = 11
FONT_SIZE_TITLE = 22

COLORS = {
    "bg": "#0F172A",
    "panel": "#111827",
    "panel_alt": "#1F2937",
    "text": "#F8FAFC",
    "text_muted": "#94A3B8",
    "border": "#334155",
    "primary": "#2563EB",
    "primary_hover": "#1D4ED8",
    "secondary": "#334155",
    "secondary_hover": "#475569",
    "back": "#374151",
    "back_hover": "#4B5563",
}

APP_STYLESHEET = f"""
QWidget {{
    background-color: {COLORS['bg']};
    color: {COLORS['text']};
    font-family: {FONT_FAMILY};
    font-size: {FONT_SIZE_BASE}pt;
}}

QFrame#frameCard,
QFrame#frameContent {{
    background-color: {COLORS['panel']};
    border: 1px solid {COLORS['border']};
    border-radius: 14px;
}}

QLabel#titleLabel,
QLabel#lblTitle {{
    font-size: {FONT_SIZE_TITLE}pt;
    font-weight: 700;
}}

QLabel#subtitleLabel,
QLabel#lblSubtitle {{
    color: {COLORS['text_muted']};
}}

QPushButton {{
    min-height: {BUTTON_HEIGHT}px;
    border-radius: {BUTTON_RADIUS}px;
    border: 1px solid {COLORS['border']};
    background-color: {COLORS['panel_alt']};
    color: {COLORS['text']};
    padding: 8px 14px;
    font-weight: 600;
}}

QPushButton:hover {{
    background-color: {COLORS['secondary_hover']};
}}

QPushButton:disabled {{
    color: {COLORS['text_muted']};
    background-color: {COLORS['panel']};
}}

QPushButton[class~="primary"] {{
    background-color: {COLORS['primary']};
    border-color: {COLORS['primary']};
}}

QPushButton[class~="primary"]:hover {{
    background-color: {COLORS['primary_hover']};
    border-color: {COLORS['primary_hover']};
}}

QPushButton[class~="secondary"] {{
    background-color: {COLORS['secondary']};
}}

QPushButton[class~="secondary"]:hover {{
    background-color: {COLORS['secondary_hover']};
}}

QPushButton[class~="back"] {{
    background-color: {COLORS['back']};
    border-color: {COLORS['back']};
}}

QPushButton[class~="back"]:hover {{
    background-color: {COLORS['back_hover']};
    border-color: {COLORS['back_hover']};
}}
"""


def set_button_variant(button: QtWidgets.QPushButton | None, variant: str) -> None:
    if button is None:
        return

    existing = button.property("class") or ""
    tokens = [token for token in str(existing).split() if token]
    if variant not in tokens:
        tokens.append(variant)
    button.setProperty("class", " ".join(tokens))
    button.style().unpolish(button)
    button.style().polish(button)


def apply_standard_control_sizing(root: QtWidgets.QWidget, controls: Iterable[str] | None = None) -> None:
    if controls is None:
        buttons = root.findChildren(QtWidgets.QPushButton)
    else:
        buttons = []
        for name in controls:
            button = root.findChild(QtWidgets.QPushButton, name)
            if button is not None:
                buttons.append(button)

    for button in buttons:
        min_size = button.minimumSize()
        button.setMinimumHeight(max(min_size.height(), BUTTON_HEIGHT))
        if button.maximumHeight() > 0 and button.maximumHeight() < BUTTON_HEIGHT:
            button.setMaximumHeight(BUTTON_HEIGHT)
