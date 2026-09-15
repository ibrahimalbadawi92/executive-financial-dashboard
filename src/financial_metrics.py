# -*- coding: utf-8 -*-
"""
All approved financial KPI formulas, exactly as approved for the current
8-sheet workbook. No metric here that isn't explicitly supported by the
source data. Profit is READ from the approved Profit sheet only - never
calculated here from Sales/Purchases/inventory (see build_profit_table).
"""
import numpy as np
import pandas as pd

import config
from src.utils import safe_div, safe_pct, yoy_change


def _filter_year(df: pd.DataFrame, year) -> pd.DataFrame:
    if year is None:
        return df
    return df[df["year"] == year]


def compute_period_metrics(fact_sales, fact_sales_returns, fact_local_purchases, fact_foreign_purchases,
                            fact_local_purchase_returns, year=None) -> dict:
    """
    Computes every approved KPI for one year (year=2022..2025) or for the
    whole period (year=None). All VAT-exclusive and VAT-inclusive figures are
    kept under clearly separate keys - never mixed under one KPI name.

    Local and Foreign Purchases are kept as distinct measures throughout
    (management request) and only ever combined into Total Purchases, which
    sums two VAT-exclusive bases and never nets against Purchase Returns - so
    unlike the old single-Purchases model, no metric here mixes a
    supplier-scoped purchase figure with a company-wide Local Purchase
    Returns figure (Local Purchase Returns has no supplier field). Net Input
    VAT / Indicative VAT Position and the Net Sales vs Net Purchases Gap are
    intentionally not computed here at all (management request - removed,
    not merely hidden).
    """
    fs = _filter_year(fact_sales, year)
    fsr = _filter_year(fact_sales_returns, year)
    flp = _filter_year(fact_local_purchases, year)
    ffp = _filter_year(fact_foreign_purchases, year)
    flpr = _filter_year(fact_local_purchase_returns, year)

    # ---- Sales (VAT-exclusive base) ----
    gross_sales_before_vat = fs["net_amount"].sum()
    sales_returns_before_vat = fsr["return_value_before_vat"].sum()
    net_sales_before_vat = gross_sales_before_vat - sales_returns_before_vat
    sales_return_rate_pct = safe_pct(sales_returns_before_vat, gross_sales_before_vat)
    sales_transaction_count = len(fs)
    avg_sales_transaction_value = safe_div(net_sales_before_vat, sales_transaction_count)

    # ---- Sales (VAT-inclusive, kept separate) ----
    gross_sales_incl_vat = fs["gross_amount"].sum()
    sales_returns_incl_vat = fsr["return_total_incl_vat"].sum()
    net_sales_incl_vat = gross_sales_incl_vat - sales_returns_incl_vat

    # ---- VAT (Output/Sales side only - Input VAT no longer surfaced, management request) ----
    gross_output_vat = fs["vat_amount"].sum()
    sales_return_vat = fsr["return_vat_amount"].sum()
    net_output_vat = gross_output_vat - sales_return_vat

    # ---- Local Purchases ----
    local_purchases_before_vat = flp["purchase_before_vat"].sum()
    local_purchase_vat = flp["vat_amount"].sum()
    local_purchases_incl_vat = flp["purchase_incl_vat"].sum()
    local_purchase_transaction_count = len(flp)

    # ---- Foreign Purchases ----
    foreign_purchase_base = ffp["purchase_base"].sum()
    foreign_purchase_additional_cost = ffp["additional_cost"].sum()
    foreign_purchase_total = ffp["purchase_total_before_vat"].sum()  # already includes additional cost - never add it again
    foreign_purchase_transaction_count = len(ffp)

    # ---- Total Purchases (both VAT-exclusive bases - accounting-compatible to sum) ----
    total_purchases_before_vat = local_purchases_before_vat + foreign_purchase_total
    purchase_transaction_count = local_purchase_transaction_count + foreign_purchase_transaction_count

    # ---- Local Purchase Returns (company-wide only - no supplier field, never
    #      attributed to Foreign Purchases) ----
    local_purchase_returns_before_vat = flpr["return_value_before_vat"].sum()
    local_purchase_returns_vat = flpr["vat_amount"].sum()

    return {
        "gross_sales_before_vat": gross_sales_before_vat,
        "sales_returns_before_vat": sales_returns_before_vat,
        "net_sales_before_vat": net_sales_before_vat,
        "sales_return_rate_pct": sales_return_rate_pct,
        "sales_transaction_count": sales_transaction_count,
        "avg_sales_transaction_value": avg_sales_transaction_value,

        "gross_sales_incl_vat": gross_sales_incl_vat,
        "sales_returns_incl_vat": sales_returns_incl_vat,
        "net_sales_incl_vat": net_sales_incl_vat,

        "gross_output_vat": gross_output_vat,
        "sales_return_vat": sales_return_vat,
        "net_output_vat": net_output_vat,

        "local_purchases_before_vat": local_purchases_before_vat,
        "local_purchase_vat": local_purchase_vat,
        "local_purchases_incl_vat": local_purchases_incl_vat,
        "local_purchase_transaction_count": local_purchase_transaction_count,

        "foreign_purchase_base": foreign_purchase_base,
        "foreign_purchase_additional_cost": foreign_purchase_additional_cost,
        "foreign_purchase_total": foreign_purchase_total,
        "foreign_purchase_transaction_count": foreign_purchase_transaction_count,

        "total_purchases_before_vat": total_purchases_before_vat,
        "purchase_transaction_count": purchase_transaction_count,

        "local_purchase_returns_before_vat": local_purchase_returns_before_vat,
        "local_purchase_returns_vat": local_purchase_returns_vat,
    }


