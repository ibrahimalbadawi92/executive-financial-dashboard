# -*- coding: utf-8 -*-
import pandas as pd
import streamlit as st

from src.translations import t, localize_comparison_label
from src.ui_components import page_header, section_header, chart_section_header, bidi_num
from src.formatting import format_money, format_money_full, format_pct, format_int, format_delta_pct
from src import charts

# True = increase is positive (green up/red down), False = increase is negative
# (inverse coloring), None = neutral/accounting indicator (always gray).
_INTERPRETATION = {
    "gross_sales_before_vat": True,
    "net_sales_before_vat": True,
    "sales_returns_before_vat": False,
    "sales_return_rate_pct": False,
    "net_output_vat": None,
    "local_purchases_before_vat": None,
    "foreign_purchase_total": None,
    "total_purchases_before_vat": None,
    "local_purchase_returns_before_vat": False,
    "sales_transaction_count": True,
    "purchase_transaction_count": None,
}

_COUNT_KPIS = {"sales_transaction_count", "purchase_transaction_count"}
_PCT_KPIS = {"sales_return_rate_pct"}


def _fmt_value(key, value, lang):
    if key in _PCT_KPIS:
        s = format_pct(value)
    elif key in _COUNT_KPIS:
        s = format_int(value)
    else:
        s = format_money_full(value, lang)
    return bidi_num(s, lang)


_localized_comparison_label = localize_comparison_label


def _variance_class(key, abs_var):
    if pd.isna(abs_var):
        return "efd-neutral"
    interp = _INTERPRETATION.get(key)
    if interp is None:
        return "efd-neutral"
    is_increase = abs_var >= 0
    good = is_increase if interp else not is_increase
    return "efd-pos" if good else "efd-neg"


def render(bundle, filtered, computed, lang):
    page_header("nav_yoy_analysis", lang, subtitle=t("yoy_global_scope_note", lang))

    yoy = bundle["yoy"]
    comparisons = list(yoy.index)
    default_idx = len(comparisons) - 2 if len(comparisons) >= 2 else 0  # "2025 vs 2024" typically

    chart_section_header("yoy_comparison_table", lang)
    chosen = st.selectbox(t("yoy", lang), comparisons, index=default_idx, key="yoy_comparison_choice",
                           format_func=lambda c: _localized_comparison_label(c, lang))

    rows_html = []
    for key in ["gross_sales_before_vat", "net_sales_before_vat", "sales_returns_before_vat", "sales_return_rate_pct",
                "net_output_vat",
                "local_purchases_before_vat", "foreign_purchase_total", "total_purchases_before_vat",
                "local_purchase_returns_before_vat",
                "sales_transaction_count", "purchase_transaction_count"]:
        cur = yoy.loc[chosen, f"{key}__current"]
        prev = yoy.loc[chosen, f"{key}__previous"]
        abs_var = yoy.loc[chosen, f"{key}__abs_var"]
        pct_var = yoy.loc[chosen, f"{key}__pct_var"]
        css_class = _variance_class(key, abs_var)
        abs_var_str = _fmt_value(key, abs_var, lang) if not pd.isna(abs_var) else "—"
        rows_html.append(
            f"<tr><td>{t(key, lang)}</td>"
            f"<td>{_fmt_value(key, cur, lang)}</td>"
            f"<td>{_fmt_value(key, prev, lang)}</td>"
            f"<td class='{css_class}'>{abs_var_str}</td>"
            f"<td class='{css_class}'>{bidi_num(format_delta_pct(pct_var), lang)}</td></tr>"
        )

    table_html = f"""
    <table class="efd-yoy-table">
      <thead><tr>
        <th></th>
        <th>{t('current_year', lang)}</th>
        <th>{t('previous_year', lang)}</th>
        <th>{t('absolute_variance', lang)}</th>
        <th>{t('pct_variance', lang)}</th>
      </tr></thead>
      <tbody>{''.join(rows_html)}</tbody>
    </table>
    """
    st.markdown(table_html, unsafe_allow_html=True)

    # ---- Profit YoY Change (approved source values only - never a margin/derived formula) ----
    st.markdown("---")
    section_header(t("profit_yoy_change", lang))
    profit_yoy = bundle["profit_yoy"]
    if len(profit_yoy):
        profit_rows = []
        for comp, row in profit_yoy.iterrows():
            css_class = "efd-pos" if row["abs_var"] >= 0 else "efd-neg"
            profit_rows.append(
                f"<tr><td>{_localized_comparison_label(comp, lang)}</td>"
                f"<td>{bidi_num(format_money_full(row['current_profit'], lang), lang)}</td>"
                f"<td>{bidi_num(format_money_full(row['previous_profit'], lang), lang)}</td>"
                f"<td class='{css_class}'>{bidi_num(format_money_full(row['abs_var'], lang), lang)}</td>"
                f"<td class='{css_class}'>{bidi_num(format_delta_pct(row['pct_var']), lang)}</td></tr>"
            )
        profit_table_html = f"""
        <table class="efd-yoy-table">
          <thead><tr>
            <th></th>
            <th>{t('current_year', lang)}</th>
            <th>{t('previous_year', lang)}</th>
            <th>{t('absolute_variance', lang)}</th>
            <th>{t('pct_variance', lang)}</th>
          </tr></thead>
          <tbody>{''.join(profit_rows)}</tbody>
        </table>
        """
        st.markdown(profit_table_html, unsafe_allow_html=True)

    st.markdown("---")
    annual = bundle["annual"]
    col_a, col_b = st.columns(2)
    with col_a:
        chart_section_header("net_sales_vs_net_purchases_trend", lang)
        st.plotly_chart(charts.grouped_bar_by_year(annual, ["net_sales_before_vat", "total_purchases_before_vat"], lang,
                                                     "net_sales_vs_net_purchases_trend", show_title=False),
                         width='stretch')
    with col_b:
        chart_section_header("annual_profit", lang)
        st.plotly_chart(charts.annual_bar_chart(bundle["profit_table"], "profit", lang, color=charts.PALETTE["positive"]),
                         width='stretch')
