# -*- coding: utf-8 -*-
"""
Streamlit-facing glue: loads and cleans the workbook exactly once per app
process (st.cache_resource) and reuses the approved analytical modules
verbatim. No business logic lives here - this only wires
data_loader -> data_cleaning -> data_model -> validations -> financial_metrics
together and caches the result.
"""
import streamlit as st

import config
from src import data_loader, data_cleaning, data_model, validations, financial_metrics, filters as filters_mod


def _source_signature() -> tuple:
    """(mtime, size) of SOURCE_WORKBOOK, cheap to stat() on every script run.
    Passed into the cache_resource-decorated loader below as a plain
    (hashable) argument so it becomes part of Streamlit's cache key - a
    change to the workbook on disk (edited and saved externally in Excel
    while this app process keeps running) produces a new signature, which
    st.cache_resource sees as a new cache entry and reloads for, rather than
    silently continuing to serve the in-memory bundle read at process start.
    A long-running process with no such tie would otherwise cache the
    workbook's contents for its entire lifetime, regardless of later edits."""
    stat = config.SOURCE_WORKBOOK.stat()
    return (stat.st_mtime, stat.st_size)


def load_pipeline() -> dict:
    """Public entry point - computes the current source signature and
    delegates to the cached loader below, so the cache is keyed by it."""
    return _load_pipeline_cached(_source_signature())


@st.cache_resource(show_spinner="Loading and validating financial data...")
def _load_pipeline_cached(source_signature: tuple) -> dict:
    raw = data_loader.load_raw_sheets()

    fact_sales, sales_excluded_audit = data_cleaning.clean_sales(raw[config.SHEET_SALES])
    fact_sales_returns, sret_excluded_audit = data_cleaning.clean_sales_returns(raw[config.SHEET_SALES_RETURNS])
    fact_sales_returns = data_cleaning.link_sales_returns_to_sales_best_effort(fact_sales_returns, fact_sales)

    fact_local_purchases, lpurch_excluded_audit = data_cleaning.clean_local_purchases(raw[config.SHEET_LOCAL_PURCHASES])
    fact_foreign_purchases, fpurch_excluded_audit = data_cleaning.clean_foreign_purchases(raw[config.SHEET_FOREIGN_PURCHASES])
    fact_local_purchase_returns, lpret_excluded_audit = data_cleaning.clean_local_purchase_returns(
        raw[config.SHEET_LOCAL_PURCHASE_RETURNS])

    fact_profit = data_cleaning.clean_profit(raw[config.SHEET_PROFIT])

    fact_supplier_debt, sdebt_excluded_audit = data_cleaning.clean_supplier_debt(raw[config.SHEET_SUPPLIER_DEBT])
    fact_supplier_creditors, scred_excluded_audit = data_cleaning.clean_supplier_creditors(raw[config.SHEET_SUPPLIER_CREDITORS])

    dim_date = data_model.build_dim_date()
    dim_customer = data_model.build_dim_customer(fact_sales)
    dim_supplier = data_model.build_dim_supplier(fact_local_purchases, fact_foreign_purchases)
    dim_cost_center = data_model.build_dim_cost_center(fact_local_purchase_returns)

    dq = validations.data_quality_summary(
        raw, fact_sales, sales_excluded_audit, fact_sales_returns, sret_excluded_audit,
        fact_local_purchases, lpurch_excluded_audit, fact_foreign_purchases, fpurch_excluded_audit,
        fact_local_purchase_returns, lpret_excluded_audit, fact_profit,
        fact_supplier_debt, sdebt_excluded_audit, fact_supplier_creditors, scred_excluded_audit,
        dim_customer,
    )

    annual = financial_metrics.build_annual_table(
        fact_sales, fact_sales_returns, fact_local_purchases, fact_foreign_purchases, fact_local_purchase_returns)
    yoy = financial_metrics.build_yoy_table(annual)

    profit_table = financial_metrics.build_profit_table(fact_profit)
    profit_yoy = financial_metrics.build_profit_yoy_table(profit_table)

    # Baseline (unfiltered) concentration - Executive Insights always describe the
    # approved full dataset, independent of whatever sidebar filters are active.
    baseline_cust_df = financial_metrics.customer_analysis(fact_sales, fact_sales_returns)
    baseline_cust_conc = financial_metrics.customer_concentration(baseline_cust_df)
    baseline_supp_local_df = financial_metrics.supplier_analysis_local(fact_local_purchases)
    baseline_supp_local_conc = financial_metrics.supplier_concentration(baseline_supp_local_df)
    baseline_supp_foreign_df = financial_metrics.supplier_analysis_foreign(fact_foreign_purchases)
    baseline_supp_foreign_conc = financial_metrics.supplier_concentration(baseline_supp_foreign_df)

    return {
        "raw": raw,
        "fact_sales": fact_sales,
        "sales_excluded_audit": sales_excluded_audit,
        "fact_sales_returns": fact_sales_returns,
        "sret_excluded_audit": sret_excluded_audit,
        "fact_local_purchases": fact_local_purchases,
        "lpurch_excluded_audit": lpurch_excluded_audit,
        "fact_foreign_purchases": fact_foreign_purchases,
        "fpurch_excluded_audit": fpurch_excluded_audit,
        "fact_local_purchase_returns": fact_local_purchase_returns,
        "lpret_excluded_audit": lpret_excluded_audit,
        "fact_profit": fact_profit,
        "fact_supplier_debt": fact_supplier_debt,
        "sdebt_excluded_audit": sdebt_excluded_audit,
        "fact_supplier_creditors": fact_supplier_creditors,
        "scred_excluded_audit": scred_excluded_audit,
        "dim_date": dim_date,
        "dim_customer": dim_customer,
        "dim_supplier": dim_supplier,
        "dim_cost_center": dim_cost_center,
        "dq": dq,
        "annual": annual,
        "yoy": yoy,
        "profit_table": profit_table,
        "profit_yoy": profit_yoy,
        "baseline_cust_df": baseline_cust_df,
        "baseline_cust_conc": baseline_cust_conc,
        "baseline_supp_local_df": baseline_supp_local_df,
        "baseline_supp_local_conc": baseline_supp_local_conc,
        "baseline_supp_foreign_df": baseline_supp_foreign_df,
        "baseline_supp_foreign_conc": baseline_supp_foreign_conc,
    }