def build_annual_table(fact_sales, fact_sales_returns, fact_local_purchases, fact_foreign_purchases,
                        fact_local_purchase_returns, years=config.ANALYSIS_YEARS) -> pd.DataFrame:
    rows = []
    for y in years:
        m = compute_period_metrics(fact_sales, fact_sales_returns, fact_local_purchases, fact_foreign_purchases,
                                    fact_local_purchase_returns, year=y)
        m["year"] = y
        rows.append(m)
    total = compute_period_metrics(fact_sales, fact_sales_returns, fact_local_purchases, fact_foreign_purchases,
                                    fact_local_purchase_returns, year=None)
    total["year"] = "ALL_PERIOD_2022_2025"
    rows.append(total)
    return pd.DataFrame(rows).set_index("year")


YOY_KPIS = [
    "gross_sales_before_vat", "net_sales_before_vat", "sales_returns_before_vat", "sales_return_rate_pct",
    "net_output_vat",
    "local_purchases_before_vat", "foreign_purchase_total", "total_purchases_before_vat",
    "local_purchase_returns_before_vat",
    "sales_transaction_count", "purchase_transaction_count",
]


def build_yoy_table(annual_df: pd.DataFrame, kpis=YOY_KPIS,
                     pairs=((2023, 2022), (2024, 2023), (2025, 2024), (2025, 2022))) -> pd.DataFrame:
    records = []
    for cur, prev in pairs:
        if cur not in annual_df.index or prev not in annual_df.index:
            continue
        row = {"comparison": f"{cur} vs {prev}"}
        for k in kpis:
            curv, prevv = annual_df.loc[cur, k], annual_df.loc[prev, k]
            abs_var, pct_var = yoy_change(curv, prevv)
            row[f"{k}__current"] = curv
            row[f"{k}__previous"] = prevv
            row[f"{k}__abs_var"] = abs_var
            row[f"{k}__pct_var"] = pct_var
        records.append(row)
    return pd.DataFrame(records).set_index("comparison")


# --------------------------------------------------------------------------
# PROFIT (approved source only - never calculated from Sales/Purchases)
# --------------------------------------------------------------------------
def build_profit_table(fact_profit: pd.DataFrame) -> pd.DataFrame:
    """Straight read of the approved Profit sheet, indexed by year. No
    calculation happens here - this is a pass-through, not a derivation."""
    return fact_profit.sort_values("year").set_index("year")


