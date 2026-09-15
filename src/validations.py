# -*- coding: utf-8 -*-
"""
Reusable data-quality and reconciliation reporting.

Terminology (kept unambiguous on purpose):
  - "Excluded from analytical totals": the record is NEVER counted anywhere
    (e.g. an embedded grand-total/subtotal row).
  - "Excluded from VAT calculation": the record IS kept in its fact table and
    DOES count toward activity/net-amount totals; only its tax figure is kept
    out of VAT sums.
These are never merged into one bucket.
"""
import pandas as pd

import config


def reconciliation_report(fact_df: pd.DataFrame, label: str, status_col: str = "reconciliation_status") -> dict:
    counts = fact_df[status_col].value_counts().to_dict()
    total = len(fact_df)
    valid = counts.get("Valid", 0)
    review = counts.get("Reconciliation-Review", 0)
    return {
        "sheet": label,
        "total_rows_checked": total,
        "valid": valid,
        "reconciliation_review": review,
        "valid_pct": round(100 * valid / total, 2) if total else None,
    }


def purchase_returns_discount_status_report(fact_local_purchase_returns: pd.DataFrame) -> dict:
    counts = fact_local_purchase_returns["discount_status"].value_counts().to_dict()
    total = len(fact_local_purchase_returns)
    return {
        "total_purchase_return_rows": total,
        "discount_reported": counts.get("Reported", 0),
        "discount_missing_inferred_zero": counts.get("Missing-Inferred-Zero", 0),
        "discount_missing_unresolved": counts.get("Missing-Unresolved", 0),
        "data_quality_warning_rows": int(fact_local_purchase_returns["data_quality_warning"].sum()),
    }


def exclusion_report(raw_row_count: int, fact_row_count: int, excluded_audit: pd.DataFrame) -> dict:
    return {
        "source_rows_in_sheet": raw_row_count,
        "analytical_rows_used": fact_row_count,
        "rows_excluded_from_analytical_totals": len(excluded_audit),
        "excluded_row_detail": excluded_audit.to_dict(orient="records"),
    }


def profit_sheet_report(fact_profit: pd.DataFrame) -> dict:
    """Validates the approved Profit sheet: unique years, numeric values,
    full 2022-2025 coverage. Purely descriptive - never alters the values."""
    years = fact_profit["year"].tolist()
    return {
        "row_count": len(fact_profit),
        "years_present": sorted(int(y) for y in years),
        "years_unique": len(years) == len(set(years)),
        "all_numeric": fact_profit["profit"].notna().all(),
        "covers_analysis_years": set(config.ANALYSIS_YEARS).issubset(set(int(y) for y in years)),
    }


def supplier_balance_report(fact_balance: pd.DataFrame, excluded_audit: pd.DataFrame, label: str) -> dict:
    """Validates a supplier-balance snapshot sheet: supplier names present,
    currency present, missing amounts, and that the excluded total row (if
    any) reconciles to the real rows' sum - never asserts sign meaning."""
    missing_currency = fact_balance["currency"].isna().sum()
    missing_local_amount = fact_balance["local_currency_amount"].isna().sum()
    recomputed_total = fact_balance["local_currency_amount"].sum()
    reported_total = excluded_audit["local_currency_amount"].iloc[0] if len(excluded_audit) else None
    total_matches = (
        bool(abs(recomputed_total - reported_total) < 1.0)
        if reported_total is not None and pd.notna(reported_total) else None
    )
    return {
        "sheet": label,
        "supplier_row_count": len(fact_balance),
        "missing_currency_rows": int(missing_currency),
        "missing_local_amount_rows": int(missing_local_amount),
        "recomputed_local_total": recomputed_total,
        "reported_grand_total": reported_total,
        "recomputed_matches_reported_total": total_matches,
    }


def cost_center_report(fact_local_purchase_returns: pd.DataFrame) -> dict:
    """
    The Cost Center field ("رقم المستودع") may, in a real production
    workbook, be a mix of business-readable names and legacy purely-numeric
    warehouse codes that were never renamed at the source. No lookup/mapping
    sheet is assumed to exist anywhere in the workbook to translate codes to
    names, so none is invented here (see project change-control rule against
    fabricating mappings) - both name and code values are used exactly as
    sourced, and any numeric ones are flagged for management/accounting
    confirmation rather than silently hidden or guessed at.
    """
    cc = fact_local_purchase_returns["cost_center_name"].dropna()
    names = cc.unique().tolist()
    is_numeric_code = cc.str.match(r"^\d+(\.0)?$")
    numeric_values = sorted(cc[is_numeric_code].unique().tolist(), key=lambda v: float(v))
    return {
        "distinct_cost_center_count": len(names),
        "cost_center_names": sorted(names),
        "numeric_code_distinct_count": len(numeric_values),
        "numeric_code_values": numeric_values,
        "numeric_code_row_count": int(is_numeric_code.sum()),
    }


