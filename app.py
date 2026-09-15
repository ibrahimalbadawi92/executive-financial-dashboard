# -*- coding: utf-8 -*-
"""
Executive Financial & Accounting Performance Dashboard - entry point.
Bilingual (AR/EN), read-only against the source workbook.
"""
from pathlib import Path

import streamlit as st

from src.translations import t, direction
from src import data_pipeline, filters as filters_mod
from src import ui_components as ui
from src.pages import (
    executive_overview, sales_performance, purchasing_performance, returns_analysis,
    vat_analysis, customers_suppliers, yoy_analysis, data_quality, supplier_balances,
)

if "lang" not in st.session_state:
    st.session_state.lang = "en"
if "page" not in st.session_state:
    st.session_state.page = "nav_executive_overview"
LANG = st.session_state.lang

st.set_page_config(page_title=t("app_title", LANG), page_icon="📊", layout="wide",
                    initial_sidebar_state="expanded")


def _inject_css(lang: str):
    css_path = Path(__file__).parent / "assets" / "styles.css"
    base_css = css_path.read_text(encoding="utf-8")
    dir_css = f"""
    [data-testid="stAppViewContainer"] {{ direction: {direction(lang)}; }}
    [data-testid="stSidebar"] {{ direction: {direction(lang)}; }}
    """
    # Arabic script reads more comfortably a little larger and with more
    # line-height than Latin text at the same pixel size - bump the compact
    # accounting-note style (used by the Gap disclaimer) for Arabic only.
    # Padding/margin are untouched, so the box grows only as much as the
    # slightly larger text naturally requires.
    lang_css = """
    .efd-note-compact { font-size: 0.84rem; line-height: 1.7; }
    """ if lang == "ar" else ""
    st.markdown(f"<style>{base_css}\n{dir_css}\n{lang_css}</style>", unsafe_allow_html=True)


_inject_css(LANG)

NAV_PAGES = [
    ("nav_executive_overview", executive_overview),
    ("nav_sales_performance", sales_performance),
    ("nav_purchasing_performance", purchasing_performance),
    ("nav_returns_analysis", returns_analysis),
    ("nav_vat_analysis", vat_analysis),
    ("nav_customers_suppliers", customers_suppliers),
    ("nav_yoy_analysis", yoy_analysis),
    ("nav_supplier_balances", supplier_balances),
    ("nav_data_quality", data_quality),
]
PAGE_MODULES = dict(NAV_PAGES)

# Loaded once per process (st.cache_resource) - safe to call before the sidebar.
bundle = data_pipeline.load_pipeline()

with st.sidebar:
    ui.brand_header(LANG)

    lang_choice = st.segmented_control(
        "lang", ["English", "العربية"],
        default="English" if LANG == "en" else "العربية",
        label_visibility="collapsed", key="lang_seg", width="stretch",
    )
    new_lang = "en" if lang_choice == "English" else "ar"

    def _set_page(page_key):
        st.session_state.page = page_key

    ui.sidebar_label(t("nav_section_label", LANG))
    for key, _mod in NAV_PAGES:
        # State update happens in on_click (fires BEFORE the script re-executes
        # to draw widgets), not via st.rerun() and not via "if button clicked"
        # after the fact - see ui_components.nav_button docstring for the
        # confirmed root cause this fixes (nav highlight lagging one click
        # behind the actually-rendered page). No explicit st.rerun() is used
        # here (that previously broke filter persistence on navigation).
        ui.nav_button(t(key, LANG), active=(st.session_state.page == key), key=f"nav_btn_{key}",
                      on_click=_set_page, args=(key,))

    ui.sidebar_label(t("filters_section_label", LANG))
    active_filters = filters_mod.render_sidebar_filters(bundle, LANG)

    # The language-triggered rerun is deliberately fired down here, AFTER every
    # keyed sidebar widget above (nav buttons, all six filters) has already
    # been declared in this same script pass - not before it, as a prior
    # version did. Confirmed root cause of a filter-reset-on-language-toggle
    # bug: st.rerun() aborts the CURRENT run immediately, and Streamlit treats
    # any keyed widget that was NOT yet declared at the point of that abort as
    # absent from this run's active-widget set, clearing its session_state
    # entry as "orphaned" - so every filter's seed-if-absent logic in
    # filters.py then reseeds it to its default on the next run. Declaring all
    # widgets first means they're always counted as active in the run that
    # triggers the rerun, so their session_state survives untouched into the
    # next (re-language) run. Purely a reordering - no new state, no changed
    # widget keys, no duplicated filter logic.
    if new_lang != LANG:
        st.session_state.lang = new_lang
        st.rerun()

filtered = filters_mod.apply_filters(bundle, active_filters)
computed = data_pipeline.compute_filtered_bundle(bundle, filtered, active_filters)

selected_module = PAGE_MODULES.get(st.session_state.page, executive_overview)
selected_module.render(bundle, filtered, computed, LANG)
