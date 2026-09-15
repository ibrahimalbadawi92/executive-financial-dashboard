# -*- coding: utf-8 -*-
import pandas as pd
import streamlit as st

from src.translations import t, localize_comparison_label
from src.ui_components import (page_header, section_header, chart_section_header, kpi_from_metrics, kpi_row,
                                 disclaimer_box, insight_panel, attention_panel, selected_period_subtitle,
                                 kpi_card_html, bidi_num)
from src.kpi_metadata import get_kpi_tooltip
from src.formatting import format_money, year_range_text
from src import charts, insights as insights_mod, financial_metrics, business_calendar


def render(bundle, filtered, computed, lang):
    page_header("nav_executive_overview", lang,
                subtitle=selected_period_subtitle(computed["active_filters"], lang))

    metrics = computed["current_metrics"]
    annual = bundle["annual"]
    profit_table = bundle["profit_table"]
    years = computed["active_filters"]["years"]
    quarters = computed["active_filters"]["quarters"]
    full_year_scope = len(quarters) == 4
    profit_value = financial_metrics.profit_for_years(profit_table, years) if full_year_scope else None

    # ---- Primary KPI row (4) ----
    c1, c2, c3, c4 = kpi_row(4, first=True)
    with c1:
        kpi_from_metrics("net_sales_before_vat", metrics, lang, comparison_metrics=computed["comparison_metrics"], comparison_label=computed["comparison_label"], delta_color="normal", show_exact=False)
    with c2:
        kpi_from_metrics("net_sales_incl_vat", metrics, lang, comparison_metrics=computed["comparison_metrics"], comparison_label=computed["comparison_label"], delta_color="normal", show_exact=False)
    with c3:
        # Cumulative Profit is EXPLICITLY labeled as such whenever more than
        # one year is in scope, so it is never mistaken for a single year's
        # Profit (management requirement).
        if profit_value is None:
            profit_label, profit_display = t("profit", lang), t("profit_not_available_quarterly", lang)
            profit_tooltip = get_kpi_tooltip("profit", lang)
        elif len(years) == 1:
            profit_label = t("profit_single_year_label", lang).format(year=years[0])
            profit_display = format_money(profit_value, lang)
            profit_tooltip = get_kpi_tooltip("profit", lang)
        else:
            profit_label = t("profit_cumulative_label", lang).format(range=year_range_text(min(years), max(years), lang))
            profit_display = format_money(profit_value, lang)
            profit_tooltip = get_kpi_tooltip("profit", lang) + " " + t("profit_cumulative_note", lang)
        kpi_card_html(profit_label, bidi_num(profit_display, lang), tooltip=profit_tooltip)
    with c4:
        kpi_from_metrics("sales_return_rate_pct", metrics, lang, comparison_metrics=computed["comparison_metrics"], comparison_label=computed["comparison_label"], delta_color="inverse", show_exact=False)

    # ---- Secondary KPI row (4) ----
    c5, c6, c7, c8 = kpi_row(4)
    with c5:
        kpi_from_metrics("local_purchases_before_vat", metrics, lang, comparison_metrics=computed["comparison_metrics"], comparison_label=computed["comparison_label"], delta_color="off", show_exact=False)
    with c6:
        kpi_from_metrics("foreign_purchase_total", metrics, lang, comparison_metrics=computed["comparison_metrics"], comparison_label=computed["comparison_label"], delta_color="off", show_exact=False)
    with c7:
        kpi_from_metrics("total_purchases_before_vat", metrics, lang, comparison_metrics=computed["comparison_metrics"], comparison_label=computed["comparison_label"], delta_color="off", show_exact=False)
    with c8:
        kpi_from_metrics("net_output_vat", metrics, lang, comparison_metrics=computed["comparison_metrics"], comparison_label=computed["comparison_label"], delta_color="off", show_exact=False)

    # ---- Chart grid ----
    row1_left, row1_right = st.columns([2, 1])
    with row1_left:
        chart_section_header("monthly_sales_full_history", lang)
        st.markdown(f'<div class="efd-note-info efd-note-compact">{t("full_period_2022_2025", lang)}</div>',
                    unsafe_allow_html=True)
        monthly_series = financial_metrics.monthly_net_sales_series(bundle["fact_sales"], bundle["fact_sales_returns"])
        st.plotly_chart(
            charts.continuous_monthly_trend(monthly_series, "net_sales_before_vat", lang, "monthly_sales_full_history",
                                             show_title=False, working_days_df=business_calendar.working_days_table()),
            width="stretch",
        )
    with row1_right:
        chart_section_header("annual_performance_comparison", lang)
        st.plotly_chart(charts.annual_bar_chart(annual, "net_sales_before_vat", lang), width="stretch")

    row2_left, row2_right = st.columns(2)
    with row2_left:
        chart_section_header("local_vs_foreign_by_year", lang)
        st.plotly_chart(
            charts.grouped_bar_by_year(annual, ["local_purchases_before_vat", "foreign_purchase_total"], lang,
                                        "local_vs_foreign_by_year", show_title=False),
            width="stretch",
        )
    with row2_right:
        chart_section_header("sales_return_rate_trend", lang)
        st.plotly_chart(charts.rate_trend_chart(annual, "sales_return_rate_pct", lang, "sales_return_rate_trend",
                                                  show_title=False),
                         width="stretch")

    row3_left, row3_right = st.columns(2)
    with row3_left:
        chart_section_header("annual_profit", lang)
        st.plotly_chart(charts.annual_bar_chart(profit_table, "profit", lang, color=charts.PALETTE["positive"]),
                         width="stretch")
    with row3_right:
        section_header(t("executive_insights", lang))
        ins = insights_mod.generate_insights(
            annual, bundle["yoy"], bundle["baseline_cust_conc"], bundle["baseline_supp_local_conc"],
            profit_table, lang=lang,
        )
        insight_panel(t("executive_insights", lang), ins[:7])

    # ---- Management Attention (data-driven only) ----
    section_header(t("key_risks_attention", lang))
    attention_items = _build_attention_items(bundle, lang)
    attention_panel(t("management_attention", lang), attention_items, t("no_attention_items", lang))


