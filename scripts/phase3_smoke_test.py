# -*- coding: utf-8 -*-
"""
Smoke-tests every page's render() function directly (outside a live Streamlit
server) for both languages, using the real cached pipeline, then runs a
filter regression matrix that independently recomputes expected values from
the filtered DataFrames rather than trusting the dashboard's own numbers.
"""
import sys
import io
import traceback
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

import config
from src import data_pipeline, filters as filters_mod
from src.pages import (
    executive_overview, sales_performance, purchasing_performance, returns_analysis,
    vat_analysis, customers_suppliers, yoy_analysis, data_quality, supplier_balances,
)

PAGES = [
    ("executive_overview", executive_overview),
    ("sales_performance", sales_performance),
    ("purchasing_performance", purchasing_performance),
    ("returns_analysis", returns_analysis),
    ("vat_analysis", vat_analysis),
    ("customers_suppliers", customers_suppliers),
    ("yoy_analysis", yoy_analysis),
    ("supplier_balances", supplier_balances),
    ("data_quality", data_quality),
]

BASE_FILTERS = {"years": [2022, 2023, 2024, 2025], "quarters": [1, 2, 3, 4],
                 "customer": None, "internal_supplier": None, "external_supplier": None, "cost_center": None}


def main():
    print("Loading pipeline...")
    bundle = data_pipeline.load_pipeline()
    print("Pipeline loaded OK.\n")

    all_ok = True

    def render_pass(label, filt):
        nonlocal all_ok
        filtered = filters_mod.apply_filters(bundle, filt)
        computed = data_pipeline.compute_filtered_bundle(bundle, filtered, filt)
        for lang in ["en", "ar"]:
            for name, mod in PAGES:
                try:
                    mod.render(bundle, filtered, computed, lang)
                    print(f"[OK]   {label:14s} lang={lang}  page={name}")
                except Exception as e:
                    all_ok = False
                    print(f"[FAIL] {label:14s} lang={lang}  page={name}  -> {type(e).__name__}: {e}")
                    traceback.print_exc()
        return filtered, computed

    render_pass("no_filters", BASE_FILTERS)
    render_pass("narrow_filters", dict(BASE_FILTERS, years=[2023], quarters=[4]))

    dim_customer = bundle["dim_customer"]
    named = dim_customer.loc[~dim_customer["is_generic_cash_customer"], "customer_name"].dropna()
    if len(named):
        render_pass("customer_filter", dict(BASE_FILTERS, customer=named.iloc[0]))

    dim_supplier = bundle["dim_supplier"]
    internal_suppliers = dim_supplier.loc[dim_supplier["in_local"], "supplier_name"].dropna()
    external_suppliers = dim_supplier.loc[dim_supplier["in_foreign"], "supplier_name"].dropna()
    if len(internal_suppliers):
        render_pass("internal_supplier_filter", dict(BASE_FILTERS, internal_supplier=internal_suppliers.iloc[0]))
    if len(external_suppliers):
        render_pass("external_supplier_filter", dict(BASE_FILTERS, external_supplier=external_suppliers.iloc[0]))
    if len(internal_suppliers) and len(external_suppliers):
        render_pass("both_supplier_filters", dict(BASE_FILTERS, internal_supplier=internal_suppliers.iloc[0],
                                                    external_supplier=external_suppliers.iloc[0]))

    dim_cost_center = bundle["dim_cost_center"]
    if len(dim_cost_center):
        render_pass("cost_center_filter", dict(BASE_FILTERS, cost_center=dim_cost_center["cost_center_name"].iloc[0]))

    # Combo scenarios E-K from the management QA matrix - each is primarily a
    # "renders with zero exceptions across all 9 pages, both languages" check;
    # the numeric independence itself is already proven above per-filter.
    if len(internal_suppliers):
        render_pass("internal_supplier+year", dict(BASE_FILTERS, internal_supplier=internal_suppliers.iloc[0], years=[2024]))  # E
    if len(external_suppliers):
        render_pass("external_supplier+year", dict(BASE_FILTERS, external_supplier=external_suppliers.iloc[0], years=[2024]))  # F
    if len(internal_suppliers) and len(external_suppliers):
        render_pass("both_supplier+quarter", dict(BASE_FILTERS, internal_supplier=internal_suppliers.iloc[0],
                                                    external_supplier=external_suppliers.iloc[0], quarters=[1]))  # G
    if len(internal_suppliers) and len(named):
        render_pass("internal_supplier+customer", dict(BASE_FILTERS, internal_supplier=internal_suppliers.iloc[0],
                                                         customer=named.iloc[0]))  # H
    if len(external_suppliers) and len(named):
        render_pass("external_supplier+customer", dict(BASE_FILTERS, external_supplier=external_suppliers.iloc[0],
                                                         customer=named.iloc[0]))  # I
    if len(internal_suppliers) and len(dim_cost_center):
        render_pass("cost_center+internal_supplier", dict(BASE_FILTERS, internal_supplier=internal_suppliers.iloc[0],
                                                            cost_center=dim_cost_center["cost_center_name"].iloc[0]))  # J
    if len(external_suppliers) and len(dim_cost_center):
        render_pass("cost_center+external_supplier", dict(BASE_FILTERS, external_supplier=external_suppliers.iloc[0],
                                                            cost_center=dim_cost_center["cost_center_name"].iloc[0]))  # K

    # ---- Filter regression assertions (independently recomputed, not just "does it render") ----
    print("\n--- Filter regression checks ---")

    def check(label, cond):
        nonlocal all_ok
        status = "[OK]  " if cond else "[FAIL]"
        if not cond:
            all_ok = False
        print(f"{status} {label}")

    filtered_all = filters_mod.apply_filters(bundle, BASE_FILTERS)
    computed_all = data_pipeline.compute_filtered_bundle(bundle, filtered_all, BASE_FILTERS)
    baseline_net_sales = computed_all["current_metrics"]["net_sales_before_vat"]
    baseline_total_purch = computed_all["current_metrics"]["total_purchases_before_vat"]
    check("Reset/default filters reproduce the synthetic full-period Net Sales (SAR 21,032,579.06)",
          abs(baseline_net_sales - 21032579.06) < 1.0)
    check("Reset/default filters reproduce the synthetic full-period Total Purchases (Local + Foreign, SAR 11,265,708.50)",
          abs(baseline_total_purch - 11265708.50) < 1.0)

    # Year filter
    filt_2025 = dict(BASE_FILTERS, years=[2025])
    filtered_2025 = filters_mod.apply_filters(bundle, filt_2025)
    computed_2025 = data_pipeline.compute_filtered_bundle(bundle, filtered_2025, filt_2025)
    net_sales_2025 = computed_2025["current_metrics"]["net_sales_before_vat"]
    expected_2025 = bundle["annual"].loc[2025, "net_sales_before_vat"]
    check(f"Year=2025 filter changes Net Sales away from the full-period total (got SAR {net_sales_2025:,.2f})",
          abs(net_sales_2025 - baseline_net_sales) > 1.0)
    check("Year=2025 filter's Net Sales matches the pipeline's own 2025 annual figure",
          abs(net_sales_2025 - expected_2025) < 1.0)

    # Quarter filter (combined with Year)
    filt_2025_q1 = dict(BASE_FILTERS, years=[2025], quarters=[1])
    filtered_2025_q1 = filters_mod.apply_filters(bundle, filt_2025_q1)
    computed_2025_q1 = data_pipeline.compute_filtered_bundle(bundle, filtered_2025_q1, filt_2025_q1)
    net_sales_2025_q1 = computed_2025_q1["current_metrics"]["net_sales_before_vat"]
    expected_2025_q1 = filtered_2025_q1["fact_sales"]["net_amount"].sum() - \
        filtered_2025_q1["fact_sales_returns"]["return_value_before_vat"].sum()
    check("Year=2025 + Quarter=1 Net Sales matches an independent direct DataFrame calculation",
          abs(net_sales_2025_q1 - expected_2025_q1) < 1.0)

    # Customer filter
    if len(named):
        one_customer = named.iloc[0]
        cf = dict(BASE_FILTERS, customer=one_customer)
        filtered_c = filters_mod.apply_filters(bundle, cf)
        computed_c = data_pipeline.compute_filtered_bundle(bundle, filtered_c, cf)
        m = computed_c["current_metrics"]
        expected_cust_net_sales = filtered_c["fact_sales"]["net_amount"].sum() - \
            filtered_c["fact_sales_returns"]["return_value_before_vat"].sum()
        check("Customer filter's Net Sales matches an independent direct DataFrame calculation",
              abs(m["net_sales_before_vat"] - expected_cust_net_sales) < 1.0)
        check("Customer filter does NOT change Local Purchases (no customer relationship on Purchases)",
              abs(m["local_purchases_before_vat"] - computed_all["current_metrics"]["local_purchases_before_vat"]) < 1.0)
        check("Customer filter does NOT change Foreign Purchases",
              abs(m["foreign_purchase_total"] - computed_all["current_metrics"]["foreign_purchase_total"]) < 1.0)
        check("Customer filter does NOT change Local Purchase Returns",
              abs(m["local_purchase_returns_before_vat"] - computed_all["current_metrics"]["local_purchase_returns_before_vat"]) < 1.0)

    # Internal Supplier filter (scenario B: internal selected, external = All)
    if len(internal_suppliers):
        one_internal = internal_suppliers.iloc[0]
        isf = dict(BASE_FILTERS, internal_supplier=one_internal)
        filtered_is = filters_mod.apply_filters(bundle, isf)
        computed_is = data_pipeline.compute_filtered_bundle(bundle, filtered_is, isf)
        m = computed_is["current_metrics"]
        expected_local = filtered_is["fact_local_purchases"]["purchase_before_vat"].sum()
        expected_total = expected_local + baseline_total_purch - computed_all["current_metrics"]["local_purchases_before_vat"]
        check("Internal Supplier filter's Domestic Purchases matches an independent direct DataFrame calculation",
              abs(m["local_purchases_before_vat"] - expected_local) < 1.0)
        check("Internal Supplier filter changes Domestic Purchases away from baseline",
              abs(m["local_purchases_before_vat"] - computed_all["current_metrics"]["local_purchases_before_vat"]) > 1.0)
        check("Internal Supplier filter does NOT change Foreign Purchases (stays at full baseline)",
              abs(m["foreign_purchase_total"] - computed_all["current_metrics"]["foreign_purchase_total"]) < 1.0)
        check("Internal Supplier filter's Total Purchases = filtered internal + full external",
              abs(m["total_purchases_before_vat"] - expected_total) < 1.0)
        check("Internal Supplier filter does NOT change Net Sales (no supplier relationship on Sales)",
              abs(m["net_sales_before_vat"] - baseline_net_sales) < 1.0)
        check("Internal Supplier filter does NOT filter Local Purchase Returns (no supplier field on that fact table)",
              abs(m["local_purchase_returns_before_vat"] - computed_all["current_metrics"]["local_purchase_returns_before_vat"]) < 1.0)

    # External Supplier filter (scenario C: external selected, internal = All)
    if len(external_suppliers):
        one_external = external_suppliers.iloc[0]
        esf = dict(BASE_FILTERS, external_supplier=one_external)
        filtered_es = filters_mod.apply_filters(bundle, esf)
        computed_es = data_pipeline.compute_filtered_bundle(bundle, filtered_es, esf)
        m = computed_es["current_metrics"]
        expected_foreign = filtered_es["fact_foreign_purchases"]["purchase_total_before_vat"].sum()
        expected_total = expected_foreign + baseline_total_purch - computed_all["current_metrics"]["foreign_purchase_total"]
        check("External Supplier filter's Foreign Purchases matches an independent direct DataFrame calculation",
              abs(m["foreign_purchase_total"] - expected_foreign) < 1.0)
        check("External Supplier filter changes Foreign Purchases away from baseline",
              abs(m["foreign_purchase_total"] - computed_all["current_metrics"]["foreign_purchase_total"]) > 1.0)
        check("External Supplier filter does NOT change Domestic Purchases (stays at full baseline)",
              abs(m["local_purchases_before_vat"] - computed_all["current_metrics"]["local_purchases_before_vat"]) < 1.0)
        check("External Supplier filter's Total Purchases = full internal + filtered external",
              abs(m["total_purchases_before_vat"] - expected_total) < 1.0)
        check("External Supplier filter does NOT change Net Sales (no supplier relationship on Sales)",
              abs(m["net_sales_before_vat"] - baseline_net_sales) < 1.0)
        check("External Supplier filter does NOT filter Local Purchase Returns (no supplier field on that fact table)",
              abs(m["local_purchase_returns_before_vat"] - computed_all["current_metrics"]["local_purchase_returns_before_vat"]) < 1.0)

    # Both supplier filters together (scenario D: independent narrowing, not mutual zeroing)
    if len(internal_suppliers) and len(external_suppliers):
        bsf = dict(BASE_FILTERS, internal_supplier=internal_suppliers.iloc[0], external_supplier=external_suppliers.iloc[0])
        filtered_bs = filters_mod.apply_filters(bundle, bsf)
        computed_bs = data_pipeline.compute_filtered_bundle(bundle, filtered_bs, bsf)
        m = computed_bs["current_metrics"]
        expected_local_both = filtered_bs["fact_local_purchases"]["purchase_before_vat"].sum()
        expected_foreign_both = filtered_bs["fact_foreign_purchases"]["purchase_total_before_vat"].sum()
        check("Both suppliers selected: Domestic Purchases matches independent direct calculation",
              abs(m["local_purchases_before_vat"] - expected_local_both) < 1.0)
        check("Both suppliers selected: Foreign Purchases matches independent direct calculation",
              abs(m["foreign_purchase_total"] - expected_foreign_both) < 1.0)
        check("Both suppliers selected: Total Purchases = filtered internal + filtered external (neither stream zeroed by the other)",
              abs(m["total_purchases_before_vat"] - (expected_local_both + expected_foreign_both)) < 1.0)
        check("Both suppliers selected: Net Sales unchanged (no supplier relationship on Sales)",
              abs(m["net_sales_before_vat"] - baseline_net_sales) < 1.0)

    # Cost Center filter
    if len(dim_cost_center):
        one_cc = dim_cost_center["cost_center_name"].iloc[0]
        ccf = dict(BASE_FILTERS, cost_center=one_cc)
        filtered_cc = filters_mod.apply_filters(bundle, ccf)
        computed_cc = data_pipeline.compute_filtered_bundle(bundle, filtered_cc, ccf)
        m = computed_cc["current_metrics"]
        expected_cc_returns = filtered_cc["fact_local_purchase_returns"]["return_value_before_vat"].sum()
        check("Cost Center filter's Local Purchase Returns matches an independent direct DataFrame calculation",
              abs(m["local_purchase_returns_before_vat"] - expected_cc_returns) < 1.0)
        check("Cost Center filter does NOT change Local Purchases",
              abs(m["local_purchases_before_vat"] - computed_all["current_metrics"]["local_purchases_before_vat"]) < 1.0)
        check("Cost Center filter does NOT change Foreign Purchases",
              abs(m["foreign_purchase_total"] - computed_all["current_metrics"]["foreign_purchase_total"]) < 1.0)
        check("Cost Center filter does NOT change Net Sales",
              abs(m["net_sales_before_vat"] - baseline_net_sales) < 1.0)

    # Profit is annual-only: full-year scope sums correctly, sub-annual scope must be "unavailable"
    from src import financial_metrics
    profit_table = bundle["profit_table"]
    profit_2022_2023 = financial_metrics.profit_for_years(profit_table, [2022, 2023])
    expected_profit_sum = financial_metrics.profit_for_year(profit_table, 2022) + financial_metrics.profit_for_year(profit_table, 2023)
    check("Profit for multiple full years sums the approved source values exactly",
          profit_2022_2023 is not None and abs(profit_2022_2023 - expected_profit_sum) < 0.01)

    # ---- New regression checks (this pass's confirmed bug fixes) ----
    print("\n--- New regression checks ---")

    # YoY comparison-scope bug fix: Year=2024+Q1 must compare against Q1 2023,
    # not silently against full-year figures while still labeling "vs 2024".
    filt_2024_q1 = dict(BASE_FILTERS, years=[2024], quarters=[1])
    filtered_2024_q1 = filters_mod.apply_filters(bundle, filt_2024_q1)
    computed_2024_q1 = data_pipeline.compute_filtered_bundle(bundle, filtered_2024_q1, filt_2024_q1)
    check("Year=2024 + Quarter=1 comparison label is 'Q1 2023' (scope-matched, not the old 'vs 2024' bug)",
          computed_2024_q1["comparison_label"] == "Q1 2023")
    prev_period_check = filters_mod.apply_filters(bundle, dict(filt_2024_q1, years=[2023]))
    expected_prev_net_sales = prev_period_check["fact_sales"]["net_amount"].sum() - \
        prev_period_check["fact_sales_returns"]["return_value_before_vat"].sum()
    check("Year=2024 + Quarter=1 comparison_metrics is genuinely Q1-2023-scoped (not full-year 2023)",
          computed_2024_q1["comparison_metrics"] is not None and
          abs(computed_2024_q1["comparison_metrics"]["net_sales_before_vat"] - expected_prev_net_sales) < 1.0)

    # Default (all 4 years) selection must show NO comparison - a cumulative
    # multi-year total has no valid single previous period (bug fix: this
    # used to compare the full 4-year total against just 2024's annual
    # figure, producing meaningless deltas like "+414% vs 2024").
    check("Default (all 4 years) selection shows no comparison (neutral delta, not a mismatched-scope percentage)",
          computed_all["comparison_label"] is None and computed_all["comparison_metrics"] is None)

    # Customer name-collision fix: two different customer_no sharing one name
    # must no longer have the full return total double-attributed to both.
    fs_full = bundle["fact_sales"]
    fsr_full = bundle["fact_sales_returns"]
    name_collisions = fs_full.groupby("customer_name_original")["customer_no"].nunique()
    collision_names = set(name_collisions[name_collisions > 1].index) & set(fsr_full["customer_name_original"].unique())
    cust_df_full = bundle["baseline_cust_df"]
    check("customer_analysis() output has exactly one row per customer name (no customer_no fan-out)",
          cust_df_full["customer_name_original"].duplicated().sum() == 0)
    if collision_names:
        sample_name = next(iter(collision_names))
        row = cust_df_full[cust_df_full["customer_name_original"] == sample_name]
        expected_returns = fsr_full.loc[fsr_full["customer_name_original"] == sample_name, "return_value_before_vat"].sum()
        check(f"Name-collision customer {sample_name!r}: Sales Returns counted exactly once (not once per customer_no)",
              len(row) == 1 and abs(row.iloc[0]["sales_returns_before_vat"] - expected_returns) < 1.0)

    # Generic 'عام' Local supplier excluded from concentration ranking
    supp_local_full = bundle["baseline_supp_local_df"]
    generic_rows = supp_local_full[supp_local_full["supplier_name_original"] == config.GENERIC_SUPPLIER_NAME]
    check("Generic 'عام' Local supplier is flagged is_generic_supplier",
          len(generic_rows) == 1 and bool(generic_rows.iloc[0]["is_generic_supplier"]))
    check("Generic 'عام' Local supplier excluded from baseline supplier_count (identifiable suppliers only)",
          bundle["baseline_supp_local_conc"]["supplier_count"] == len(supp_local_full) - len(generic_rows))
    check("Generic 'عام' Local supplier's value is reported separately, not silently dropped",
          bundle["baseline_supp_local_conc"]["generic_supplier_value"] > 0)

    # KPI exact-value truncation fix: default show_exact must be False everywhere
    import inspect
    from src.ui_components import kpi_from_metrics as _kfm
    check("kpi_from_metrics defaults show_exact=False (exact value moved to tooltip, no CSS ellipsis truncation)",
          inspect.signature(_kfm).parameters["show_exact"].default is False)

    print("\nALL SMOKE TESTS PASSED" if all_ok else "\nSOME SMOKE TESTS FAILED")
    return all_ok


if __name__ == "__main__":
    ok = main()
    sys.exit(0 if ok else 1)
