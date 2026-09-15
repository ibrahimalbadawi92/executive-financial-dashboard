# -*- coding: utf-8 -*-
import streamlit as st

from src.translations import t
from src.ui_components import page_header, chart_section_header, kpi_from_metrics, kpi_row, selected_period_subtitle
from src import charts, financial_metrics, business_calendar


def render(bundle, filtered, computed, lang):
    page_header("nav_sales_performance", lang, subtitle=selected_period_subtitle(computed["active_filters"], lang))

    metrics = computed["current_metrics"]
    annual = bundle["annual"]
    fs = filtered["fact_sales"]

    c1, c2, c3, c4 = kpi_row(4, first=True)
    with c1:
        kpi_from_metrics("gross_sales_before_vat", metrics, lang, comparison_metrics=computed["comparison_metrics"], comparison_label=computed["comparison_label"], delta_color="normal")
    with c2:
        kpi_from_metrics("net_sales_before_vat", metrics, lang, comparison_metrics=computed["comparison_metrics"], comparison_label=computed["comparison_label"], delta_color="normal")
    with c3:
        kpi_from_metrics("sales_returns_before_vat", metrics, lang, comparison_metrics=computed["comparison_metrics"], comparison_label=computed["comparison_label"], delta_color="inverse")
    with c4:
        kpi_from_metrics("sales_return_rate_pct", metrics, lang, comparison_metrics=computed["comparison_metrics"], comparison_label=computed["comparison_label"], delta_color="inverse")

    c5, c6, c7 = kpi_row(3)
    with c5:
        kpi_from_metrics("sales_transaction_count", metrics, lang, comparison_metrics=computed["comparison_metrics"], comparison_label=computed["comparison_label"], delta_color="off")
    with c6:
        kpi_from_metrics("net_sales_incl_vat", metrics, lang, comparison_metrics=computed["comparison_metrics"], comparison_label=computed["comparison_label"], delta_color="normal")
    with c7:
        kpi_from_metrics("gross_output_vat", metrics, lang, comparison_metrics=computed["comparison_metrics"], comparison_label=computed["comparison_label"], delta_color="off")

    # "One clear 4-year monthly comparison chart" (management request) - every
    # calendar month lines up at the same x position across all 4 year lines,
    # with Working Days added to the hover for context.
    chart_section_header("monthly_net_sales_trend", lang)
    st.plotly_chart(
        charts.monthly_trend_multi_year(fs, "net_amount", lang, "monthly_net_sales_trend", show_title=False,
                                         working_days_df=business_calendar.working_days_table()),
        width='stretch', key="sales_perf_monthly_net_sales_trend",
    )

    col_a, col_b = st.columns(2)
    with col_a:
        chart_section_header("annual_performance_comparison", lang)
        st.plotly_chart(charts.annual_bar_chart(annual, "net_sales_before_vat", lang), width='stretch')
    with col_b:
        chart_section_header("gross_sales_vs_returns", lang)
        st.plotly_chart(
            charts.grouped_bar_by_year(annual, ["gross_sales_before_vat", "sales_returns_before_vat"], lang,
                                        "gross_sales_vs_returns", show_title=False),
            width='stretch',
        )

    col_c, col_d = st.columns(2)
    with col_c:
        chart_section_header("sales_by_transaction_type", lang)
        mix = financial_metrics.cash_vs_credit_sales(fs)
        key_labels = {"cash_sale": "cash_sales", "credit_sale": "credit_sales", "service": "service_sales", "other": "filter_all"}
        if mix:
            st.plotly_chart(charts.type_mix_bar(mix, lang, t("sales_by_transaction_type", lang), key_labels,
                                                  show_title=False),
                             width='stretch')
    with col_d:
        chart_section_header("sales_quantity_trend", lang)
        st.plotly_chart(charts.monthly_trend_multi_year(fs, "quantity", lang, "sales_quantity_trend", agg="sum",
                                                          show_title=False),
                         width='stretch', key="sales_perf_sales_quantity_trend")
