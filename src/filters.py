# -*- coding: utf-8 -*-
"""
Global sidebar filters. Scope is deliberately restricted to what the
approved data model supports for each fact table:

  - Year / Quarter: safe on every DATED fact table (Sales, Sales Returns,
    Local Purchases, Foreign Purchases, Local Purchase Returns). Profit is
    annual-only (see pages) and Supplier Debt/Creditors are undated
    point-in-time snapshots - neither is filtered by Year/Quarter here.
  - Customer: applies ONLY to FactSales and FactSalesReturns (Local/Foreign
    Purchases and Local Purchase Returns have no customer relationship).
  - Internal Supplier / External Supplier (management request - split from
    the former single "Supplier" filter): two INDEPENDENT selections.
    Internal Supplier applies ONLY to FactLocalPurchases (matched on
    whitespace/case-normalized name - never fuzzy-matched); External
    Supplier applies ONLY to FactForeignPurchases. Selecting one never
    narrows or zeroes out the other purchase stream - Total Purchases is
    always (filtered-or-full local) + (filtered-or-full foreign). Neither
    touches Local Purchase Returns (no supplier field exists there) or the
    Sales side. Options for each list come from dim_supplier's in_local/
    in_foreign flags (src/data_model.py:build_dim_supplier), which already
    record - per supplier - which of the two fact tables it genuinely
    appears in, so the two option lists never mix names between streams.
  - Cost Center: applies ONLY to FactLocalPurchaseReturns (the only fact
    table with a proven Cost Center field).

This keeps every page's charts consistent with the same filter state without
ever creating a cross-filter that the data doesn't actually support.
"""
import streamlit as st

import config
from src.translations import t


def _sanitize_selection(key: str, valid_options: list, default: str):
    """
    If a sidebar filter's already-set session_state value is no longer a
    member of the current (freshly computed, this run) options list - e.g.
    the source workbook was edited/re-saved and a Customer/Internal Supplier/
    External Supplier/Cost Center value was renamed or removed between app runs - reset it to
    `default` before the widget renders. Without this, passing a stale
    session_state value as a selectbox's implicit current value while it is
    absent from `options` raises a StreamlitAPIException, crashing the page
    instead of gracefully falling back to "All". A missing key (first run)
    is left untouched here; the caller's own seed-if-absent block handles it.
    """
    if key in st.session_state and st.session_state[key] not in valid_options:
        st.session_state[key] = default


