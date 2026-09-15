# -*- coding: utf-8 -*-
"""
Deterministic executive insights - no AI/LLM text generation. Every insight
is computed directly from the same annual/YoY/concentration/profit tables
produced by financial_metrics.py, then rendered through translations.t() so
it is automatically bilingual and never duplicated between languages.
"""
import numpy as np

from src.translations import t, localize_comparison_label
from src.utils import safe_pct
from src.formatting import bidi_isolate
from src import financial_metrics


def _fmt_money(v):
    return f"{v:,.0f}"


def _fmt_pct(v):
    return f"{v:,.1f}"


def _fmt_money_signed(v, lang):
    """abs()-free money value, bidi-isolated for RTL so a negative sign never
    visually relocates to the end of the number inside Arabic sentence text
    (confirmed bug - was previously only fixed on KPI cards), for the
    "(SAR {value})" absolute-variance figure."""
    s = f"{v:,.0f}"
    return bidi_isolate(s) if lang == "ar" else s


def _fmt_money_growth(v, lang):
    """Same as _fmt_money_signed but with an explicit '+' prefix on a
    non-negative value (matches the approved narrative style for the
    strongest-growth insight, e.g. '+412,500') - bidi-isolated for RTL for
    the same reason as _fmt_money_signed."""
    s = f"{v:,.0f}"
    if v >= 0:
        s = f"+{s}"
    return bidi_isolate(s) if lang == "ar" else s


def generate_insights(annual_df, yoy_df, customer_concentration, local_supplier_concentration,
                       profit_table, lang="en") -> list[dict]:
    """
    Returns a list of {key, text} insight dicts for the given language.
    annual_df: output of financial_metrics.build_annual_table (indexed by year + 'ALL_PERIOD_2022_2025')
    yoy_df: output of financial_metrics.build_yoy_table
    local_supplier_concentration: financial_metrics.supplier_concentration() on Local Purchases only
    profit_table: financial_metrics.build_profit_table() output (approved source, never derived here)
    """
    insights = []
    years_df = annual_df.drop(index="ALL_PERIOD_2022_2025", errors="ignore")

    # Best / weakest sales year
    best_year = years_df["net_sales_before_vat"].idxmax()
    weakest_year = years_df["net_sales_before_vat"].idxmin()
    insights.append({"key": "insight_best_sales_year", "text": t("insight_best_sales_year", lang).format(
        year=best_year, value=_fmt_money(years_df.loc[best_year, "net_sales_before_vat"]))})
    insights.append({"key": "insight_weakest_sales_year", "text": t("insight_weakest_sales_year", lang).format(
        year=weakest_year, value=_fmt_money(years_df.loc[weakest_year, "net_sales_before_vat"]))})

    # Largest YoY growth / decline in Net Sales (consecutive-year comparisons only)
    consecutive = yoy_df[yoy_df.index.isin(["2023 vs 2022", "2024 vs 2023", "2025 vs 2024"])]
    if not consecutive.empty:
        pct_col = "net_sales_before_vat__pct_var"
        abs_col = "net_sales_before_vat__abs_var"
        best_comp = consecutive[pct_col].idxmax()
        worst_comp = consecutive[pct_col].idxmin()
        insights.append({"key": "insight_highest_yoy_sales_growth", "text": t("insight_highest_yoy_sales_growth", lang).format(
            comparison=localize_comparison_label(best_comp, lang), pct=_fmt_pct(consecutive.loc[best_comp, pct_col]),
            value=_fmt_money_growth(consecutive.loc[best_comp, abs_col], lang))})
        insights.append({"key": "insight_largest_sales_decline", "text": t("insight_largest_sales_decline", lang).format(
            comparison=localize_comparison_label(worst_comp, lang), pct=_fmt_pct(abs(consecutive.loc[worst_comp, pct_col])),
            value=_fmt_money_signed(consecutive.loc[worst_comp, abs_col], lang))})

    # Return rate extremes
    hi_rr_year = years_df["sales_return_rate_pct"].idxmax()
    lo_rr_year = years_df["sales_return_rate_pct"].idxmin()
    insights.append({"key": "insight_highest_return_rate_year", "text": t("insight_highest_return_rate_year", lang).format(
        year=hi_rr_year, pct=_fmt_pct(years_df.loc[hi_rr_year, "sales_return_rate_pct"]))})
    insights.append({"key": "insight_lowest_return_rate_year", "text": t("insight_lowest_return_rate_year", lang).format(
        year=lo_rr_year, pct=_fmt_pct(years_df.loc[lo_rr_year, "sales_return_rate_pct"]))})

    # Highest purchasing year (Total Purchases = Local + Foreign)
    hi_purch_year = years_df["total_purchases_before_vat"].idxmax()
    insights.append({"key": "insight_highest_purchasing_year", "text": t("insight_highest_purchasing_year", lang).format(
        year=hi_purch_year, value=_fmt_money(years_df.loc[hi_purch_year, "total_purchases_before_vat"]))})

    # Concentration risk
    insights.append({"key": "insight_customer_concentration", "text": t("insight_customer_concentration", lang).format(
        pct=_fmt_pct(customer_concentration["top5_customer_share_pct"]))})
    insights.append({"key": "insight_supplier_concentration", "text": t("insight_supplier_concentration", lang).format(
        pct=_fmt_pct(local_supplier_concentration["top5_supplier_share_pct"]))})
    insights.append({"key": "insight_cash_walkin_dominance", "text": t("insight_cash_walkin_dominance", lang).format(
        pct=_fmt_pct(customer_concentration["cash_walkin_share_of_all_sales_pct"]))})

    # Latest-year Profit (approved source only - never derived here)
    latest_year = max(years_df.index)
    latest_profit = financial_metrics.profit_for_year(profit_table, latest_year)
    if latest_profit is not None:
        insights.append({"key": "insight_profit_latest_year", "text": t("insight_profit_latest_year", lang).format(
            year=latest_year, value=_fmt_money(latest_profit))})

    # 4-year direction (2025 vs 2022)
    if 2022 in years_df.index and 2025 in years_df.index:
        v2022 = years_df.loc[2022, "net_sales_before_vat"]
        v2025 = years_df.loc[2025, "net_sales_before_vat"]
        pct = safe_pct(v2025 - v2022, v2022)
        key = "insight_four_year_direction_up" if v2025 >= v2022 else "insight_four_year_direction_down"
        insights.append({"key": key, "text": t(key, lang).format(
            pct=_fmt_pct(abs(pct)), value_2022=_fmt_money(v2022), value_2025=_fmt_money(v2025))})

    return insights
