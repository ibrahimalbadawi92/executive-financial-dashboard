# -*- coding: utf-8 -*-
"""
Number/currency formatting shared by every page. Intelligent SAR formatting
(SAR 35.6M / SAR 850K) for headline values; full precision is used in chart
hover tooltips (never truncated there).
"""
import pandas as pd

from src.translations import t


def format_money(value, lang: str = "en", decimals: int = 1) -> str:
    """
    Intelligent compact currency formatting.
    English: SAR 12.4M / SAR 850K / SAR 420 (Latin M/K abbreviations).
    Arabic: localized units, never English M/K abbreviations -
    12.4 مليون ر.س / 850 ألف ر.س / 420 ر.س.
    """
    if value is None or pd.isna(value):
        return "—"
    sign = "-" if value < 0 else ""
    v = abs(value)

    if lang == "ar":
        if v >= 1_000_000:
            s = f"{v/1_000_000:.{decimals}f}"
            return f"{sign}{s} مليون ر.س"
        elif v >= 1_000:
            s = f"{v/1_000:.0f}"
            return f"{sign}{s} ألف ر.س"
        else:
            s = f"{v:,.0f}"
            return f"{sign}{s} ر.س"

    cur = t("currency_code", lang)
    if v >= 1_000_000:
        s = f"{v/1_000_000:.{decimals}f}M"
    elif v >= 1_000:
        s = f"{v/1_000:.0f}K"
    else:
        s = f"{v:,.0f}"
    return f"{cur} {sign}{s}"


def format_money_full(value, lang: str = "en") -> str:
    """Full-precision currency value, for hover tooltips / tables."""
    if value is None or pd.isna(value):
        return "—"
    cur = t("currency_code", lang)
    s = f"{value:,.2f}"
    return f"{cur} {s}" if lang == "en" else f"{s} {cur}"


def format_pct(value, decimals: int = 1) -> str:
    if value is None or pd.isna(value):
        return "—"
    return f"{value:,.{decimals}f}%"


def format_int(value) -> str:
    if value is None or pd.isna(value):
        return "—"
    return f"{value:,.0f}"


def format_delta_pct(value, decimals: int = 1) -> str:
    """Signed percentage for YoY deltas, e.g. '+2.8%' / '-34.0%'."""
    if value is None or pd.isna(value):
        return "—"
    sign = "+" if value >= 0 else ""
    return f"{sign}{value:,.{decimals}f}%"


def bidi_isolate(text: str) -> str:
    """
    Wraps an LTR numeric run (e.g. a year range like '2022-2025') in <bdi
    dir="ltr"> so it stays chronologically ordered when embedded inside RTL
    Arabic text - the Unicode bidi algorithm can otherwise visually reverse a
    bare 'YYYY-YYYY' sequence sitting inside an RTL block. Only meaningful
    where the caller renders via unsafe_allow_html.
    """
    return f'<bdi dir="ltr">{text}</bdi>'


def year_range_text(start, end, lang: str) -> str:
    """Chronologically-safe 'start-end' (en dash) label, bidi-isolated for Arabic."""
    if start == end:
        return str(start)
    plain = f"{start}–{end}"
    return bidi_isolate(plain) if lang == "ar" else plain