def render_sidebar_filters(bundle: dict, lang: str) -> dict:
    """Must be called from within a `with st.sidebar:` block - uses plain st.*
    calls (not st.sidebar.*) so it lands directly under the Filters label.

    Every widget below is seeded into st.session_state exactly once (only if
    the key doesn't exist yet) and never called again with default=/index= -
    passing both `default`/`index` AND `key` on every rerun is a known
    Streamlit anti-pattern that can silently reset a widget's value on a
    rerun triggered by a DIFFERENT widget (e.g. the sidebar nav buttons) -
    this was the confirmed root cause of a prior "filters reset after
    navigating" bug. Do not reintroduce it."""
    dim_customer = bundle["dim_customer"]
    dim_supplier = bundle["dim_supplier"]
    dim_cost_center = bundle["dim_cost_center"]

    if "flt_years" not in st.session_state:
        st.session_state["flt_years"] = config.ANALYSIS_YEARS
    if "flt_quarters" not in st.session_state:
        st.session_state["flt_quarters"] = [1, 2, 3, 4]

    placeholder = t("filter_placeholder", lang)
    years = st.multiselect(t("filter_year", lang), config.ANALYSIS_YEARS, key="flt_years", placeholder=placeholder)
    quarters = st.multiselect(t("filter_quarter", lang), [1, 2, 3, 4], key="flt_quarters",
                               format_func=lambda q: f"Q{q}", placeholder=placeholder)

    all_label = t("filter_all", lang)
    customer_options = [all_label] + sorted(
        dim_customer.loc[~dim_customer["is_generic_cash_customer"], "customer_name"].dropna().unique().tolist()
    )
    # Split from the dimension's in_local/in_foreign flags - never fabricated,
    # never fuzzy-matched, and (structural audit) currently 100% disjoint:
    # every supplier appears in exactly one of the two purchase streams.
    internal_supplier_options = [all_label] + sorted(
        dim_supplier.loc[dim_supplier["in_local"], "supplier_name"].dropna().unique().tolist()
    )
    external_supplier_options = [all_label] + sorted(
        dim_supplier.loc[dim_supplier["in_foreign"], "supplier_name"].dropna().unique().tolist()
    )
    cost_center_options = [all_label] + sorted(dim_cost_center["cost_center_name"].dropna().unique().tolist())

    _sanitize_selection("flt_customer", customer_options, all_label)
    _sanitize_selection("flt_supplier_internal", internal_supplier_options, all_label)
    _sanitize_selection("flt_supplier_external", external_supplier_options, all_label)
    _sanitize_selection("flt_cost_center", cost_center_options, all_label)

    if "flt_customer" not in st.session_state:
        st.session_state["flt_customer"] = all_label
    if "flt_supplier_internal" not in st.session_state:
        st.session_state["flt_supplier_internal"] = all_label
    if "flt_supplier_external" not in st.session_state:
        st.session_state["flt_supplier_external"] = all_label
    if "flt_cost_center" not in st.session_state:
        st.session_state["flt_cost_center"] = all_label

    customer = st.selectbox(t("filter_customer", lang), customer_options, key="flt_customer", placeholder=placeholder)
    supplier_internal = st.selectbox(t("filter_supplier_internal", lang), internal_supplier_options,
                                      key="flt_supplier_internal", placeholder=placeholder)
    supplier_external = st.selectbox(t("filter_supplier_external", lang), external_supplier_options,
                                      key="flt_supplier_external", placeholder=placeholder)
    cost_center = st.selectbox(t("filter_cost_center", lang), cost_center_options, key="flt_cost_center",
                                placeholder=placeholder)

    return {
        "years": years or config.ANALYSIS_YEARS,
        "quarters": quarters or [1, 2, 3, 4],
        "customer": None if customer == all_label else customer,
        "internal_supplier": None if supplier_internal == all_label else supplier_internal,
        "external_supplier": None if supplier_external == all_label else supplier_external,
        "cost_center": None if cost_center == all_label else cost_center,
    }


def apply_filters(bundle: dict, filters: dict) -> dict:
    fs = bundle["fact_sales"]
    fsr = bundle["fact_sales_returns"]
    flp = bundle["fact_local_purchases"]
    ffp = bundle["fact_foreign_purchases"]
    flpr = bundle["fact_local_purchase_returns"]

    def time_mask(df):
        return df["year"].isin(filters["years"]) & df["quarter"].isin(filters["quarters"])

    fs_f = fs[time_mask(fs)]
    fsr_f = fsr[time_mask(fsr)]
    flp_f = flp[time_mask(flp)]
    ffp_f = ffp[time_mask(ffp)]
    flpr_f = flpr[time_mask(flpr)]

    if filters["customer"]:
        fs_f = fs_f[fs_f["customer_name_original"] == filters["customer"]]
        fsr_f = fsr_f[fsr_f["customer_name_original"] == filters["customer"]]
        # Local/Foreign Purchases and Local Purchase Returns intentionally untouched -
        # no customer relationship exists on any of them.

    if filters["internal_supplier"]:
        flp_f = flp_f[flp_f["supplier_name_original"] == filters["internal_supplier"]]
        # Foreign Purchases intentionally untouched - Internal Supplier only
        # narrows the internal/local purchase stream, never the external one.

    if filters["external_supplier"]:
        ffp_f = ffp_f[ffp_f["supplier_name_original"] == filters["external_supplier"]]
        # Local Purchases intentionally untouched - External Supplier only
        # narrows the foreign/external purchase stream, never the internal one.

    # Sales/Sales Returns and Local Purchase Returns intentionally untouched by
    # either supplier filter - no supplier field exists on Local Purchase
    # Returns (Phase 1/2 finding, reconfirmed against the current workbook),
    # and Sales has no supplier relationship.

    if filters["cost_center"]:
        flpr_f = flpr_f[flpr_f["cost_center_name"] == filters["cost_center"]]
        # Every other fact table intentionally untouched - Cost Center only
        # exists on Local Purchase Returns.

    return {
        "fact_sales": fs_f,
        "fact_sales_returns": fsr_f,
        "fact_local_purchases": flp_f,
        "fact_foreign_purchases": ffp_f,
        "fact_local_purchase_returns": flpr_f,
    }
