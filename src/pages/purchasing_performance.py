# -*- coding: utf-8 -*-
import streamlit as st

from src.translations import t
from src.ui_components import page_header, chart_section_header, kpi_from_metrics, kpi_row, kpi_card_html, \
    selected_period_subtitle, raw_note_box
from src.kpi_metadata import get_kpi_tooltip
from src.formatting import format_pct, format_int
from src import charts, financial_metrics


def render(bundle, filtered, computed, lang):
    page_header("nav_purchasing_performance", lang,
                subtitle=selected_period_subtitle(computed["active_filters"], lang))

    metrics = computed["current_metrics"]
    annual = bundle["annual"]
    flp = filtered["fact_local_purchases"]
    ffp = filtered["fact_foreign_purchases"]

    # Local and Foreign Purchases are kept as clearly separate measures
    # throughout this page (management request) - never combined without
    # showing both components.
    c1, c2, c3, c4 = kpi_row(4, first=True)
    with c1:
        kpi_from_metrics("local_purchases_before_vat", metrics, lang, comparison_metrics=computed["comparison_metrics"], comparison_label=computed["comparison_label"], delta_color="off")
    with c2:
        kpi_from_metrics("foreign_purchase_base", metrics, lang, comparison_metrics=computed["comparison_metrics"], comparison_label=computed["comparison_label"], delta_color="off")
    with c3:
        kpi_from_metrics("foreign_purchase_additional_cost", metrics, lang, comparison_metrics=computed["comparison_metrics"], comparison_label=computed["comparison_label"], delta_color="off")
    with c4:
        kpi_from_metrics("foreign_purchase_total", metrics, lang, comparison_metrics=computed["comparison_metrics"], comparison_label=computed["comparison_label"], delta_color="off")

    c5, c6, c7, c8 = kpi_row(4)
    with c5:
        kpi_from_metrics("total_purchases_before_vat", metrics, lang, comparison_metrics=computed["comparison_metrics"], comparison_label=computed["comparison_label"], delta_color="off")
    with c6:
        kpi_from_metrics("local_purchase_vat", metrics, lang, comparison_metrics=computed["comparison_metrics"], comparison_label=computed["comparison_label"], delta_color="off")
    with c7:
        kpi_from_metrics("local_purchases_incl_vat", metrics, lang, comparison_metrics=computed["comparison_metrics"], comparison_label=computed["comparison_label"], delta_color="off")
    with c8:
        kpi_from_metrics("purchase_transaction_count", metrics, lang, comparison_metrics=computed["comparison_metrics"], comparison_label=computed["comparison_label"], delta_color="off")

    chart_section_header("local_vs_foreign_by_month", lang)
    st.plotly_chart(
        charts.dual_series_monthly_trend(
            flp, "purchase_before_vat", t("local_purchases_before_vat", lang),
            ffp, "purchase_total_before_vat", t("foreign_purchase_total", lang),
            lang, "local_vs_foreign_by_month", show_title=False,
        ),
        width='stretch',
    )

    col_a, col_b = st.columns(2)
    with col_a:
        chart_section_header("local_vs_foreign_by_year", lang)
        st.plotly_chart(
            charts.grouped_bar_by_year(annual, ["local_purchases_before_vat", "foreign_purchase_total"], lang,
                                        "local_vs_foreign_by_year", show_title=False),
            width='stretch',
        )
    with col_b:
        chart_section_header("local_purchases_by_type", lang)
        mix = financial_metrics.cash_vs_credit_local_purchases(flp)
        key_labels = {"cash_purchase": "cash_purchases", "credit_purchase": "credit_purchases", "other": "filter_all"}
        if mix:
            st.plotly_chart(charts.type_mix_bar(mix, lang, t("local_purchases_by_type", lang), key_labels,
                                                  show_title=False),
                             width='stretch')

    col_c, col_d = st.columns(2)
    with col_c:
        chart_section_header("foreign_purchases_by_supplier", lang)
        supp_foreign_df = computed["supp_foreign_df"]
        if len(supp_foreign_df):
            st.plotly_chart(
                charts.horizontal_top_n_bar(supp_foreign_df, "supplier_name_original", "purchase_value_before_vat",
                                             lang, t("foreign_purchases_by_supplier", lang), n=10, show_title=False),
                width='stretch',
            )
    with col_d:
        chart_section_header("local_purchases_by_supplier", lang)
        supp_local_df = computed["supp_local_df"]
        if len(supp_local_df):
            st.plotly_chart(
                charts.horizontal_top_n_bar(supp_local_df, "supplier_name_original", "purchase_value_before_vat",
                                             lang, t("local_purchases_by_supplier", lang), n=10, show_title=False),
                width='stretch',
            )

    concentration_col_a, concentration_col_b = st.columns(2)
    with concentration_col_a:
        chart_section_header("local_supplier_concentration", lang)
        local_conc = computed["supp_local_conc"]
        lc1, lc2, lc3 = st.columns(3)
        with lc1:
            kpi_card_html(t("top5_share", lang), format_pct(local_conc["top5_supplier_share_pct"]),
                          tooltip=get_kpi_tooltip("top5_supplier_share_pct", lang))
        with lc2:
            kpi_card_html(t("top10_share", lang), format_pct(local_conc["top10_supplier_share_pct"]),
                          tooltip=get_kpi_tooltip("top10_supplier_share_pct", lang))
        with lc3:
            kpi_card_html(t("supplier_count", lang), format_int(local_conc["supplier_count"]),
                          tooltip=get_kpi_tooltip("supplier_count", lang))
        if local_conc.get("generic_supplier_value"):
            supp_local_df = computed["supp_local_df"]
            generic_row = supp_local_df[supp_local_df["is_generic_supplier"]]
            generic_count = int(generic_row["transaction_count"].iloc[0]) if len(generic_row) else 0
            raw_note_box(t("generic_supplier_note", lang).format(count=generic_count), kind="info", compact=True)
    with concentration_col_b:
        chart_section_header("foreign_supplier_concentration", lang)
        foreign_conc = computed["supp_foreign_conc"]
        fc1, fc2, fc3 = st.columns(3)
        with fc1:
            kpi_card_html(t("top5_share", lang), format_pct(foreign_conc["top5_supplier_share_pct"]),
                          tooltip=get_kpi_tooltip("top5_supplier_share_pct", lang))
        with fc2:
            kpi_card_html(t("top10_share", lang), format_pct(foreign_conc["top10_supplier_share_pct"]),
                          tooltip=get_kpi_tooltip("top10_supplier_share_pct", lang))
        with fc3:
            kpi_card_html(t("supplier_count", lang), format_int(foreign_conc["supplier_count"]),
                          tooltip=get_kpi_tooltip("supplier_count", lang))