def profit_for_year(profit_table: pd.DataFrame, year: int):
    """Returns the approved Profit for `year`, or None if not covered by the
    source sheet - never a calculated fallback."""
    return profit_table.loc[year, "profit"] if year in profit_table.index else None


def profit_for_years(profit_table: pd.DataFrame, years: list):
    """Sum of the approved annual Profit values for the given full years -
    a plain sum of supplied figures, not a derived calculation. Returns None
    if any requested year is not covered (never a partial/misleading total)."""
    vals = [profit_for_year(profit_table, y) for y in years]
    if not vals or any(v is None for v in vals):
        return None
    return float(sum(vals))


def build_profit_yoy_table(profit_table: pd.DataFrame,
                            pairs=((2023, 2022), (2024, 2023), (2025, 2024))) -> pd.DataFrame:
    """Profit YoY Change = (Current Profit - Previous Profit) / Previous
    Profit - a comparison of the supplied Profit values only, never a margin
    or a Sales/Purchases-derived figure."""
    records = []
    for cur, prev in pairs:
        curv = profit_for_year(profit_table, cur)
        prevv = profit_for_year(profit_table, prev)
        if curv is None or prevv is None:
            continue
        abs_var, pct_var = yoy_change(curv, prevv)
        records.append({"comparison": f"{cur} vs {prev}", "current_profit": curv,
                         "previous_profit": prevv, "abs_var": abs_var, "pct_var": pct_var})
    return pd.DataFrame(records).set_index("comparison") if records else pd.DataFrame(
        columns=["current_profit", "previous_profit", "abs_var", "pct_var"])


def monthly_net_sales_series(fact_sales: pd.DataFrame, fact_sales_returns: pd.DataFrame) -> pd.DataFrame:
    """
    True Net Sales (Gross Sales − Sales Returns) per calendar month, for the
    continuous full-period 48-month Sales trend chart (management request -
    ONE continuous line across all of Jan 2022 - Dec 2025, never split into
    per-year series). Deliberately takes the raw fact tables (not the
    already-filtered ones) - this chart stays fixed at the full 2022-2025
    period regardless of active Year/Quarter filters elsewhere on the page.
    """
    g_sales = fact_sales.groupby(["year", "month"], observed=True)["net_amount"].sum()
    g_returns = fact_sales_returns.groupby(["year", "month"], observed=True)["return_value_before_vat"].sum()
    combined = pd.DataFrame({"gross_sales": g_sales, "sales_returns": g_returns}).fillna(0.0)
    combined["net_sales_before_vat"] = combined["gross_sales"] - combined["sales_returns"]
    combined = combined.reset_index()
    combined["year"] = combined["year"].astype(int)
    combined["month"] = combined["month"].astype(int)
    return combined.sort_values(["year", "month"]).reset_index(drop=True)