def compute_comparison_period(bundle: dict, active_filters: dict):
    """
    Determines the correct "previous period" comparison for KPI-card YoY
    deltas, matching the ACTIVE filter scope exactly (bug fix - the prior
    implementation always compared the latest two full years from the
    static annual table regardless of the selected Year/Quarter, so e.g.
    selecting Year=2024+Quarter=Q1 still labeled its delta "vs 2024" while
    silently comparing full-year 2025 vs full-year 2024).

    Returns (comparison_metrics: dict | None, comparison_label: str | None).
    comparison_metrics is None when no single meaningful previous period
    exists for the current selection (e.g. the default multi-year + partial-
    quarter combination) - callers must show a neutral delta in that case,
    never a misleading one.

    Rules:
      - Exactly one year selected, full year (all 4 quarters): compare that
        year vs year-1, using the precomputed annual table.
      - Exactly one year selected, partial quarters: compare the SAME
        quarter(s) of that year vs year-1 (recomputed directly - the annual
        table only has full-year figures), keeping any active
        Customer/Supplier/Cost Center filter identical on both sides so the
        comparison is apples-to-apples.
      - Multiple years selected (including the default, all 4 - the most
        common view) - NO comparison, any quarter selection. Bug fix: an
        earlier version of this function compared the latest selected year's
        single-year annual figure against the CURRENT metric, which for a
        multi-year selection is a cumulative sum across every selected year
        - producing enormous, meaningless deltas (e.g. "+414% vs 2024" when
        the current value was actually the full 2022-2025 total, not just
        2025's). A cumulative multi-year total has no valid single "previous
        period" of the same shape to compare against, so no comparison is
        shown - matching the explicit rule that an ambiguous scope must show
        a neutral delta, never a misleading one.
    """
    years = sorted(active_filters.get("years") or [])
    quarters = sorted(active_filters.get("quarters") or [])
    full_year = len(quarters) == 4
    annual = bundle["annual"]

    if not years:
        return None, None

    if len(years) == 1:
        cur_y = years[0]
        prev_y = cur_y - 1
        if prev_y not in config.ANALYSIS_YEARS:
            return None, None
        if full_year:
            if prev_y in annual.index:
                return annual.loc[prev_y].to_dict(), str(prev_y)
            return None, None
        prev_filters = dict(active_filters, years=[prev_y])
        prev_filtered = filters_mod.apply_filters(bundle, prev_filters)
        prev_metrics = financial_metrics.compute_period_metrics(
            prev_filtered["fact_sales"], prev_filtered["fact_sales_returns"],
            prev_filtered["fact_local_purchases"], prev_filtered["fact_foreign_purchases"],
            prev_filtered["fact_local_purchase_returns"], year=None,
        )
        q_label = ", ".join(f"Q{q}" for q in quarters)
        return prev_metrics, f"{q_label} {prev_y}"

    # More than one year selected (including the default all-4 case): no
    # single meaningful previous period exists for a cumulative multi-year
    # total - see docstring.
    return None, None


def compute_filtered_bundle(bundle: dict, filtered: dict, active_filters: dict) -> dict:
    """Recomputes metrics/analyses on the currently-filtered fact tables. Cheap
    (vectorized pandas over <100k rows) - no caching needed per interaction.

    active_filters is threaded through so downstream pages can render a
    correct filtered-period subtitle and know which filters are active."""
    fs, fsr = filtered["fact_sales"], filtered["fact_sales_returns"]
    flp, ffp = filtered["fact_local_purchases"], filtered["fact_foreign_purchases"]
    flpr = filtered["fact_local_purchase_returns"]

    current_metrics = financial_metrics.compute_period_metrics(fs, fsr, flp, ffp, flpr, year=None)
    cust_df = financial_metrics.customer_analysis(fs, fsr)
    cust_conc = financial_metrics.customer_concentration(cust_df)
    supp_local_df = financial_metrics.supplier_analysis_local(flp)
    supp_local_conc = financial_metrics.supplier_concentration(supp_local_df)
    supp_foreign_df = financial_metrics.supplier_analysis_foreign(ffp)
    supp_foreign_conc = financial_metrics.supplier_concentration(supp_foreign_df)
    cash_credit_sales = financial_metrics.cash_vs_credit_sales(fs)
    cash_credit_local_purch = financial_metrics.cash_vs_credit_local_purchases(flp)
    lpret_by_cost_center = financial_metrics.local_purchase_returns_by_cost_center(flpr)
    comparison_metrics, comparison_label = compute_comparison_period(bundle, active_filters)

    return {
        "current_metrics": current_metrics,
        "cust_df": cust_df,
        "cust_conc": cust_conc,
        "supp_local_df": supp_local_df,
        "supp_local_conc": supp_local_conc,
        "supp_foreign_df": supp_foreign_df,
        "supp_foreign_conc": supp_foreign_conc,
        "cash_credit_sales": cash_credit_sales,
        "cash_credit_local_purch": cash_credit_local_purch,
        "lpret_by_cost_center": lpret_by_cost_center,
        "active_filters": active_filters,
        "comparison_metrics": comparison_metrics,
        "comparison_label": comparison_label,
    }
