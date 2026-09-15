# -*- coding: utf-8 -*-
"""
Reads the source workbook. Read-only - never writes to SOURCE_WORKBOOK.

Kept free of Streamlit so it can be unit-tested standalone; app.py (Phase 3)
will wrap load_raw_sheets() with st.cache_data so the workbook is parsed once
per session instead of on every UI interaction.
"""
import pandas as pd

import config


def _strip_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Several sheets/columns carry trailing whitespace in the source file
    (e.g. 'الارباح ', 'السنه ', 'اسم المورد ', 'العملة الأجنبية ') - strip
    programmatically rather than special-casing each one."""
    df = df.copy()
    df.columns = [c.strip() if isinstance(c, str) else c for c in df.columns]
    return df


EXPECTED_SHEETS = {
    config.SHEET_SALES,
    config.SHEET_SALES_RETURNS,
    config.SHEET_PROFIT,
    config.SHEET_FOREIGN_PURCHASES,
    config.SHEET_LOCAL_PURCHASES,
    config.SHEET_LOCAL_PURCHASE_RETURNS,
    config.SHEET_SUPPLIER_DEBT,
    config.SHEET_SUPPLIER_CREDITORS,
}


def load_raw_sheets() -> dict:
    """
    Reads all 8 sheets from SOURCE_WORKBOOK exactly as they are, with sheet
    name AND column whitespace stripped only (no filtering, no type
    coercion, no row removal). Returns {stripped_sheet_name: DataFrame},
    keyed by the config.SHEET_* constants (which are already whitespace-free).
    """
    if not config.SOURCE_WORKBOOK.exists():
        raise FileNotFoundError(
            f"Source workbook not found at: {config.SOURCE_WORKBOOK}. "
            "Refusing to proceed with synthetic or assumed data."
        )

    raw_sheets = pd.read_excel(config.SOURCE_WORKBOOK, sheet_name=None, engine="openpyxl")

    sheets = {}
    for raw_name, df in raw_sheets.items():
        stripped_name = raw_name.strip() if isinstance(raw_name, str) else raw_name
        sheets[stripped_name] = _strip_columns(df)

    actual = set(sheets.keys())
    if actual != EXPECTED_SHEETS:
        raise ValueError(
            f"Workbook sheet names changed since the last structural audit. "
            f"Expected {EXPECTED_SHEETS}, found {actual}. Stopping rather than guessing."
        )

    return sheets