# --------------------------------------------------------------------------
# CUSTOMER ANALYSIS (generic 'نقدي' cash bucket always kept identifiable,
# excluded from concentration ranking per Phase 1/2 rule)
# --------------------------------------------------------------------------
def customer_analysis(fact_sales: pd.DataFrame, fact_sales_returns: pd.DataFrame) -> pd.DataFrame:
    """
    Grouped by customer_name_original ONLY (not customer_no+name). Root
    cause fixed here: Sales Returns has no customer_no field at all - only a
    name. A small number of customer names (structural audit: 52 across the
    approved workbook, 33 with at least one return row) are used under more
    than one customer_no in Sales. Grouping Sales by (customer_no, name) and
    then merging Returns by name alone caused the SAME return total to be
    attached in full to EVERY customer_no sharing that name - inflating
    Return Rate for whichever customer_no had the smaller Sales volume under
    that name (confirmed empirically up to 1900%+ on one name). Since the
    source cannot distinguish which customer_no a return truly belongs to
    when names collide, aggregating at the name grain (the only grain the
    join key actually supports) is the safe, non-fabricating fix - not an
    invented allocation.
    """
    sales_agg = fact_sales.groupby("customer_name_original", dropna=False).agg(
        customer_no=("customer_no", "first"),
        distinct_customer_no_count=("customer_no", "nunique"),
        gross_sales_before_vat=("net_amount", "sum"),
        transaction_count=("net_amount", "size"),
    ).reset_index()

    returns_agg = (
        fact_sales_returns.groupby("customer_name_original", dropna=False)["return_value_before_vat"]
        .sum().reset_index().rename(columns={"return_value_before_vat": "sales_returns_before_vat"})
    )

    merged = sales_agg.merge(returns_agg, on="customer_name_original", how="left")
    merged["sales_returns_before_vat"] = merged["sales_returns_before_vat"].fillna(0.0)
    merged["net_sales_before_vat"] = merged["gross_sales_before_vat"] - merged["sales_returns_before_vat"]
    merged["return_rate_pct"] = merged.apply(
        lambda r: safe_pct(r["sales_returns_before_vat"], r["gross_sales_before_vat"]), axis=1
    )
    merged["is_generic_cash_customer"] = merged["customer_name_original"] == config.GENERIC_CASH_CUSTOMER_NAME

    total_net_sales = merged["net_sales_before_vat"].sum()
    merged["contribution_pct_of_total"] = merged["net_sales_before_vat"].apply(lambda v: safe_pct(v, total_net_sales))

    return merged.sort_values("net_sales_before_vat", ascending=False).reset_index(drop=True)


def customer_concentration(customer_df: pd.DataFrame) -> dict:
    """Concentration among IDENTIFIABLE (non-generic) customers only."""
    named = customer_df[~customer_df["is_generic_cash_customer"]].sort_values(
        "net_sales_before_vat", ascending=False
    ).reset_index(drop=True)
    total = named["net_sales_before_vat"].sum()
    top5 = named.head(5)["net_sales_before_vat"].sum()
    top10 = named.head(10)["net_sales_before_vat"].sum()
    generic = customer_df[customer_df["is_generic_cash_customer"]]
    return {
        "named_customer_count": len(named),
        "named_customer_total_net_sales": total,
        "top5_customer_share_pct": safe_pct(top5, total),
        "top10_customer_share_pct": safe_pct(top10, total),
        "cash_walkin_net_sales": generic["net_sales_before_vat"].sum() if len(generic) else 0.0,
        "cash_walkin_share_of_all_sales_pct": safe_pct(
            generic["net_sales_before_vat"].sum() if len(generic) else 0.0,
            customer_df["net_sales_before_vat"].sum(),
        ),
    }


# --------------------------------------------------------------------------
# SUPPLIER ANALYSIS - kept separate for Local vs Foreign (management
# request), never combined into one supplier ranking. Local Purchase Returns
# has no supplier field and is never joined here.
# --------------------------------------------------------------------------
def supplier_analysis_local(fact_local_purchases: pd.DataFrame) -> pd.DataFrame:
    agg = fact_local_purchases.groupby("supplier_name_original", dropna=False).agg(
        purchase_value_before_vat=("purchase_before_vat", "sum"),
        transaction_count=("purchase_before_vat", "size"),
    ).reset_index()
    total = agg["purchase_value_before_vat"].sum()
    agg["contribution_pct_of_total"] = agg["purchase_value_before_vat"].apply(lambda v: safe_pct(v, total))
    # Structural audit finding: supplier_name_original == 'عام' ("general") is
    # a generic/unspecified-supplier bucket, not one identifiable supplier -
    # flagged (never silently removed) so concentration analysis can exclude
    # it the same way 'نقدي' is excluded from customer concentration.
    agg["is_generic_supplier"] = agg["supplier_name_original"] == config.GENERIC_SUPPLIER_NAME
    return agg.sort_values("purchase_value_before_vat", ascending=False).reset_index(drop=True)


