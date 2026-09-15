# -*- coding: utf-8 -*-
import streamlit as st

from src.translations import t
from src.ui_components import page_header, section_header, dq_status_badge, raw_note_box, kpi_row
from src.formatting import format_int, format_pct, format_money
from src.chart_metadata import get_chart_tooltip
from src import charts


def render(bundle, filtered, computed, lang):
    page_header("nav_data_quality", lang, subtitle=t("data_quality_global_scope_note", lang))

    dq = bundle["dq"]
    total_source = sum(dq["total_source_records"].values())

    recon = dq["reconciliation"]
    sheets = ["sales", "sales_returns", "local_purchases", "foreign_purchases", "local_purchase_returns"]
    checked_total = sum(recon[s]["total_rows_checked"] for s in sheets)
    valid_total = sum(recon[s]["valid"] for s in sheets)
    review_total = sum(recon[s]["reconciliation_review"] for s in sheets)
    success_rate = (valid_total / checked_total * 100) if checked_total else None

    exclusions = dq["exclusions"]
    total_exclusions = sum(exclusions[s]["rows_excluded_from_analytical_totals"] for s in sheets)

    section_header(t("data_quality_scorecard", lang))
    c1, c2, c3, c4 = kpi_row(4, first=True)
    with c1:
        dq_status_badge(t("total_records", lang), total_source, kind="valid",
                         help_text=get_chart_tooltip("total_records", lang))
    with c2:
        dq_status_badge(t("valid_records", lang), valid_total, kind="valid",
                         help_text=get_chart_tooltip("valid_records", lang))
    with c3:
        dq_status_badge(t("warning_records", lang), review_total, kind="warning",
                         help_text=get_chart_tooltip("warning_records", lang))
    with c4:
        dq_status_badge(t("analytical_exclusions", lang), total_exclusions, kind="critical",
                         help_text=get_chart_tooltip("analytical_exclusions", lang))

    c5, c6 = kpi_row(2)
    with c5:
        dq_status_badge(t("reconciliation_review_records", lang), review_total, kind="warning",
                         help_text=get_chart_tooltip("reconciliation_review_records", lang))
    with c6:
        dq_status_badge(t("reconciliation_success_rate", lang), format_pct(success_rate), kind="valid",
                         help_text=get_chart_tooltip("reconciliation_success_rate", lang))

    st.markdown("---")
    section_header(t("reconciliation_summary", lang))

    counts_by_sheet = {
        t("sales_sheet", lang): {"Valid": recon["sales"]["valid"], "Reconciliation-Review": recon["sales"]["reconciliation_review"]},
        t("sales_returns_sheet", lang): {"Valid": recon["sales_returns"]["valid"], "Reconciliation-Review": recon["sales_returns"]["reconciliation_review"]},
        t("local_purchases_before_vat", lang): {"Valid": recon["local_purchases"]["valid"], "Reconciliation-Review": recon["local_purchases"]["reconciliation_review"]},
        t("foreign_purchase_total", lang): {"Valid": recon["foreign_purchases"]["valid"], "Reconciliation-Review": recon["foreign_purchases"]["reconciliation_review"]},
        t("purchase_returns_sheet", lang): {"Valid": recon["local_purchase_returns"]["valid"], "Reconciliation-Review": recon["local_purchase_returns"]["reconciliation_review"]},
    }
    st.plotly_chart(charts.reconciliation_status_bar(counts_by_sheet, lang, t("reconciliation_summary", lang),
                                                        show_title=False),
                     width='stretch')

    st.markdown("---")
    section_header(t("sales_sheet", lang))
    st.write(f"{t('total_records', lang)}: **{format_int(recon['sales']['total_rows_checked'])}** — "
             f"{t('status_valid', lang)}: **{format_int(recon['sales']['valid'])}** "
             f"({format_pct(recon['sales']['valid_pct'])})")
    if exclusions["sales"]["rows_excluded_from_analytical_totals"] > 0:
        with st.expander(t("analytical_exclusions", lang) + " - " + t("sales_sheet", lang)):
            st.dataframe(exclusions["sales"]["excluded_row_detail"], width='stretch', hide_index=True)
    cust_name_q = dq["customer_name_quality"]
    if cust_name_q["numeric_only_name_count"] > 0:
        raw_note_box(t("customer_numeric_name_note", lang).format(
            count=cust_name_q["numeric_only_name_count"], values=", ".join(cust_name_q["numeric_only_name_values"]),
        ), kind="warning")

    section_header(t("sales_returns_sheet", lang))
    st.write(f"{t('total_records', lang)}: **{format_int(recon['sales_returns']['total_rows_checked'])}** — "
             f"{t('analytical_exclusions', lang)}: **{format_int(exclusions['sales_returns']['rows_excluded_from_analytical_totals'])}**")
    if exclusions["sales_returns"]["rows_excluded_from_analytical_totals"] > 0:
        with st.expander(t("analytical_exclusions", lang) + " - " + t("sales_returns_sheet", lang)):
            st.dataframe(exclusions["sales_returns"]["excluded_row_detail"], width='stretch', hide_index=True)
    raw_note_box(t("sales_return_link_note", lang), kind="info")
    if len(bundle["fact_sales_returns"]) and "best_effort_match_status" in bundle["fact_sales_returns"].columns:
        raw_note_box(t("match_status_disclaimer", lang), kind="info")

    section_header(t("local_purchases_before_vat", lang))
    st.write(f"{t('total_records', lang)}: **{format_int(recon['local_purchases']['total_rows_checked'])}** — "
             f"{t('status_valid', lang)}: **{format_int(recon['local_purchases']['valid'])}** "
             f"({format_pct(recon['local_purchases']['valid_pct'])})")

    section_header(t("foreign_purchase_total", lang))
    st.write(f"{t('total_records', lang)}: **{format_int(recon['foreign_purchases']['total_rows_checked'])}** — "
             f"{t('status_valid', lang)}: **{format_int(recon['foreign_purchases']['valid'])}** "
             f"({format_pct(recon['foreign_purchases']['valid_pct'])})")
    raw_note_box(
        "Foreign Purchases has no VAT field in the source data (no domestic tax is charged the same way as "
        "Local Purchases)." if lang == "en" else
        "لا يوجد حقل ضريبة في بيانات المشتريات الخارجية المصدرية (لا تُفرض عليها ضريبة محلية بنفس طريقة "
        "المشتريات الداخلية).",
        kind="info",
    )

    section_header(t("purchase_returns_sheet", lang))
    disc = dq["local_purchase_returns_discount_status"]
    st.write(
        f"{t('total_records', lang)}: **{format_int(disc['total_purchase_return_rows'])}** — "
        f"{t('status_valid', lang)}: **{format_int(recon['local_purchase_returns']['valid'])}**  |  "
        f"{t('discount_reported_label', lang)}: **{format_int(disc['discount_reported'])}**  |  "
        f"{t('discount_missing_inferred_zero_label', lang)}: **{format_int(disc['discount_missing_inferred_zero'])}**"
    )
    if disc["discount_missing_inferred_zero"] > 0:
        raw_note_box(t("purchase_return_discount_missing_note", lang), kind="info")
    raw_note_box(t("purchase_return_no_supplier_note", lang), kind="warning")
    raw_note_box(t("purchase_return_no_invoice_link_note", lang), kind="warning")

    cc = dq["cost_centers"]
    st.write(f"{t('cost_center', lang)}: **{cc['distinct_cost_center_count']}** " +
             ("distinct names" if lang == "en" else "اسماً مختلفاً"))
    if cc["numeric_code_row_count"] > 0:
        total_lpret = dq["analytical_records"]["local_purchase_returns"]
        raw_note_box(t("cost_center_numeric_code_note", lang).format(
            count=cc["numeric_code_row_count"], total=total_lpret,
            numeric_distinct=cc["numeric_code_distinct_count"], codes=", ".join(cc["numeric_code_values"]),
        ), kind="warning")

    st.markdown("---")
    section_header(t("profit", lang))
    prof = dq["profit"]
    years_str = ", ".join(str(y) for y in sorted(prof["years_present"]))
    coverage_str = t("coverage_complete", lang) if prof["covers_analysis_years"] else t("coverage_incomplete", lang)
    st.write(
        f"**{prof['row_count']}** {t('annual_records_label', lang)} | "
        f"{t('available_years_label', lang)}: **{years_str}** | "
        f"{t('coverage_label', lang)}: **{coverage_str}**"
    )

    st.markdown("---")
    section_header(t("supplier_balances", lang))
    sdebt = dq["supplier_debt"]
    scred = dq["supplier_creditors"]
    debt_check = t("matches_source_total", lang) if sdebt["recomputed_matches_reported_total"] else t("does_not_match_source_total", lang)
    cred_check = t("matches_source_total", lang) if scred["recomputed_matches_reported_total"] else t("does_not_match_source_total", lang)
    st.write(
        f"{t('supplier_debt_section', lang)}: **{sdebt['supplier_row_count']}** {t('suppliers_label', lang)}, "
        f"{t('local_currency_amount_col', lang)}: **{format_money(sdebt['recomputed_local_total'], lang)}** ({debt_check})"
    )
    st.write(
        f"{t('supplier_creditors_section', lang)}: **{scred['supplier_row_count']}** {t('suppliers_label', lang)}, "
        f"{t('local_currency_amount_col', lang)}: **{format_money(scred['recomputed_local_total'], lang)}** ({cred_check})"
    )
    raw_note_box(t("supplier_balance_snapshot_note", lang), kind="info")
    raw_note_box(t("supplier_balance_no_net_note", lang), kind="info")
