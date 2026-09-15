# -*- coding: utf-8 -*-
"""
Transforms raw sheets into audited fact tables. Every transformation is
vectorized, non-destructive of original values, and traceable back to a
source row number.

Naming convention used throughout:
    *_original       -> value exactly as read from the workbook
    *_normalized      -> cleaned/standardized derived value (original kept alongside)
    reported_*         -> value as reported in the source
    validated_*         -> value accepted for financial analysis after review
"""
import numpy as np
import pandas as pd

import config
from src import data_model

SALES_TYPE_MAP = {
    "بيع نقدى": "cash_sale",
    "بيع آجل": "credit_sale",
    "خدمات": "service",
}
SALES_RETURN_TYPE_MAP = {
    "مردود نقدى": "cash_return",
    "مردود آجل": "credit_return",
}
PURCHASE_TYPE_MAP = {
    "نقدا": "cash_purchase",
    "آجل": "credit_purchase",
    "اعتماد": "lc_purchase",
}
PURCHASE_RETURN_TYPE_MAP = {
    "مردود نقدي": "cash_return",
    "مردود أجل": "credit_return",
}


def _normalize_type(series: pd.Series, mapping: dict) -> pd.Series:
    # Source 'type' fields carry inconsistent whitespace (e.g. Sales 'خدمات ' has a
    # trailing space) - strip before mapping so this never silently falls into "other".
    return series.map(
        lambda v: mapping.get(v.strip(), "other") if isinstance(v, str) else "unknown"
    )


def _split_trailing_null_key_rows(df: pd.DataFrame, key_col: str):
    """
    Several sheets in the approved workbook carry one or more embedded
    summary/total rows appended after the real transaction rows - identified
    unambiguously by having no value in the sheet's own row-identifying key
    column (trnno / رقم فاتورةالمردود / رقم الحركة / etc - a real transaction
    always has one). Splitting on "key is null" rather than a specific label
    text is deliberately general: the new workbook's Sales and Sales Returns
    sheets were found (structural audit) to carry TWO such trailing rows
    (a full-period grand total and an unlabeled 2022-only subtotal) rather
    than the historically-expected single row, and this still catches both
    correctly. Returns (real_rows, excluded_rows) - excluded_rows is never
    used in any downstream analytical calculation, only for traceability.
    """
    is_excluded = df[key_col].isna()
    return df.loc[~is_excluded].copy(), df.loc[is_excluded].copy()