def supplier_analysis_foreign(fact_foreign_purchases: pd.DataFrame) -> pd.DataFrame:
    agg = fact_foreign_purchases.groupby("supplier_name_original", dropna=False).agg(
        purchase_value_before_vat=("purchase_total_before_vat", "sum"),
        transaction_count=("purchase_total_before_vat", "size"),
    ).reset_index()
    total = agg["purchase_value_before_vat"].sum()
    agg["contribution_pct_of_total"] = agg["purchase_value_before_vat"].apply(lambda v: safe_pct(v, total))
    # No generic/unspecified supplier bucket found in Foreign Purchases
    # (structural audit) - column kept for schema parity with
    # supplier_analysis_local() so supplier_concentration() can stay generic.
    agg["is_generic_supplier"] = False
    return agg.sort_values("purchase_value_before_vat", ascending=False).reset_index(drop=True)


def supplier_concentration(supplier_df: pd.DataFrame) -> dict:
    """
    Top5/Top10 concentration among IDENTIFIABLE (non-generic) suppliers only
    - works on either supplier_analysis_local() or supplier_analysis_foreign()
    output (same column shape). The generic 'عام' bucket (Local Purchases
    only) is excluded from ranking/Top-N the same way 'نقدي' is excluded from
    customer concentration, and reported separately so its size is never
    hidden.
    """
    named = supplier_df[~supplier_df["is_generic_supplier"]].sort_values(
        "purchase_value_before_vat", ascending=False
    ).reset_index(drop=True)
    total = named["purchase_value_before_vat"].sum()
    top5 = named.head(5)["purchase_value_before_vat"].sum()
    top10 = named.head(10)["purchase_value_before_vat"].sum()
    generic = supplier_df[supplier_df["is_generic_supplier"]]
    generic_value = generic["purchase_value_before_vat"].sum() if len(generic) else 0.0
    return {
        "supplier_count": len(named),
        "total_purchase_value_before_vat": total,
        "top5_supplier_share_pct": safe_pct(top5, total),
        "top10_supplier_share_pct": safe_pct(top10, total),
        "generic_supplier_value": generic_value,
        "generic_supplier_share_pct": safe_pct(generic_value, supplier_df["purchase_value_before_vat"].sum()),
    }


# --------------------------------------------------------------------------
# LOCAL PURCHASE RETURNS BY COST CENTER (the only fact table with a proven
# Cost Center field - never applied to any other dataset)
# --------------------------------------------------------------------------
def local_purchase_returns_by_cost_center(fact_local_purchase_returns: pd.DataFrame) -> pd.DataFrame:
    agg = fact_local_purchase_returns.groupby("cost_center_name", dropna=False).agg(
        return_value_before_vat=("return_value_before_vat", "sum"),
        return_row_count=("return_value_before_vat", "size"),
    ).reset_index()
    return agg.sort_values("return_value_before_vat", ascending=False).reset_index(drop=True)


# --------------------------------------------------------------------------
# SUPPLIER BALANCES (point-in-time source snapshots - signs preserved
# exactly as reported; no invented "net position" - see page/README)
# --------------------------------------------------------------------------
def supplier_balance_summary(fact_balance: pd.DataFrame) -> dict:
    return {
        "supplier_count": fact_balance["supplier_name_original"].nunique(),
        "total_local_currency": fact_balance["local_currency_amount"].sum(),
    }


# --------------------------------------------------------------------------
# CASH VS CREDIT SPLITS
# --------------------------------------------------------------------------
def cash_vs_credit_sales(fact_sales: pd.DataFrame) -> dict:
    return fact_sales.groupby("normalized_transaction_type")["net_amount"].sum().to_dict()


def cash_vs_credit_local_purchases(fact_local_purchases: pd.DataFrame) -> dict:
    return fact_local_purchases.groupby("normalized_transaction_type")["purchase_before_vat"].sum().to_dict()
