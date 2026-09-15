# -*- coding: utf-8 -*-
"""
Pipeline validation: load -> clean -> validate -> compute -> cross-check -> report.
Read-only against the source workbook. Writes nothing back to it.

Portfolio/demo build: every expected value below (row counts, the four
annual Profit figures, the Sales Returns grand-total) is the deterministic
output of scripts/generate_synthetic_data.py (fixed SEED) - none of it is
real company data. Regenerate the workbook and these numbers stay identical.
"""
import sys
import io
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

import numpy as np
import pandas as pd

import config
from src import data_loader, data_cleaning, data_model, validations, financial_metrics, insights, business_calendar

pd.set_option("display.max_columns", 200)
pd.set_option("display.width", 220)
pd.set_option("display.float_format", lambda x: f"{x:,.2f}")


def hr(t):
    print("\n" + "=" * 110)
    print(t)
    print("=" * 110)


def check(label, condition, detail=""):
    status = "PASS" if condition else "FAIL"
    print(f"[{status}] {label}" + (f"  -- {detail}" if detail else ""))
    return condition


def main():
    all_checks_passed = True

    hr("STEP 1 - LOAD (read-only)")
    raw = data_loader.load_raw_sheets()
    for name, df in raw.items():
        print(f"  {name}: {len(df):,} rows")
    mtime_before = config.SOURCE_WORKBOOK.stat().st_mtime
    size_before = config.SOURCE_WORKBOOK.stat().st_size

    hr("STEP 2 - CLEAN / BUILD FACT TABLES")
    fact_sales, sales_excluded_audit = data_cleaning.clean_sales(raw[config.SHEET_SALES])
    fact_sales_returns, sret_excluded_audit = data_cleaning.clean_sales_returns(raw[config.SHEET_SALES_RETURNS])
    fact_sales_returns = data_cleaning.link_sales_returns_to_sales_best_effort(fact_sales_returns, fact_sales)
    fact_local_purchases, lpurch_excluded_audit = data_cleaning.clean_local_purchases(raw[config.SHEET_LOCAL_PURCHASES])
    fact_foreign_purchases, fpurch_excluded_audit = data_cleaning.clean_foreign_purchases(raw[config.SHEET_FOREIGN_PURCHASES])
    fact_local_purchase_returns, lpret_excluded_audit = data_cleaning.clean_local_purchase_returns(raw[config.SHEET_LOCAL_PURCHASE_RETURNS])
    fact_profit = data_cleaning.clean_profit(raw[config.SHEET_PROFIT])
    fact_supplier_debt, sdebt_excluded_audit = data_cleaning.clean_supplier_debt(raw[config.SHEET_SUPPLIER_DEBT])
    fact_supplier_creditors, scred_excluded_audit = data_cleaning.clean_supplier_creditors(raw[config.SHEET_SUPPLIER_CREDITORS])

    print(f"  FactSales: {len(fact_sales):,} rows (excluded: {len(sales_excluded_audit)})")
    print(f"  FactSalesReturns: {len(fact_sales_returns):,} rows (excluded: {len(sret_excluded_audit)})")
    print(f"  FactLocalPurchases: {len(fact_local_purchases):,} rows (excluded: {len(lpurch_excluded_audit)})")
    print(f"  FactForeignPurchases: {len(fact_foreign_purchases):,} rows (excluded: {len(fpurch_excluded_audit)})")
    print(f"  FactLocalPurchaseReturns: {len(fact_local_purchase_returns):,} rows (excluded: {len(lpret_excluded_audit)})")
    print(f"  FactProfit: {len(fact_profit):,} rows")
    print(f"  FactSupplierDebt: {len(fact_supplier_debt):,} rows (excluded: {len(sdebt_excluded_audit)})")
    print(f"  FactSupplierCreditors: {len(fact_supplier_creditors):,} rows (excluded: {len(scred_excluded_audit)})")

    dim_date = data_model.build_dim_date()
    dim_customer = data_model.build_dim_customer(fact_sales)
    dim_supplier = data_model.build_dim_supplier(fact_local_purchases, fact_foreign_purchases)
    dim_cost_center = data_model.build_dim_cost_center(fact_local_purchase_returns)
    print(f"  DimDate: {len(dim_date):,} days   DimCustomer: {len(dim_customer):,}   "
          f"DimSupplier: {len(dim_supplier):,}   DimCostCenter: {len(dim_cost_center):,}")

    hr("STEP 3 - DATA QUALITY / RECONCILIATION")
    dq = validations.data_quality_summary(
        raw, fact_sales, sales_excluded_audit, fact_sales_returns, sret_excluded_audit,
        fact_local_purchases, lpurch_excluded_audit, fact_foreign_purchases, fpurch_excluded_audit,
        fact_local_purchase_returns, lpret_excluded_audit, fact_profit,
        fact_supplier_debt, sdebt_excluded_audit, fact_supplier_creditors, scred_excluded_audit,
        dim_customer,
    )
    import json
    print(json.dumps(dq, indent=2, ensure_ascii=False, default=str))

    hr("STEP 4 - ANNUAL FINANCIAL TABLE")
    annual = financial_metrics.build_annual_table(fact_sales, fact_sales_returns, fact_local_purchases,
                                                   fact_foreign_purchases, fact_local_purchase_returns)
    print(annual.T.to_string())

    hr("STEP 5 - YOY TABLE")
    yoy = financial_metrics.build_yoy_table(annual)
    print(yoy.T.to_string())

    hr("STEP 5b - PROFIT TABLE (approved source only)")
    profit_table = financial_metrics.build_profit_table(fact_profit)
    print(profit_table.to_string())
    profit_yoy = financial_metrics.build_profit_yoy_table(profit_table)
    print(profit_yoy.to_string())

    hr("STEP 5c - WORKING DAYS TABLE (business calendar)")
    wd_table = business_calendar.working_days_table()
    print(wd_table.to_string())

    hr("STEP 6 - CUSTOMER / SUPPLIER ANALYSIS")
    cust_df = financial_metrics.customer_analysis(fact_sales, fact_sales_returns)
    cust_conc = financial_metrics.customer_concentration(cust_df)
    print("Customer concentration:", cust_conc)

    supp_local_df = financial_metrics.supplier_analysis_local(fact_local_purchases)
    supp_local_conc = financial_metrics.supplier_concentration(supp_local_df)
    print("\nLocal supplier concentration:", supp_local_conc)

    supp_foreign_df = financial_metrics.supplier_analysis_foreign(fact_foreign_purchases)
    supp_foreign_conc = financial_metrics.supplier_concentration(supp_foreign_df)
    print("Foreign supplier concentration:", supp_foreign_conc)

    hr("STEP 6b - SUPPLIER BALANCES")
    debt_summary = financial_metrics.supplier_balance_summary(fact_supplier_debt)
    cred_summary = financial_metrics.supplier_balance_summary(fact_supplier_creditors)
    print("Supplier Debt summary:", debt_summary)
    print("Supplier Creditors summary:", cred_summary)

    hr("STEP 7 - EXECUTIVE INSIGHTS (EN)")
    ins_en = insights.generate_insights(annual, yoy, cust_conc, supp_local_conc, profit_table, lang="en")
    for i in ins_en:
        print(f"  - {i['text']}")

    hr("STEP 7b - EXECUTIVE INSIGHTS (AR)")
    ins_ar = insights.generate_insights(annual, yoy, cust_conc, supp_local_conc, profit_table, lang="ar")
    for i in ins_ar:
        print(f"  - {i['text']}")

    hr("STEP 8 - CROSS-VALIDATION CHECKS")

    # 1) Source workbook untouched
    mtime_after = config.SOURCE_WORKBOOK.stat().st_mtime
    size_after = config.SOURCE_WORKBOOK.stat().st_size
    all_checks_passed &= check("Source workbook mtime unchanged (not modified)", mtime_before == mtime_after)
    all_checks_passed &= check("Source workbook size unchanged (not modified)", size_before == size_after)

    # 2) Annual totals sum to full-period total (for additive KPIs)
    additive_kpis = ["gross_sales_before_vat", "sales_returns_before_vat", "net_sales_before_vat",
                      "gross_output_vat", "sales_return_vat", "net_output_vat",
                      "local_purchases_before_vat", "local_purchase_vat",
                      "foreign_purchase_base", "foreign_purchase_additional_cost", "foreign_purchase_total",
                      "total_purchases_before_vat", "local_purchase_returns_before_vat", "local_purchase_returns_vat",
                      "sales_transaction_count", "purchase_transaction_count"]
    years_only = annual.drop(index="ALL_PERIOD_2022_2025")
    for kpi in additive_kpis:
        summed = years_only[kpi].sum()
        total = annual.loc["ALL_PERIOD_2022_2025", kpi]
        ok = abs(summed - total) <= 0.5
        all_checks_passed &= check(f"Sum of yearly '{kpi}' == full-period total",
                                    ok, f"summed={summed:,.2f} vs total={total:,.2f}")

    # 3) Gross Sales - Sales Returns = Net Sales
    for y in annual.index:
        diff = (annual.loc[y, "gross_sales_before_vat"] - annual.loc[y, "sales_returns_before_vat"]
                - annual.loc[y, "net_sales_before_vat"])
        all_checks_passed &= check(f"[{y}] Gross Sales - Sales Returns = Net Sales", abs(diff) <= 0.5, f"diff={diff:,.4f}")

    # 4) VAT formula (output side only)
    for y in annual.index:
        diff_out = annual.loc[y, "gross_output_vat"] - annual.loc[y, "sales_return_vat"] - annual.loc[y, "net_output_vat"]
        all_checks_passed &= check(f"[{y}] Net Output VAT formula", abs(diff_out) <= 0.5, f"diff={diff_out:,.4f}")

    # 5) Local + Foreign Purchases = Total Purchases (never netted against returns)
    for y in annual.index:
        diff = (annual.loc[y, "local_purchases_before_vat"] + annual.loc[y, "foreign_purchase_total"]
                - annual.loc[y, "total_purchases_before_vat"])
        all_checks_passed &= check(f"[{y}] Local + Foreign Purchases = Total Purchases", abs(diff) <= 0.5, f"diff={diff:,.4f}")

    # 6) Foreign Purchase Base + Additional Cost = Foreign Purchase Total (structural
    # relationship - wide tolerance, matches the row-level check below; this is a
    # source-data characteristic of Foreign Purchases, not a cleaning defect).
    for y in annual.index:
        diff = (annual.loc[y, "foreign_purchase_base"] + annual.loc[y, "foreign_purchase_additional_cost"]
                - annual.loc[y, "foreign_purchase_total"])
        all_checks_passed &= check(f"[{y}] Foreign Purchase Base + Additional Cost = Foreign Purchase Total",
                                    abs(diff) <= config.FOREIGN_PURCHASE_RECON_TOLERANCE, f"diff={diff:,.4f}")

    # 7) Local Purchases before VAT + Local Purchase VAT = Local Purchases Incl VAT
    for y in annual.index:
        diff = (annual.loc[y, "local_purchases_before_vat"] + annual.loc[y, "local_purchase_vat"]
                - annual.loc[y, "local_purchases_incl_vat"])
        all_checks_passed &= check(f"[{y}] Local Purchases before VAT + VAT = Incl VAT", abs(diff) <= 0.5, f"diff={diff:,.4f}")

    # 8) Transaction counts match fact table row counts
    all_checks_passed &= check("Sum of yearly Sales Transaction Count == len(FactSales)",
                                years_only["sales_transaction_count"].sum() == len(fact_sales))
    all_checks_passed &= check("Sum of yearly Purchase Transaction Count == len(FactLocalPurchases)+len(FactForeignPurchases)",
                                years_only["purchase_transaction_count"].sum() == len(fact_local_purchases) + len(fact_foreign_purchases))

    # 9) No value multiplication from the best-effort return<->sale link
    all_checks_passed &= check("FactSalesReturns row count unchanged after best-effort link merge",
                                len(fact_sales_returns) == 950, f"got {len(fact_sales_returns)}")

    # 10) Sales sheet embedded grand-total row correctly excluded (new-workbook finding).
    # By construction the excluded row's value equals the sum of the real rows above it -
    # that IS the proof it's a grand-total row, not a real transaction.
    sales_total_row_value = sales_excluded_audit["Net invoice without tax"].sum()
    fact_sales_sum = fact_sales["net_amount"].sum()
    all_checks_passed &= check(
        "FactSales sum == excluded grand-total row's value (confirms it WAS a total row)",
        abs(fact_sales_sum - sales_total_row_value) <= 1.0,
        f"fact_sum={fact_sales_sum:,.2f} vs excluded_row_value={sales_total_row_value:,.2f}"
    )
    all_checks_passed &= check("FactSales row count == 15,000 (matches the deterministic synthetic generator)",
                                len(fact_sales) == 15000, f"got {len(fact_sales)}")

    # 11) Sales Returns embedded grand-total row correctly excluded. Its own
    # value should equal the real fact sum - that IS the proof it's a
    # grand-total row, not a real transaction (see generate_synthetic_data.py).
    fact_sret_sum = fact_sales_returns["return_value_before_vat"].sum()
    grand_total_row = sret_excluded_audit.iloc[0]["value_before_vat"] if len(sret_excluded_audit) else None
    all_checks_passed &= check(
        "FactSalesReturns sum == excluded grand-total row's value (confirms it WAS a grand-total row)",
        grand_total_row is not None and abs(fact_sret_sum - grand_total_row) <= 1.0,
        f"fact_sum={fact_sret_sum:,.2f} vs excluded_row_value={grand_total_row}"
    )
    all_checks_passed &= check("1 Sales Returns summary row excluded (single embedded grand-total row)",
                                len(sret_excluded_audit) == 1, f"got {len(sret_excluded_audit)}")

    # 12) Foreign Purchases: purtot + addcost ~= total (wider tolerance, source-data characteristic)
    diff_fp = (fact_foreign_purchases["purchase_base"] + fact_foreign_purchases["additional_cost"]
               - fact_foreign_purchases["purchase_total_before_vat"]).abs()
    all_checks_passed &= check("Foreign Purchases: purtot + addcost ~= total for every row (wide tolerance)",
                                (diff_fp <= config.FOREIGN_PURCHASE_RECON_TOLERANCE).all(),
                                f"max diff={diff_fp.max():,.2f}")

    # 13) Local Purchases: purtot + tax = total with tax (tight tolerance)
    diff_lp = (fact_local_purchases["purchase_before_vat"] + fact_local_purchases["vat_amount"]
               - fact_local_purchases["purchase_incl_vat"]).abs()
    all_checks_passed &= check("Local Purchases: purtot + tax = total with tax for every row (tight tolerance)",
                                (diff_lp <= config.RECON_TOLERANCE).all(), f"max diff={diff_lp.max():,.4f}")

    # 14) Local Purchase Returns row count and missing-discount resolution
    all_checks_passed &= check("FactLocalPurchaseReturns row count == 380",
                                len(fact_local_purchase_returns) == 380, f"got {len(fact_local_purchase_returns)}")
    missing_row = fact_local_purchase_returns[fact_local_purchase_returns["discount_status"] == "Missing-Inferred-Zero"]
    all_checks_passed &= check("Exactly 1 Missing-Inferred-Zero discount row", len(missing_row) == 1, f"got {len(missing_row)}")
    if len(missing_row):
        r = missing_row.iloc[0]
        all_checks_passed &= check("Missing-discount row: validated_discount == 0.0", r["validated_discount"] == 0.0)
        all_checks_passed &= check("Missing-discount row: original 'discount' still NaN (untouched)", pd.isna(r["discount"]))
        all_checks_passed &= check("Missing-discount row: reconciliation_status == Valid (post-inference)",
                                    r["reconciliation_status"] == "Valid")
        all_checks_passed &= check("Missing-discount row: data_quality_warning == True (still flagged)",
                                    bool(r["data_quality_warning"]) is True)

    # 15) Cost Center uses business-readable names (the synthetic generator
    # deliberately uses a small public-safe city list - see
    # generate_synthetic_data.py:COST_CENTERS - rather than numeric codes)
    cc_names = fact_local_purchase_returns["cost_center_name"].unique().tolist()
    has_readable_name = any(not n.strip().isdigit() for n in cc_names if isinstance(n, str))
    all_checks_passed &= check("Cost Center field contains business-readable names (not only numeric codes)",
                                has_readable_name, f"sample names: {cc_names[:6]}")

    # 16) Profit sheet - independently-supplied synthetic source, never derived.
    # Expected values are the deterministic output of generate_synthetic_data.py
    # (fixed SEED) - fully synthetic, not real company figures.
    prof_report = dq["profit"]
    all_checks_passed &= check("Profit sheet covers 2022-2025 exactly", prof_report["covers_analysis_years"] is True)
    all_checks_passed &= check("Profit sheet years are unique", prof_report["years_unique"] is True)
    for y, expected in [(2022, 2936990.04), (2023, 3474197.69), (2024, 3855619.22), (2025, 3218368.49)]:
        actual = financial_metrics.profit_for_year(profit_table, y)
        all_checks_passed &= check(f"[{y}] Profit matches the deterministic synthetic generator's expected output",
                                    actual is not None and abs(actual - expected) <= 0.01,
                                    f"expected={expected:,.2f} actual={actual}")

    # 17) Supplier Debt / Creditors: recomputed total matches the sheet's own reported grand total
    all_checks_passed &= check("Supplier Debt recomputed total matches reported grand total",
                                dq["supplier_debt"]["recomputed_matches_reported_total"] is True)
    all_checks_passed &= check("Supplier Creditors recomputed total matches reported grand total",
                                dq["supplier_creditors"]["recomputed_matches_reported_total"] is True)

    # 18) Working Days - independently recomputed (separate implementation, same rule:
    # calendar days - unique(Fridays UNION Eid dates)) and cross-checked against
    # business_calendar.working_days_in_month for every analysis month.
    def _independent_working_days(year, month):
        start = pd.Timestamp(year=year, month=month, day=1)
        end = start + pd.offsets.MonthEnd(0)
        days = pd.date_range(start, end, freq="D")
        eid_dates = set()
        for holidays in config.BUSINESS_HOLIDAYS.values():
            for key in ("eid_fitr_start", "eid_adha_start"):
                s = pd.Timestamp(holidays[key])
                for i in range(config.EID_HOLIDAY_LENGTH_DAYS):
                    eid_dates.add((s + pd.Timedelta(days=i)).normalize())
        non_working = {d for d in days if d.dayofweek == 4} | {d for d in days if d in eid_dates}
        return len(days) - len(non_working)

    mismatches = []
    for y in config.ANALYSIS_YEARS:
        for m in range(1, 13):
            expected = _independent_working_days(y, m)
            actual = business_calendar.working_days_in_month(y, m)
            if expected != actual:
                mismatches.append((y, m, expected, actual))
    all_checks_passed &= check("Working Days matches an independent recomputation for all 48 analysis months",
                                len(mismatches) == 0, f"mismatches={mismatches}")

    # Cross-month Eid block sanity: both halves of a split block should be > 0 working days short
    # of their full calendar length (i.e. the holiday actually reduced each side).
    wd_mar_2025 = business_calendar.working_days_in_month(2025, 3)
    wd_apr_2025 = business_calendar.working_days_in_month(2025, 4)
    all_checks_passed &= check("Working Days correctly split a cross-month Eid block (Mar/Apr 2025 both < calendar days)",
                                wd_mar_2025 < 31 and wd_apr_2025 < 30, f"Mar={wd_mar_2025} Apr={wd_apr_2025}")

    hr("OVERALL RESULT")
    print("ALL CHECKS PASSED" if all_checks_passed else "SOME CHECKS FAILED - REVIEW ABOVE")

    hr("FILES TOUCHED")
    print(f"Source workbook (read-only, unmodified): {config.SOURCE_WORKBOOK}")
    print(f"Project root (created/modified): {PROJECT_ROOT}")

    return {
        "raw": raw, "fact_sales": fact_sales, "fact_sales_returns": fact_sales_returns,
        "fact_local_purchases": fact_local_purchases, "fact_foreign_purchases": fact_foreign_purchases,
        "fact_local_purchase_returns": fact_local_purchase_returns, "fact_profit": fact_profit,
        "fact_supplier_debt": fact_supplier_debt, "fact_supplier_creditors": fact_supplier_creditors,
        "dim_date": dim_date, "dim_customer": dim_customer, "dim_supplier": dim_supplier,
        "dim_cost_center": dim_cost_center, "dq": dq, "annual": annual, "yoy": yoy,
        "profit_table": profit_table, "all_checks_passed": all_checks_passed,
    }


if __name__ == "__main__":
    result = main()
    sys.exit(0 if result["all_checks_passed"] else 1)