# --------------------------------------------------------------------------
# SALES
# --------------------------------------------------------------------------
def clean_sales(raw_sales: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Returns (fact_sales, excluded_audit). The approved workbook's Sales
    sheet carries one embedded grand-total row (trnno null) whose monetary
    columns exactly equal the sum of every real row above it (structural
    audit finding) - excluded here the same way the historically-known Sales
    Returns total row is."""
    df = raw_sales.copy()
    df["source_row_number"] = df.index + 2  # +2: 1 for header row, 1 for 1-based indexing

    real, excluded = _split_trailing_null_key_rows(df, "trnno")
    excluded_audit = excluded[["source_row_number", "Net invoice without tax", "total tax",
                                "total invoice with tax"]].copy()
    excluded_audit["exclusion_reason"] = (
        "Embedded workbook grand-total row (trnno is blank). Its value/tax/total exactly "
        "equal the sum of all real sales rows above it (verified in structural audit)."
    )

    out = pd.DataFrame({
        "source_row_number": real["source_row_number"],
        "trnno_reference": real["trnno"],
        "transaction_date": pd.to_datetime(real["trndat"], errors="coerce"),
        "original_transaction_type": real["type"],
        "normalized_transaction_type": _normalize_type(real["type"], SALES_TYPE_MAP),
        "customer_no": real["customer no"],
        "customer_name_original": real["customer name"].astype(str).str.strip(),
        "customer_vat_registration_id": real["customer vat id"],  # TEXT identifier only - never used in arithmetic
        "net_amount": pd.to_numeric(real["Net invoice without tax"], errors="coerce"),
        "vat_amount": pd.to_numeric(real["total tax"], errors="coerce"),
        "gross_amount": pd.to_numeric(real["total invoice with tax"], errors="coerce"),
        "quantity": pd.to_numeric(real["quntity"], errors="coerce"),
    })
    out["is_generic_cash_customer"] = out["customer_no"] == config.GENERIC_CASH_CUSTOMER_NO

    out["reconciliation_diff"] = (out["net_amount"] + out["vat_amount"] - out["gross_amount"])
    out["reconciliation_status"] = np.where(
        out["reconciliation_diff"].abs() <= config.RECON_TOLERANCE, "Valid", "Reconciliation-Review"
    )

    out = data_model.attach_date_attributes(out, "transaction_date")
    return out.reset_index(drop=True), excluded_audit.reset_index(drop=True)


# --------------------------------------------------------------------------
# SALES RETURNS
# --------------------------------------------------------------------------
def clean_sales_returns(raw_sret: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Returns (fact_sales_returns, excluded_audit). excluded_audit preserves
    every embedded summary row for traceability - never used in any
    downstream analytical calculation. The approved workbook carries TWO such
    rows (a labeled grand total 'اجمالى التقرير' and an unlabeled 2022-only
    subtotal), both caught by the same null-key rule (see
    _split_trailing_null_key_rows).
    """
    df = raw_sret.copy()
    df["source_row_number"] = df.index + 2

    real, excluded = _split_trailing_null_key_rows(df, "رقم فاتورةالمردود")
    excluded_audit = excluded[["source_row_number", "اسم العميل", "القيمة", "الضريبة", "الصافي بالضريبة"]].rename(
        columns={
            "اسم العميل": "customer_name_original",
            "القيمة": "value_before_vat",
            "الضريبة": "vat_amount",
            "الصافي بالضريبة": "total_incl_vat",
        }
    ).copy()
    excluded_audit["exclusion_reason"] = (
        "Embedded workbook summary row (return reference number is blank) - either the "
        "full-period grand total ('اجمالى التقرير') or an unlabeled period subtotal left "
        "over from the source export. Never a real transaction."
    )

    out = pd.DataFrame({
        "source_row_number": real["source_row_number"],
        "return_ref_no": real["رقم فاتورةالمردود"],
        "return_date": pd.to_datetime(real["تاريخ الفاتورة"], errors="coerce"),
        "original_return_type": real["نوع الفاتورة"],
        "normalized_return_type": _normalize_type(real["نوع الفاتورة"], SALES_RETURN_TYPE_MAP),
        "original_sale_trnno_ref": real["رقم فاتورة المبيعات"],  # reference only - see match_status below
        "customer_name_original": real["اسم العميل"].astype(str).str.strip(),
        "return_value_before_vat": pd.to_numeric(real["القيمة"], errors="coerce"),
        "return_vat_amount": pd.to_numeric(real["الضريبة"], errors="coerce"),
        "return_total_incl_vat": pd.to_numeric(real["الصافي بالضريبة"], errors="coerce"),
        "quantity": pd.to_numeric(real["الكمية"], errors="coerce"),
    })
    out["is_generic_cash_customer"] = out["customer_name_original"] == config.GENERIC_CASH_CUSTOMER_NAME

    out["reconciliation_diff"] = (
        out["return_value_before_vat"] + out["return_vat_amount"] - out["return_total_incl_vat"]
    )
    out["reconciliation_status"] = np.where(
        out["reconciliation_diff"].abs() <= config.RECON_TOLERANCE, "Valid", "Reconciliation-Review"
    )

    out = data_model.attach_date_attributes(out, "return_date")
    return out.reset_index(drop=True), excluded_audit.reset_index(drop=True)


def link_sales_returns_to_sales_best_effort(fact_sales_returns: pd.DataFrame,
                                              fact_sales: pd.DataFrame) -> pd.DataFrame:
    """
    Best-effort / illustrative-only linkage of a return to its original sale,
    matched on (trnno + exact date) - the only composite proven safe-ish in
    Phase 1 (trnno alone recycles across unrelated transactions).

    IMPORTANT: this NEVER feeds monetary aggregation. It only adds audit
    columns (match_status, matched_source_row_number) for drill-down display.
    A row matching >1 sale on the same (trnno, date) is marked 'Ambiguous'
    rather than silently picking one, so it can never be mistaken for a
    verified 1:1 accounting link.
    """
    sales_key = fact_sales[["source_row_number", "trnno_reference", "transaction_date"]].copy()
    sales_key["match_count"] = sales_key.groupby(["trnno_reference", "transaction_date"])["source_row_number"].transform("count")

    merged = fact_sales_returns.merge(
        sales_key,
        left_on=["original_sale_trnno_ref", "return_date"],
        right_on=["trnno_reference", "transaction_date"],
        how="left",
        suffixes=("", "_matched_sale"),
    )
    # a return could coincidentally match >1 sale row sharing (trnno,date) -> keep first for display,
    # but the ambiguity flag is what matters for auditability, not the picked row.
    merged["match_status"] = np.select(
        [merged["source_row_number_matched_sale"].isna(), merged["match_count"].fillna(0) > 1],
        ["Unmatched", "Ambiguous"],
        default="Best-Effort-Matched",
    )
    merged = merged.drop_duplicates(subset=["source_row_number"], keep="first")
    result = fact_sales_returns.copy()
    result["best_effort_match_status"] = merged.set_index("source_row_number")["match_status"].reindex(result["source_row_number"]).values
    result["best_effort_matched_sale_row"] = merged.set_index("source_row_number")["source_row_number_matched_sale"].reindex(result["source_row_number"]).values
    return result


# --------------------------------------------------------------------------
# PROFIT (management-approved source - never derived from Sales/Purchases)
# --------------------------------------------------------------------------
def clean_profit(raw_profit: pd.DataFrame) -> pd.DataFrame:
    """
    Reads the approved Profit sheet directly - Year + Profit only. No
    calculation, no derivation from Sales/Purchases/inventory happens here or
    anywhere downstream; this is a straight pass-through of management's own
    supplied figures, with only whitespace-strip and numeric-type coercion.
    """
    df = raw_profit.copy()
    out = pd.DataFrame({
        "year": pd.to_numeric(df["السنه"], errors="coerce").astype("Int64"),
        "profit": pd.to_numeric(df["الارباح"], errors="coerce"),
    })
    return out.dropna(subset=["year"]).reset_index(drop=True)


# --------------------------------------------------------------------------
# FOREIGN PURCHASES
# --------------------------------------------------------------------------
def clean_foreign_purchases(raw_fpurch: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Returns (fact_foreign_purchases, excluded_audit). Foreign Purchases has
    no VAT/tax field in the source at all (import/LC purchases are not
    charged local VAT the same way domestic purchases are) - no tax-status
    classification is invented here. purtot + addcost approximates total
    (validated in structural audit; the wider FOREIGN_PURCHASE_RECON_TOLERANCE
    reflects the source data's own precision, not a cleaning defect).
    Additional Cost is already included in `total` - callers must never add
    it again on top of the total when computing Foreign Purchase activity.
    """
    df = raw_fpurch.copy()
    df["source_row_number"] = df.index + 2

    real, excluded = _split_trailing_null_key_rows(df, "trnno")
    excluded_audit = excluded[["source_row_number", "purtot", "addcost", "total", "qty"]].copy()
    excluded_audit["exclusion_reason"] = (
        "Embedded workbook grand-total row (trnno is blank). Its purtot/addcost/total/qty "
        "exactly equal the sum of all real foreign-purchase rows above it."
    )

    purtot = pd.to_numeric(real["purtot"], errors="coerce")
    addcost = pd.to_numeric(real["addcost"], errors="coerce")
    total = pd.to_numeric(real["total"], errors="coerce")
    qty = pd.to_numeric(real["qty"], errors="coerce")

    out = pd.DataFrame({
        "source_row_number": real["source_row_number"],
        "trnno_reference": real["trnno"],
        "purchase_date": pd.to_datetime(real["date"], errors="coerce"),
        "original_transaction_type": real["type"],
        "normalized_transaction_type": _normalize_type(real["type"], PURCHASE_TYPE_MAP),
        "supplier_name_original": real["supplier"].astype(str).str.strip(),
        "purchase_base": purtot,
        "additional_cost": addcost,
        "purchase_total_before_vat": total,  # approved base: purtot + addcost, structural audit confirmed
        "quantity": qty,
    })
    out["net_base_reconciliation_diff"] = (purtot + addcost - total)
    out["reconciliation_status"] = np.where(
        out["net_base_reconciliation_diff"].abs() <= config.FOREIGN_PURCHASE_RECON_TOLERANCE,
        "Valid", "Reconciliation-Review",
    )

    out = data_model.attach_date_attributes(out, "purchase_date")
    return out.reset_index(drop=True), excluded_audit.reset_index(drop=True)


# --------------------------------------------------------------------------
# LOCAL PURCHASES
# --------------------------------------------------------------------------
def clean_local_purchases(raw_lpurch: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Returns (fact_local_purchases, excluded_audit). purtot + tax = total
    with tax (validated in structural audit, tight tolerance like every
    other domestically-taxed sheet)."""
    df = raw_lpurch.copy()
    df["source_row_number"] = df.index + 2

    real, excluded = _split_trailing_null_key_rows(df, "trnno")
    excluded_audit = excluded[["source_row_number", "purtot", "tax", "total with tax", "qty"]].copy()
    excluded_audit["exclusion_reason"] = (
        "Embedded workbook grand-total row (trnno is blank). Its purtot/tax/total/qty "
        "exactly equal the sum of all real local-purchase rows above it."
    )

    purtot = pd.to_numeric(real["purtot"], errors="coerce")
    tax = pd.to_numeric(real["tax"], errors="coerce")
    total_with_tax = pd.to_numeric(real["total with tax"], errors="coerce")
    qty = pd.to_numeric(real["qty"], errors="coerce")

    out = pd.DataFrame({
        "source_row_number": real["source_row_number"],
        "trnno_reference": real["trnno"],
        "purchase_date": pd.to_datetime(real["date"], errors="coerce"),
        "original_transaction_type": real["type"],
        "normalized_transaction_type": _normalize_type(real["type"], PURCHASE_TYPE_MAP),
        "supplier_name_original": real["supplier"].astype(str).str.strip(),
        "purchase_before_vat": purtot,
        "vat_amount": tax,
        "purchase_incl_vat": total_with_tax,
        "quantity": qty,
    })
    out["reconciliation_diff"] = (purtot + tax - total_with_tax)
    out["reconciliation_status"] = np.where(
        out["reconciliation_diff"].abs() <= config.RECON_TOLERANCE, "Valid", "Reconciliation-Review"
    )

    out = data_model.attach_date_attributes(out, "purchase_date")
    return out.reset_index(drop=True), excluded_audit.reset_index(drop=True)


# --------------------------------------------------------------------------
# LOCAL PURCHASE RETURNS
# --------------------------------------------------------------------------
def clean_local_purchase_returns(raw_lpret: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Returns (fact_local_purchase_returns, excluded_audit). This is explicitly
    LOCAL Purchase Returns only - the source has no supplier field and no
    relationship to Foreign Purchases; never subtracted from Foreign
    Purchases. The Cost Center column may, in a real production workbook,
    contain a mix of business-readable names and legacy numeric warehouse
    codes left over from an earlier system - both are used exactly as
    sourced, with no invented mapping (see validations.cost_center_report,
    which flags any numeric ones explicitly rather than hiding them).
    """
    df = raw_lpret.copy()
    df["source_row_number"] = df.index + 2

    real, excluded = _split_trailing_null_key_rows(df, "رقم الحركة")
    excluded_audit = excluded[["source_row_number", "التكلفة", "الخصم", "الضريبة", "الإجمالي"]].copy()
    excluded_audit["exclusion_reason"] = (
        "Embedded workbook summary row (movement number is blank) - a period subtotal "
        "left over from the source export. Never a real transaction."
    )

    cost = pd.to_numeric(real["التكلفة"], errors="coerce")
    discount = pd.to_numeric(real["الخصم"], errors="coerce")
    vat = pd.to_numeric(real["الضريبة"], errors="coerce")
    total = pd.to_numeric(real["الإجمالي"], errors="coerce")

    out = pd.DataFrame({
        "source_row_number": real["source_row_number"],
        "cost_center_name": real["رقم المستودع"].astype(str).str.strip(),
        # movement_no is a WAREHOUSE STOCK-MOVEMENT number, proven in Phase 1 to be
        # unrelated to Purchases.trnno despite superficial numeric overlap. Kept only
        # for internal multi-line document grouping (see return_document_id below).
        "movement_no_reference": real["رقم الحركة"],
        "return_date": pd.to_datetime(real["التاريخ"], errors="coerce"),
        "original_movement_type": real["نوع الحركة"],
        "normalized_movement_type": _normalize_type(real["نوع الحركة"], PURCHASE_RETURN_TYPE_MAP),
        "item_code": real["رقم الصنف"],
        "quantity": pd.to_numeric(real["الكمية"], errors="coerce"),
        "cost_before_discount": cost,
        "discount": discount,  # reported value, exactly as sourced - never overwritten
        "vat_amount": vat,
        "total_incl_vat": total,
    })

    # --- Discount_Status / validated_discount ---------------------------------------
    # 1 row has a missing Discount. Cost + VAT = Total reconciles EXACTLY for that row,
    # strong evidence the missing discount represents zero, not an unknown value. Applied
    # narrowly: only a missing discount independently corroborated by an exact
    # Cost+VAT=Total match is inferred as zero; any other missing discount would be left
    # unresolved (Missing-Unresolved), not silently assumed.
    is_missing_discount = discount.isna()
    calc_total_if_zero_discount = cost + vat
    diff_if_zero_discount = (calc_total_if_zero_discount - total).abs()
    is_inferred_zero = is_missing_discount & (diff_if_zero_discount <= config.RECON_TOLERANCE)
    is_unresolved_missing = is_missing_discount & ~is_inferred_zero

    out["discount_status"] = np.select(
        [is_inferred_zero, is_unresolved_missing],
        ["Missing-Inferred-Zero", "Missing-Unresolved"],
        default="Reported",
    )
    out["discount_source"] = np.select(
        [is_inferred_zero, is_unresolved_missing],
        ["Inferred from Cost + VAT = Total", "Unavailable"],
        default="Reported",
    )
    out["validated_discount"] = np.where(is_inferred_zero, 0.0, discount)  # stays NaN for Missing-Unresolved

    out["return_value_before_vat"] = cost - out["validated_discount"]  # "Purchase Return Before VAT"

    # Internal-only grouping key for a multi-line return document (NOT a purchase link).
    out["return_document_id"] = (
        out["cost_center_name"].astype(str) + "_" +
        out["movement_no_reference"].astype(str) + "_" +
        out["return_date"].dt.strftime("%Y-%m-%d")
    )

    out["reconciliation_diff"] = (out["return_value_before_vat"] + out["vat_amount"] - out["total_incl_vat"])
    out["reconciliation_status"] = np.where(
        out["reconciliation_diff"].abs() <= config.RECON_TOLERANCE, "Valid", "Reconciliation-Review"
    )
    # Even when validated_discount resolves the monetary reconciliation, the row stays
    # flagged as a Data Quality warning (source data was incomplete) - never silently clean.
    out["data_quality_warning"] = is_inferred_zero

    out = data_model.attach_date_attributes(out, "return_date")
    return out.reset_index(drop=True), excluded_audit.reset_index(drop=True)


# --------------------------------------------------------------------------
# SUPPLIER DEBT / SUPPLIER CREDITORS (point-in-time source snapshots - no date)
# --------------------------------------------------------------------------
def _clean_supplier_balance_sheet(raw: pd.DataFrame, label: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Shared cleaning for both supplier-balance sheets - identical schema.
    Source signs are preserved exactly as reported; this dashboard does NOT
    infer which sign convention means "owed to us" vs "owed by us" beyond
    what the sheet name and structure directly show (see financial_metrics
    and the Supplier Balances page for the transparent, separate-totals
    presentation this drives).
    """
    df = raw.copy()
    df["source_row_number"] = df.index + 2

    name_col = "اسم المورد"
    is_total_row = df[name_col].astype(str).str.strip() == config.SUPPLIER_BALANCE_TOTAL_ROW_MARKER
    excluded_audit = df.loc[is_total_row, ["source_row_number", name_col, "العملة الأجنبية", "العملة المحلية"]].rename(
        columns={name_col: "label", "العملة الأجنبية": "foreign_currency_amount", "العملة المحلية": "local_currency_amount"}
    ).copy()
    excluded_audit["exclusion_reason"] = (
        f"Embedded workbook grand-total row (اسم المورد == '{config.SUPPLIER_BALANCE_TOTAL_ROW_MARKER}'). "
        f"Its local-currency amount exactly equals the sum of all real {label} rows above it."
    )

    real = df.loc[~is_total_row].copy()
    out = pd.DataFrame({
        "source_row_number": real["source_row_number"],
        "supplier_name_original": real[name_col].astype(str).str.strip(),
        "currency": real["العملة"],
        "foreign_currency_amount": pd.to_numeric(real["العملة الأجنبية"], errors="coerce"),
        "local_currency_amount": pd.to_numeric(real["العملة المحلية"], errors="coerce"),
    })
    return out.reset_index(drop=True), excluded_audit.reset_index(drop=True)


def clean_supplier_debt(raw_sdebt: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    return _clean_supplier_balance_sheet(raw_sdebt, "supplier-debt")


def clean_supplier_creditors(raw_scred: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    return _clean_supplier_balance_sheet(raw_scred, "supplier-creditor")
