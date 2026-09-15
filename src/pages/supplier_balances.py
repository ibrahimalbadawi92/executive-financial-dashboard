# -*- coding: utf-8 -*-
"""
Supplier Balances - point-in-time snapshots from the source workbook
(مديونية الموردين / دائنين الموردين). No transaction date exists on either
sheet, so this page is intentionally NOT affected by the Year/Quarter
filters (see selected_period_subtitle usage below - omitted on purpose).
Debt and Creditor totals are shown separately, never netted, because their
sign conventions have not been confirmed as directly comparable (see
config/data_cleaning/validations docstrings and the note boxes below).
"""
import pandas as pd
import streamlit as st

from src.translations import t
from src.ui_components import page_header, section_header, chart_section_header, kpi_card_html, raw_note_box, bidi_num
from src.kpi_metadata import get_kpi_tooltip
from src.formatting import format_money
from src import charts, financial_metrics


def _formatted_balance_table(df: pd.DataFrame, lang: str) -> pd.DataFrame:
    """
    Confirmed formatting bug fix: raw source floats (e.g. 12345.6789) were
    shown unformatted in the table. Comma-grouped, 2-decimal display strings
    - internal precision is untouched (this formats a display COPY only),
    and negative values (Creditor balances) keep their sign exactly as
    sourced. st.dataframe renders plain text per cell (not HTML), so no
    bidi-isolation markup is used here - Streamlit's dataframe widget
    left-aligns numeric-looking cell content regardless of page direction,
    which does not exhibit the same RTL sign-relocation issue as raw HTML.
    """
    out = df[["supplier_name_original", "currency", "foreign_currency_amount", "local_currency_amount"]].copy()
    out["foreign_currency_amount"] = out["foreign_currency_amount"].apply(
        lambda v: f"{v:,.2f}" if pd.notna(v) else "—")
    out["local_currency_amount"] = out["local_currency_amount"].apply(
        lambda v: f"{v:,.2f}" if pd.notna(v) else "—")
    return out.rename(columns={
        "supplier_name_original": t("filter_supplier", lang),
        "currency": t("currency_col", lang),
        "foreign_currency_amount": t("foreign_currency_amount_col", lang),
        "local_currency_amount": t("local_currency_amount_col", lang),
    })


def render(bundle, filtered, computed, lang):
    page_header("nav_supplier_balances", lang, subtitle=t("supplier_balance_snapshot_note", lang))

    fact_debt = bundle["fact_supplier_debt"]
    fact_cred = bundle["fact_supplier_creditors"]
    debt_summary = financial_metrics.supplier_balance_summary(fact_debt)
    cred_summary = financial_metrics.supplier_balance_summary(fact_cred)

    c1, c2 = st.columns(2)
    with c1:
        kpi_card_html(t("total_supplier_debt", lang), bidi_num(format_money(debt_summary["total_local_currency"], lang), lang),
                      tooltip=get_kpi_tooltip("total_supplier_debt", lang))
    with c2:
        kpi_card_html(t("total_supplier_credit_balance", lang), bidi_num(format_money(cred_summary["total_local_currency"], lang), lang),
                      tooltip=get_kpi_tooltip("total_supplier_credit_balance", lang))

    raw_note_box(t("supplier_balance_no_net_note", lang), kind="info")

    st.markdown("---")
    section_header(t("supplier_debt_section", lang))
    col_a, col_b = st.columns(2)
    with col_a:
        chart_section_header("top_supplier_debts", lang)
        if len(fact_debt):
            st.plotly_chart(
                charts.horizontal_top_n_bar(fact_debt.sort_values("local_currency_amount", ascending=False),
                                             "supplier_name_original", "local_currency_amount", lang,
                                             t("top_supplier_debts", lang), n=10, show_title=False),
                width='stretch',
            )
    with col_b:
        st.dataframe(_formatted_balance_table(fact_debt, lang), width='stretch', hide_index=True)

    st.markdown("---")
    section_header(t("supplier_creditors_section", lang))
    col_c, col_d = st.columns(2)
    with col_c:
        chart_section_header("top_supplier_credits", lang)
        if len(fact_cred):
            # Sort by magnitude (most negative = largest creditor exposure) while
            # keeping the source sign exactly as reported in the displayed value.
            ranked = fact_cred.reindex(fact_cred["local_currency_amount"].abs().sort_values(ascending=False).index)
            st.plotly_chart(
                charts.horizontal_top_n_bar(ranked, "supplier_name_original", "local_currency_amount", lang,
                                             t("top_supplier_credits", lang), n=10, show_title=False),
                width='stretch',
            )
    with col_d:
        st.dataframe(_formatted_balance_table(fact_cred, lang), width='stretch', hide_index=True)
