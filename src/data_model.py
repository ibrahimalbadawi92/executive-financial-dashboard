# -*- coding: utf-8 -*-
"""
Shared analytical dimensions: DimDate, DimCustomer, DimSupplier.

Per Phase 1 findings, Date is the ONLY dimension safely shared by all four
fact tables. Customer is shared by Sales <-> Sales Returns (by name only -
Returns has no customer number). Supplier applies to Purchases only -
Purchase Returns has no supplier field and must never be joined to it.
"""
import numpy as np
import pandas as pd

import config

_MONTH_NAMES_EN = ["January", "February", "March", "April", "May", "June",
                    "July", "August", "September", "October", "November", "December"]
_MONTH_NAMES_AR = ["يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو",
                    "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"]
_DOW_NAMES_EN = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
_DOW_NAMES_AR = ["الاثنين", "الثلاثاء", "الأربعاء", "الخميس", "الجمعة", "السبت", "الأحد"]


def _derive_date_attributes(dates: pd.Series) -> pd.DataFrame:
    """Vectorized derivation of every DimDate attribute from a datetime series."""
    dates = pd.to_datetime(dates)
    year = dates.dt.year
    month = dates.dt.month
    quarter = dates.dt.quarter
    dow = dates.dt.dayofweek  # Monday=0..Sunday=6

    out = pd.DataFrame({
        "date": dates.dt.normalize(),
        "year": year,
        "quarter": quarter,
        "quarter_label": "Q" + quarter.astype("Int64").astype(str) + "-" + year.astype("Int64").astype(str),
        "month": month,
        "month_name_en": month.map(lambda m: _MONTH_NAMES_EN[m - 1] if pd.notna(m) else np.nan),
        "month_name_ar": month.map(lambda m: _MONTH_NAMES_AR[m - 1] if pd.notna(m) else np.nan),
        "year_month": year.astype("Int64").astype(str) + "-" + month.astype("Int64").astype(str).str.zfill(2),
        "day": dates.dt.day,
        "dow_en": dow.map(lambda d: _DOW_NAMES_EN[d] if pd.notna(d) else np.nan),
        "dow_ar": dow.map(lambda d: _DOW_NAMES_AR[d] if pd.notna(d) else np.nan),
    })
    return out


def build_dim_date(start=config.PERIOD_START, end=config.PERIOD_END) -> pd.DataFrame:
    """Full calendar-day Date Dimension covering the entire analysis period."""
    calendar = pd.Series(pd.date_range(start=start, end=end, freq="D"))
    dim = _derive_date_attributes(calendar)
    # month_name_en as an ordered categorical -> guarantees chronological sort in any groupby/plot
    month_order_en = _MONTH_NAMES_EN
    month_order_ar = _MONTH_NAMES_AR
    dim["month_name_en"] = pd.Categorical(dim["month_name_en"], categories=month_order_en, ordered=True)
    dim["month_name_ar"] = pd.Categorical(dim["month_name_ar"], categories=month_order_ar, ordered=True)
    return dim.reset_index(drop=True)


def attach_date_attributes(df: pd.DataFrame, date_col: str) -> pd.DataFrame:
    """
    Adds year/quarter/month/day-of-week columns to a fact table, derived with
    the exact same logic as build_dim_date (so the two are always consistent).
    Rows with an invalid/missing date get NaN attributes, not dropped.
    """
    attrs = _derive_date_attributes(df[date_col]).drop(columns=["date"])
    out = pd.concat([df.reset_index(drop=True), attrs.reset_index(drop=True)], axis=1)
    return out


def build_dim_customer(fact_sales: pd.DataFrame) -> pd.DataFrame:
    """
    Distinct customers observed in Sales (Sales Returns has no customer number
    and is matched to this dimension by name only, downstream, not merged here).
    """
    g = fact_sales.groupby("customer_no", dropna=False).agg(
        customer_name=("customer_name_original", lambda s: s.mode().iat[0] if not s.mode().empty else s.iloc[0]),
        vat_registration_id=("customer_vat_registration_id", lambda s: s.dropna().iloc[0] if s.notna().any() else np.nan),
        distinct_names_used=("customer_name_original", "nunique"),
    ).reset_index()
    g["is_generic_cash_customer"] = g["customer_no"] == config.GENERIC_CASH_CUSTOMER_NO
    return g


def build_dim_supplier(fact_local_purchases: pd.DataFrame, fact_foreign_purchases: pd.DataFrame) -> pd.DataFrame:
    """
    Distinct suppliers observed across BOTH Local and Foreign Purchases (no
    supplier-number field exists in the source, name is the only identity).
    Whitespace/case are normalized for grouping only - names are never
    fuzzy-matched or merged across genuinely different spellings, per the
    approved supplier-filter-safety rule. `in_local`/`in_foreign` flag which
    fact table(s) each supplier actually appears in, so a supplier filter
    can be applied only where the relationship genuinely exists.
    """
    loc = fact_local_purchases[["supplier_name_original"]].copy()
    loc["source"] = "local"
    frn = fact_foreign_purchases[["supplier_name_original"]].copy()
    frn["source"] = "foreign"
    both = pd.concat([loc, frn], ignore_index=True)
    both = both.dropna(subset=["supplier_name_original"])

    g = both.groupby("supplier_name_original").agg(
        transaction_count=("supplier_name_original", "size"),
        in_local=("source", lambda s: (s == "local").any()),
        in_foreign=("source", lambda s: (s == "foreign").any()),
    ).reset_index().rename(columns={"supplier_name_original": "supplier_name"})
    return g


def build_dim_cost_center(fact_local_purchase_returns: pd.DataFrame) -> pd.DataFrame:
    """
    Distinct Cost Center values observed in Local Purchase Returns. A real
    production workbook may carry a mix of business-readable names and
    legacy purely-numeric warehouse codes left over from an earlier system -
    no lookup/mapping sheet is assumed to exist, so the source field is used
    exactly as-is (name or code) with no invented mapping (see
    validations.cost_center_report, which flags any numeric ones explicitly
    for management/accounting confirmation rather than hiding them). Only
    Local Purchase Returns has a proven Cost Center field; no other fact
    table shares it.
    """
    g = fact_local_purchase_returns.groupby("cost_center_name", dropna=False).agg(
        return_row_count=("cost_center_name", "size"),
    ).reset_index()
    return g
