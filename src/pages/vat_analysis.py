# -*- coding: utf-8 -*-
import streamlit as st

from src.translations import t
from src.ui_components import page_header, chart_section_header, kpi_from_metrics, kpi_row, disclaimer_box, \
    selected_period_subtitle
from src import charts


def render(bundle, filtered, computed, lang):
    page_header("nav_vat_analysis", lang, subtitle=selected_period_subtitle(computed["active_filters"], lang))
    disclaimer_box("vat_disclaimer", lang, kind="info")

    metrics = computed["current_metrics"]
    annual = bundle["annual"]
    fs = filtered["fact_sales"]

    # Output/Sales VAT only - Net Input VAT and Indicative VAT Position are
    # intentionally not shown (management request). Raw purchase-tax figures
    # remain available on Purchasing Performance and Data Quality.
    c1, c2, c3 = kpi_row(3, first=True)
    with c1:
        kpi_from_metrics("gross_output_vat", metrics, lang, comparison_metrics=computed["comparison_metrics"], comparison_label=computed["comparison_label"], delta_color="off")
    with c2:
        kpi_from_metrics("sales_return_vat", metrics, lang, comparison_metrics=computed["comparison_metrics"], comparison_label=computed["comparison_label"], delta_color="off")
    with c3:
        kpi_from_metrics("net_output_vat", metrics, lang, comparison_metrics=computed["comparison_metrics"], comparison_label=computed["comparison_label"], delta_color="off")

    chart_section_header("vat_annual_comparison", lang)
    st.plotly_chart(charts.grouped_bar_by_year(annual, ["gross_output_vat", "sales_return_vat", "net_output_vat"],
                                                lang, "vat_annual_comparison", show_title=False),
                     width='stretch')

    chart_section_header("vat_monthly_trend", lang)
    st.plotly_chart(charts.monthly_trend_multi_year(fs, "vat_amount", lang, "vat_monthly_trend", show_title=False),
                     width='stretch')
