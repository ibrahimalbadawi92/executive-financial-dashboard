# -*- coding: utf-8 -*-
import streamlit as st

from src.translations import t
from src.ui_components import page_header, chart_section_header, raw_note_box, kpi_card_html, selected_period_subtitle, bidi_num
from src.kpi_metadata import get_kpi_tooltip
from src.formatting import format_pct, format_int, format_money
from src import charts


def render(bundle, filtered, computed, lang):
    page_header("nav_customers_suppliers", lang, subtitle=selected_period_subtitle(computed["active_filters"], lang))

    # ============================== CUSTOMERS ==============================
    chart_section_header("top_customers", lang)
    cust_df = computed["cust_df"]
    conc = computed["cust_conc"]

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        kpi_card_html(t("top5_share", lang), format_pct(conc["top5_customer_share_pct"]),
                      tooltip=get_kpi_tooltip("top5_customer_share_pct", lang))
    with c2:
        kpi_card_html(t("top10_share", lang), format_pct(conc["top10_customer_share_pct"]),
                      tooltip=get_kpi_tooltip("top10_customer_share_pct", lang))
    with c3:
        kpi_card_html(t("cash_walkin_customers", lang), format_money(conc["cash_walkin_net_sales"], lang),
                      tooltip=t("cash_walkin_note", lang))
    with c4:
        kpi_card_html(t("cash_walkin_customers", lang) + " %", format_pct(conc["cash_walkin_share_of_all_sales_pct"]),
                      tooltip=t("cash_walkin_note", lang))

    raw_note_box(t("cash_walkin_note", lang), kind="info")

    named = cust_df[~cust_df["is_generic_cash_customer"]].copy()
    col_a, col_b = st.columns(2)
    with col_a:
        chart_section_header("top_customers_net_sales", lang)
        if len(named):
            st.plotly_chart(
                charts.horizontal_top_n_bar(named.sort_values("net_sales_before_vat", ascending=False),
                                             "customer_name_original", "net_sales_before_vat", lang,
                                             t("top_customers_net_sales", lang), n=10, show_title=False),
                width='stretch',
            )
    with col_b:
        chart_section_header("top_customers_gross_sales", lang)
        if len(named):
            st.plotly_chart(
                charts.horizontal_top_n_bar(named.sort_values("gross_sales_before_vat", ascending=False),
                                             "customer_name_original", "gross_sales_before_vat", lang,
                                             t("top_customers_gross_sales", lang), n=10, show_title=False),
                width='stretch',
            )

    col_c, col_d = st.columns(2)
    with col_c:
        chart_section_header("top_customers_returns", lang)
        with_returns = named[named["sales_returns_before_vat"] > 0].sort_values("sales_returns_before_vat", ascending=False)
        if len(with_returns):
            st.plotly_chart(
                charts.horizontal_top_n_bar(with_returns, "customer_name_original", "sales_returns_before_vat", lang,
                                             t("top_customers_returns", lang), n=10, show_title=False),
                width='stretch',
            )
        else:
            raw_note_box(t("no_data_for_filters", lang), kind="info")
    with col_d:
        chart_section_header("customer_return_rate", lang)
        st.dataframe(
            with_returns[["customer_name_original", "return_rate_pct"]].head(10).rename(
                columns={"customer_name_original": t("filter_customer", lang), "return_rate_pct": t("customer_return_rate", lang)}
            ).style.format({t("customer_return_rate", lang): "{:.1f}%"}),
            width='stretch', hide_index=True,
        )

    st.markdown("---")

    # ============================== SUPPLIERS (Local vs Foreign kept separate) ==============================
    chart_section_header("top_suppliers", lang)
    supp_local_df = computed["supp_local_df"]
    supp_local_conc = computed["supp_local_conc"]
    supp_foreign_df = computed["supp_foreign_df"]
    supp_foreign_conc = computed["supp_foreign_conc"]

    s1, s2, s3, s4 = st.columns(4)
    with s1:
        kpi_card_html(t("local_purchases_by_supplier", lang) + " - " + t("supplier_count", lang),
                      format_int(supp_local_conc["supplier_count"]), tooltip=get_kpi_tooltip("supplier_count", lang))
    with s2:
        kpi_card_html(t("local_purchases_by_supplier", lang) + " - " + t("top5_share", lang),
                      format_pct(supp_local_conc["top5_supplier_share_pct"]),
                      tooltip=get_kpi_tooltip("top5_supplier_share_pct", lang))
    with s3:
        kpi_card_html(t("foreign_purchases_by_supplier", lang) + " - " + t("supplier_count", lang),
                      format_int(supp_foreign_conc["supplier_count"]), tooltip=get_kpi_tooltip("supplier_count", lang))
    with s4:
        kpi_card_html(t("foreign_purchases_by_supplier", lang) + " - " + t("top5_share", lang),
                      format_pct(supp_foreign_conc["top5_supplier_share_pct"]),
                      tooltip=get_kpi_tooltip("top5_supplier_share_pct", lang))

    if supp_local_conc.get("generic_supplier_value"):
        generic_row = supp_local_df[supp_local_df["is_generic_supplier"]]
        generic_count = int(generic_row["transaction_count"].iloc[0]) if len(generic_row) else 0
        raw_note_box(t("generic_supplier_note", lang).format(count=generic_count), kind="info", compact=True)

    col_e, col_f = st.columns(2)
    with col_e:
        chart_section_header("local_purchases_by_supplier", lang)
        if len(supp_local_df):
            st.plotly_chart(
                charts.horizontal_top_n_bar(supp_local_df, "supplier_name_original", "purchase_value_before_vat",
                                             lang, t("local_purchases_by_supplier", lang), n=10, show_title=False),
                width='stretch',
            )
    with col_f:
        chart_section_header("foreign_purchases_by_supplier", lang)
        if len(supp_foreign_df):
            st.plotly_chart(
                charts.horizontal_top_n_bar(supp_foreign_df, "supplier_name_original", "purchase_value_before_vat",
                                             lang, t("foreign_purchases_by_supplier", lang), n=10, show_title=False),
                width='stretch',
            )