def customer_name_quality_report(dim_customer: pd.DataFrame) -> dict:
    """
    A small number of distinct customer_no groups in the Sales sheet may
    (a separate, much smaller issue than the Cost Center numeric-code one
    above) have a source 'customer name' value that is
    itself just the literal digit string '1' - not a real business/person
    name, and not the generic 'نقدي' cash-customer bucket (a different,
    already-excluded customer_no). No alternate name field exists for these
    two, so none is invented; they are flagged here for management/
    accounting awareness rather than hidden or silently relabeled - see the
    Customer filter's `pandas.Series.unique()` dedup, which also means they
    render as a single visually-identical '1' option.
    """
    names = dim_customer.loc[~dim_customer["is_generic_cash_customer"], "customer_name"].dropna()
    is_numeric_only = names.str.match(r"^\d+(\.0)?$")
    return {
        "numeric_only_name_count": int(is_numeric_only.sum()),
        "numeric_only_name_values": sorted(names[is_numeric_only].unique().tolist()),
    }


def data_quality_summary(raw_sheets: dict, fact_sales, sales_excluded_audit, fact_sales_returns, sret_excluded_audit,
                          fact_local_purchases, lpurch_excluded_audit, fact_foreign_purchases, fpurch_excluded_audit,
                          fact_local_purchase_returns, lpret_excluded_audit, fact_profit,
                          fact_supplier_debt, sdebt_excluded_audit, fact_supplier_creditors, scred_excluded_audit,
                          dim_customer) -> dict:
    """Top-level Data Quality scorecard for the current 8-sheet workbook."""
    sales_recon = reconciliation_report(fact_sales, "Sales")
    sret_recon = reconciliation_report(fact_sales_returns, "Sales Returns")
    lpurch_recon = reconciliation_report(fact_local_purchases, "Local Purchases")
    fpurch_recon = reconciliation_report(fact_foreign_purchases, "Foreign Purchases")
    lpret_recon = reconciliation_report(fact_local_purchase_returns, "Local Purchase Returns")
    lpret_discount = purchase_returns_discount_status_report(fact_local_purchase_returns)

    return {
        "total_source_records": {
            "sales": len(raw_sheets[config.SHEET_SALES]),
            "sales_returns": len(raw_sheets[config.SHEET_SALES_RETURNS]),
            "local_purchases": len(raw_sheets[config.SHEET_LOCAL_PURCHASES]),
            "foreign_purchases": len(raw_sheets[config.SHEET_FOREIGN_PURCHASES]),
            "local_purchase_returns": len(raw_sheets[config.SHEET_LOCAL_PURCHASE_RETURNS]),
            "profit": len(raw_sheets[config.SHEET_PROFIT]),
            "supplier_debt": len(raw_sheets[config.SHEET_SUPPLIER_DEBT]),
            "supplier_creditors": len(raw_sheets[config.SHEET_SUPPLIER_CREDITORS]),
        },
        "analytical_records": {
            "sales": len(fact_sales),
            "sales_returns": len(fact_sales_returns),
            "local_purchases": len(fact_local_purchases),
            "foreign_purchases": len(fact_foreign_purchases),
            "local_purchase_returns": len(fact_local_purchase_returns),
        },
        "exclusions": {
            "sales": exclusion_report(len(raw_sheets[config.SHEET_SALES]), len(fact_sales), sales_excluded_audit),
            "sales_returns": exclusion_report(len(raw_sheets[config.SHEET_SALES_RETURNS]), len(fact_sales_returns), sret_excluded_audit),
            "local_purchases": exclusion_report(len(raw_sheets[config.SHEET_LOCAL_PURCHASES]), len(fact_local_purchases), lpurch_excluded_audit),
            "foreign_purchases": exclusion_report(len(raw_sheets[config.SHEET_FOREIGN_PURCHASES]), len(fact_foreign_purchases), fpurch_excluded_audit),
            "local_purchase_returns": exclusion_report(len(raw_sheets[config.SHEET_LOCAL_PURCHASE_RETURNS]), len(fact_local_purchase_returns), lpret_excluded_audit),
        },
        "reconciliation": {
            "sales": sales_recon,
            "sales_returns": sret_recon,
            "local_purchases": lpurch_recon,
            "foreign_purchases": fpurch_recon,
            "local_purchase_returns": lpret_recon,
        },
        "local_purchase_returns_discount_status": lpret_discount,
        "profit": profit_sheet_report(fact_profit),
        "supplier_debt": supplier_balance_report(fact_supplier_debt, sdebt_excluded_audit, "Supplier Debt"),
        "supplier_creditors": supplier_balance_report(fact_supplier_creditors, scred_excluded_audit, "Supplier Creditors"),
        "cost_centers": cost_center_report(fact_local_purchase_returns),
        "customer_name_quality": customer_name_quality_report(dim_customer),
    }