def _build_attention_items(bundle, lang):
    items = []
    yoy = bundle["yoy"]
    latest_comparisons = [c for c in ["2025 vs 2024", "2024 vs 2023", "2023 vs 2022"] if c in yoy.index]
    if latest_comparisons:
        latest = latest_comparisons[0]
        pct_var = yoy.loc[latest, "net_sales_before_vat__pct_var"]
        if pd.notna(pct_var) and pct_var <= -15:
            level = "critical" if pct_var <= -25 else "warning"
            items.append({"text": t("attention_sales_decline", lang).format(
                pct=f"{abs(pct_var):.1f}", comparison=localize_comparison_label(latest, lang)),
                          "level": level})

        cur_rr = yoy.loc[latest, "sales_return_rate_pct__current"]
        prev_rr = yoy.loc[latest, "sales_return_rate_pct__previous"]
        if pd.notna(cur_rr) and pd.notna(prev_rr) and cur_rr > prev_rr:
            items.append({"text": t("attention_return_rate_rising", lang).format(
                prev_pct=f"{prev_rr:.1f}", cur_pct=f"{cur_rr:.1f}"), "level": "warning"})

    cust_conc = bundle["baseline_cust_conc"]
    if cust_conc["top5_customer_share_pct"] and cust_conc["top5_customer_share_pct"] > 30:
        items.append({"text": t("insight_customer_concentration", lang).format(
            pct=f'{cust_conc["top5_customer_share_pct"]:.1f}'), "level": "warning"})

    supp_conc = bundle["baseline_supp_local_conc"]
    if supp_conc["top5_supplier_share_pct"] and supp_conc["top5_supplier_share_pct"] > 30:
        items.append({"text": t("insight_supplier_concentration", lang).format(
            pct=f'{supp_conc["top5_supplier_share_pct"]:.1f}'), "level": "warning"})

    return items
