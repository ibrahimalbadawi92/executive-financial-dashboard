# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd

from src.translations import t
from src.ui_components import page_header, section_header, chart_section_header, kpi_from_metrics, kpi_row, \
    raw_note_box, kpi_card_html, selected_period_subtitle
from src.kpi_metadata import get_kpi_tooltip
from src.formatting import format_money, format_pct, format_int
from src import charts, financial_metrics


def render(bundle, filtered, computed, lang):
    page_header("nav_returns_analysis", lang, subtitle=selected_period_subtitle(computed["active_filters"], lang))

    metrics = computed["current_metrics"]
    annual = bundle["annual"]
    fsr = filtered["fact_sales_returns"]
    flpr = filtered["fact_local_purchase_returns"]

    # ============================== SALES RETURNS ==============================
    section_header(t("sales_returns_section_title", lang))
    c1, c2, c3 = kpi_row(3, first=True)
    with c1:
        kpi_from_metrics("sales_returns_before_vat", metrics, lang, comparison_metrics=computed["comparison_metrics"], comparison_label=computed["comparison_label"], delta_color="inverse",
                          tooltip_key="sales_return_link_note")
    with c2:
        kpi_from_metrics("sales_return_rate_pct", metrics, lang, comparison_metrics=computed["comparison_metrics"], comparison_label=computed["comparison_label"], delta_color="inverse")
    with c3:
        qty = fsr["quantity"].sum() if len(fsr) else 0.0
        kpi_card_html(t("sales_returns_quantity_label", lang), format_int(qty),
                      tooltip=get_kpi_tooltip("sales_returns_quantity", lang))

    col_a, col_b = st.columns(2)
    with col_a:
        chart_section_header("monthly_trend_sales_returns", lang)
        st.plotly_chart(charts.monthly_trend_multi_year(fsr, "return_value_before_vat", lang,
                                                          "monthly_trend_sales_returns", show_title=False),
                         width='stretch')
    with col_b:
        chart_section_header("annual_trend_sales_returns", lang)
        st.plotly_chart(charts.annual_bar_chart(annual, "sales_returns_before_vat", lang, color=charts.PALETTE["negative"]),
                         width='stretch')

    chart_section_header("customers_highest_returns", lang)
    if len(fsr):
        by_cust = fsr[~fsr["is_generic_cash_customer"]].groupby("customer_name_original")["return_value_before_vat"].sum()
        by_cust = by_cust.sort_values(ascending=False).reset_index().rename(
            columns={"customer_name_original": "customer", "return_value_before_vat": "value"})
        if len(by_cust):
            st.plotly_chart(charts.horizontal_top_n_bar(by_cust, "customer", "value", lang,
                                                          t("customers_highest_returns", lang), n=10,
                                                          show_title=False),
                             width='stretch')
        else:
            raw_note_box(t("no_data_for_filters", lang), kind="info")
    else:
        raw_note_box(t("no_data_for_filters", lang), kind="info")

    chart_section_header("original_sale_match_status", lang)
    if len(fsr) and "best_effort_match_status" in fsr.columns:
        # Methodology note (never used for financial totals) lives in the
        # section-header popover above, keeping this executive page focused
        # on the numbers; full detail is also on the Data Quality page.
        status_labels = {"Best-Effort-Matched": "match_matched", "Unmatched": "match_unmatched", "Ambiguous": "match_ambiguous"}
        counts = fsr["best_effort_match_status"].value_counts()
        cols = st.columns(len(counts) if len(counts) else 1)
        for col, (status, n) in zip(cols, counts.items()):
            with col:
                key = status_labels.get(status, status)
                kpi_card_html(t(key, lang), format_int(n), tooltip=get_kpi_tooltip(key, lang))

    st.markdown("---")

    # ============================== LOCAL PURCHASE RETURNS ==============================
    section_header(t("purchase_returns_section_title", lang))
    c4, c5, c6 = kpi_row(3, first=True)
    with c4:
        kpi_from_metrics("local_purchase_returns_before_vat", metrics, lang, comparison_metrics=computed["comparison_metrics"], comparison_label=computed["comparison_label"], delta_color="off",
                          tooltip_key="purchase_return_no_invoice_link_note")
    with c5:
        kpi_from_metrics("local_purchase_returns_vat", metrics, lang, comparison_metrics=computed["comparison_metrics"], comparison_label=computed["comparison_label"], delta_color="off")
    with c6:
        qty2 = flpr["quantity"].sum() if len(flpr) else 0.0
        kpi_card_html(t("purchase_returns_quantity_label", lang), format_int(qty2),
                      tooltip=get_kpi_tooltip("purchase_returns_quantity", lang))

    col_c, col_d = st.columns(2)
    with col_c:
        chart_section_header("monthly_trend_purchase_returns", lang)
        st.plotly_chart(charts.monthly_trend_multi_year(flpr, "return_value_before_vat", lang,
                                                          "monthly_trend_purchase_returns", show_title=False),
                         width='stretch')
    with col_d:
        chart_section_header("annual_trend_purchase_returns", lang)
        st.plotly_chart(charts.annual_bar_chart(annual, "local_purchase_returns_before_vat", lang, color=charts.PALETTE["warning"]),
                         width='stretch')

    col_e, col_f = st.columns(2)
    with col_e:
        chart_section_header("local_purchase_returns_by_cost_center", lang)
        by_cc = financial_metrics.local_purchase_returns_by_cost_center(flpr)
        if len(by_cc):
            st.plotly_chart(charts.horizontal_top_n_bar(by_cc, "cost_center_name", "return_value_before_vat", lang,
                                                          t("local_purchase_returns_by_cost_center", lang), n=10,
                                                          show_title=False),
                             width='stretch')
    with col_f:
        chart_section_header("purchase_returns_by_type", lang)
        if len(flpr):
            mix = flpr.groupby("normalized_movement_type")["return_value_before_vat"].sum().to_dict()
            # Confirmed bug fix: this chart was reusing SALES movement-type
            # labels ("Cash Sales"/"Credit Sales") on a Purchase Returns
            # visual - audited the actual نوع الحركة source values (مردود
            # نقدي / مردود أجل) and use accurate, purchase-return-specific
            # labels instead. Never reuse Sales labels on a Purchase Return
            # chart again.
            key_labels = {"cash_return": "cash_return", "credit_return": "credit_return", "other": "filter_all"}
            st.plotly_chart(charts.type_mix_bar(mix, lang, t("purchase_returns_by_type", lang), key_labels,
                                                  show_title=False),
                             width='stretch')
