# -*- coding: utf-8 -*-
"""
Small, generic numeric helpers shared by financial_metrics and validations.
No business logic lives here - only safe arithmetic primitives.
"""
import numpy as np
import pandas as pd


def safe_div(numerator, denominator):
    """Divide, returning NaN instead of raising/inf on a zero or missing denominator."""
    if denominator is None or pd.isna(denominator) or denominator == 0:
        return np.nan
    return numerator / denominator


def safe_pct(numerator, denominator):
    """Like safe_div but expressed as a percentage (0-100 scale)."""
    r = safe_div(numerator, denominator)
    return np.nan if pd.isna(r) else r * 100.0


def yoy_change(current, previous):
    """
    Returns (absolute_variance, pct_variance) for a Year-over-Year comparison.
    pct_variance is NaN when previous is zero/missing (division-by-zero safe).
    """
    if current is None or previous is None or pd.isna(current) or pd.isna(previous):
        return np.nan, np.nan
    abs_var = current - previous
    pct_var = safe_pct(abs_var, previous)
    return abs_var, pct_var


def round2(x):
    return np.nan if x is None or pd.isna(x) else round(float(x), 2)
