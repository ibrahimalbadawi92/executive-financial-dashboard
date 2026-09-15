# -*- coding: utf-8 -*-
"""
Reusable Streamlit UI building blocks - every page composes these instead of
hand-rolling markup, so the executive look stays consistent everywhere.
KPI cards are custom HTML (not raw st.metric) so exact values live INSIDE the
card as subtle secondary text, never as a detached line underneath it.

All KPI/definition tooltips (KPI cards, Data Quality badges, chart section
headers) render through info_popover() - a custom dark popover, not the
browser's native `title` attribute - so they look consistent and support
hover, click/tap and keyboard use uniformly.
"""
import streamlit as st
import pandas as pd

from src.translations import t
from src.formatting import format_money, format_money_full, format_pct, format_int, year_range_text, bidi_isolate
from src.kpi_metadata import get_kpi_tooltip
from src.chart_metadata import get_chart_tooltip


def brand_header(lang: str):
    st.markdown(
        f'<div class="efd-brand">'
        f'<div class="efd-brand-title">{t("app_title", lang)}</div>'
        f'<div class="efd-brand-subtitle">{t("currency_code", lang)} · {year_range_text(2022, 2025, lang)}</div>'
        f'<div class="efd-brand-disclaimer">{t("portfolio_disclaimer", lang)}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def sidebar_label(text: str):
    st.markdown(f'<div class="efd-sidebar-label">{text}</div>', unsafe_allow_html=True)


def row_spacer():
    """
    Guarantees clearance between two consecutive st.columns() row blocks.
    Streamlit's own internal wrapper (one level inside [data-testid="stMarkdown"])
    reports a measured height consistently ~16px shorter than our styled cards'
    true rendered height (verified empirically per-page via getBoundingClientRect
    - even a JS-forced inline `height:auto !important` on that wrapper does not
    change it, so this is not fixable via a CSS override on the card itself).
    Left uncorrected, a card row's true content overflows into the next
    st.columns() row. This is a deliberate, measured correction, not a blank
    filler - see kpi_row() below for the standard way to apply it.
    """
    st.markdown('<div class="efd-row-spacer"></div>', unsafe_allow_html=True)


def kpi_row(n: int, first: bool = False):
    """
    THE way to open a row of KPI/status cards (st.columns() for
    kpi_from_metrics()/dq_status_badge() calls) anywhere in the dashboard.
    Automatically inserts row_spacer() before every row except the first one
    on a page, so multi-row KPI grids never need a page-specific spacer call
    and never collide - one reusable fix instead of per-page hacks.

    Usage:
        c1, c2, c3, c4 = kpi_row(4, first=True)
        ...
        c5, c6, c7 = kpi_row(3)   # spacer inserted automatically
    """
    if not first:
        row_spacer()
    return st.columns(n)


def nav_button(label: str, active: bool, key: str, on_click=None, args: tuple = ()) -> bool:
    """
    Root-cause fix for the confirmed nav-highlight-lags-by-one-click bug:
    `active` used to be computed from st.session_state.page BEFORE the click
    that might change it was processed (Python must call st.button() to get
    its return value, and Streamlit has already sent this button's
    primary/secondary type to the browser by the time that return value is
    known) - so the just-clicked button always rendered with its OLD
    (pre-click) highlight state, one page behind, every time.

    Fix: do the state update in `on_click` (Streamlit invokes callbacks
    BEFORE the script reruns to draw widgets), so by the time `active` is
    computed for THIS button - and every other nav button drawn after it in
    the same pass - st.session_state.page already reflects the click. No
    explicit st.rerun() is introduced (that previously broke filter
    persistence on navigation - see app.py's nav loop comment).
    """
    return st.button(label, key=key, type="primary" if active else "secondary", width="stretch",
                      on_click=on_click, args=args)


def page_header(title_key: str, lang: str, subtitle: str = None):
    st.markdown(f'<div class="efd-page-title">{t(title_key, lang)}</div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="efd-page-subtitle">{subtitle}</div>', unsafe_allow_html=True)


def selected_period_subtitle(active_filters: dict, lang: str) -> str:
    """
    'Selected Period: 2022-2025' / 'Selected Period: 2025' / 'Selected Period:
    2025 · Q1' - reflects the active Year/Quarter filter so every page (not
    just Executive Overview) visibly confirms the filter took effect. Derived
    from the filter SELECTION itself (active_filters), not from the filtered
    fact tables, so it stays accurate even when a Customer/Supplier filter
    happens to leave zero rows in a selected year/quarter.
    """
    years = sorted(active_filters.get("years") or [])
    quarters = sorted(active_filters.get("quarters") or [])
    label = t("selected_period", lang)
    if not years:
        return label
    parts = [year_range_text(years[0], years[-1], lang)]
    if quarters and len(quarters) < 4:
        q_str = ", ".join(f"Q{q}" for q in quarters)
        parts.append(bidi_isolate(q_str) if lang == "ar" else q_str)
    return f"{label}: " + " · ".join(parts)


def info_popover(text: str) -> str:
    """
    HTML for a subtle ⓘ icon + custom dark popover - hover, click/tap and
    keyboard-Tab all work via CSS :hover/:focus/:focus-within (the icon is a
    real tabindex target, so a tap/click focuses it and the popover shows;
    clicking anywhere else moves focus away and it closes automatically -
    standard DOM focus behavior, no JS needed for that part).

    No native browser `title` tooltip and no <script> tag - Streamlit's
    markdown sanitizer strips <script> tags AND inline event-handler
    attributes (onclick, onkeydown, etc.) from unsafe_allow_html content
    (verified empirically: an onkeydown attribute placed here is silently
    removed before it reaches the DOM). That means Escape-to-close cannot be
    implemented - there is no JS execution path available to intercept it.
    Tab (moving focus to the next element) is the keyboard way to dismiss the
    popover instead.

    Returns "" when there is nothing to show, so callers can splice it in
    unconditionally.
    """
    if not text:
        return ""
    return (
        '<span class="efd-info-wrap" tabindex="0">'
        '<span class="efd-info-icon" aria-hidden="true">ⓘ</span>'
        f'<span class="efd-info-popover" role="tooltip">{text}</span>'
        '</span>'
    )


def section_header(text: str, info_html: str = ""):
    st.markdown(f'<div class="efd-section-header">{text}{info_html}</div>', unsafe_allow_html=True)


def chart_section_header(text_key: str, lang: str):
    """
    section_header() with its chart-explanation popover attached
    automatically, looked up from src/chart_metadata.py by the SAME
    translation key already used for the header text - no page hardcodes
    chart explanation text.
    """
    tooltip = get_chart_tooltip(text_key, lang)
    section_header(t(text_key, lang), info_popover(tooltip))


def bidi_num(s: str, lang: str) -> str:
    """
    Wraps a formatted numeric/money/percent string in a bidi-isolating <bdi>
    for safe embedding inside RTL (Arabic) HTML - fixes negative values
    visually relocating their sign (e.g. "34.0%-" instead of "-34.0%")
    under the Unicode bidi algorithm. No-op in English. ONLY use on strings
    headed into unsafe_allow_html HTML - never inside a Plotly
    hovertemplate/customdata string (that would print a literal <bdi> tag).
    """
    return bidi_isolate(s) if lang == "ar" and s else s


def _delta_html(pct, ref_label: str, delta_color: str, lang: str = "en") -> str:
    if pct is None or pd.isna(pct):
        return '<span class="efd-kpi-delta efd-neutral">—</span>'
    is_increase = pct >= 0
    arrow = "↑" if is_increase else "↓"
    if delta_color == "off":
        css_class = "efd-neutral"
    elif delta_color == "inverse":
        css_class = "efd-neg" if is_increase else "efd-pos"
    else:  # "normal"
        css_class = "efd-pos" if is_increase else "efd-neg"
    pct_str = bidi_num(f"{abs(pct):,.1f}%", lang)
    return f'<span class="efd-kpi-delta {css_class}">{arrow} {pct_str} {ref_label}</span>'


def kpi_card_html(label: str, value: str, delta_html: str = "", exact_value: str = "",
                   tooltip: str = None, extra_badge_html: str = ""):
    icon_html = info_popover(tooltip)
    st.markdown(
        f'<div class="efd-kpi-card">'
        f'<div class="efd-kpi-label">{label}{icon_html}{extra_badge_html}</div>'
        f'<div class="efd-kpi-value">{value}</div>'
        f'<div class="efd-kpi-footer">{delta_html}<span class="efd-kpi-exact">{exact_value}</span></div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def kpi_from_metrics(metric_key: str, current_metrics: dict, lang: str,
                      comparison_metrics: dict = None, comparison_label: str = None,
                      delta_color: str = "normal", tooltip_key: str = None, badge_key: str = None,
                      show_exact: bool = False):
    """
    Builds a KPI card for `metric_key` using the currently-filtered value plus
    a delta against `comparison_metrics`/`comparison_label` - the
    scope-matched previous period for the ACTIVE filter selection (see
    data_pipeline.compute_comparison_period). When comparison_metrics is
    None (no single meaningful previous period for the current selection),
    the card shows a neutral "—" delta rather than a mismatched-scope
    percentage with a misleading label - this was a confirmed bug (delta
    always said "vs <year>" while silently comparing full-year figures
    regardless of an active Quarter filter).

    show_exact=False (the default) hides the exact-value footer text and
    instead folds the exact value into the card's popover tooltip, so long
    exact values never CSS-ellipsis-truncate inside the fixed-width footer
    (confirmed truncation bug - fixed centrally here rather than per page).
    Pass show_exact=True only where a page deliberately wants the exact
    value visible in the footer AND has room for it.

    The KPI definition (formula, in business language) is looked up
    automatically from src/kpi_metadata.py by metric_key - callers never
    hardcode definition text. `tooltip_key` (a translations.py key, when
    given) supplies an *additional* note - e.g. a data-quality caveat - that
    is appended after the definition rather than replacing it.
    """
    value = current_metrics.get(metric_key)
    is_pct = metric_key.endswith("_pct")
    is_count = metric_key.endswith("_count")

    if is_pct:
        display_value, exact_value = format_pct(value), ""
    elif is_count:
        display_value, exact_value = format_int(value), ""
    else:
        display_value = format_money(value, lang)
        exact_value = format_money_full(value, lang)
    display_value = bidi_num(display_value, lang)
    exact_value = bidi_num(exact_value, lang)

    delta_html = _delta_html(None, "", delta_color, lang)
    value_available = value is not None and not (isinstance(value, float) and pd.isna(value))
    if value_available and comparison_metrics is not None and metric_key in comparison_metrics:
        cur_v, prev_v = value, comparison_metrics[metric_key]
        pct = None
        if prev_v is not None and prev_v not in (0,) and prev_v == prev_v:
            pct = (cur_v - prev_v) / prev_v * 100
        ref_label = f"vs {comparison_label}" if lang == "en" else f"مقابل {comparison_label}"
        delta_html = _delta_html(pct, ref_label, delta_color, lang)

    definition_tooltip = get_kpi_tooltip(metric_key, lang)
    extra_tooltip = t(tooltip_key, lang) if tooltip_key else None
    tooltip = " ".join(p for p in (definition_tooltip, extra_tooltip) if p) or None
    badge_html = f'<span class="efd-badge-not-profit">{t(badge_key, lang)}</span>' if badge_key else ""

    if show_exact:
        footer_exact = exact_value
    else:
        footer_exact = ""
        if exact_value:
            tooltip = f"{tooltip} — {exact_value}" if tooltip else exact_value

    kpi_card_html(t(metric_key, lang), display_value, delta_html, footer_exact, tooltip, badge_html)


def disclaimer_box(text_key: str, lang: str, kind: str = "info", compact: bool = False):
    """kind: 'info' (teal), 'warning' (amber), 'critical' (red)."""
    css_class = {"info": "efd-note-info", "warning": "efd-note-warning", "critical": "efd-note-critical"}[kind]
    if compact:
        css_class += " efd-note-compact"
    st.markdown(f'<div class="{css_class}">{t(text_key, lang)}</div>', unsafe_allow_html=True)


def raw_note_box(text: str, kind: str = "info", compact: bool = False):
    css_class = {"info": "efd-note-info", "warning": "efd-note-warning", "critical": "efd-note-critical"}[kind]
    if compact:
        css_class += " efd-note-compact"
    st.markdown(f'<div class="{css_class}">{text}</div>', unsafe_allow_html=True)


def insight_panel(title: str, insights: list):
    rows = "".join(f'<div class="efd-insight-row"><span class="efd-insight-dot"></span><span>{i["text"]}</span></div>'
                    for i in insights)
    st.markdown(f'<div class="efd-panel"><div class="efd-panel-title">{title}</div>{rows}</div>',
                unsafe_allow_html=True)


def attention_panel(title: str, items: list, empty_text: str):
    """items: list of {"text": str, "level": "warning"|"critical"}"""
    if items:
        rows = "".join(
            f'<div class="efd-insight-row efd-attention-row{" efd-attention-critical" if it.get("level")=="critical" else ""}">'
            f'<span>{it["text"]}</span></div>'
            for it in items
        )
    else:
        rows = f'<div class="efd-attention-empty">{empty_text}</div>'
    st.markdown(f'<div class="efd-panel"><div class="efd-panel-title">{title}</div>{rows}</div>',
                unsafe_allow_html=True)


def insight_list(insights: list):
    """Kept for pages that render a plain insight list without a panel wrapper."""
    items = "".join(f'<div class="efd-insight-row"><span class="efd-insight-dot"></span><span>{i["text"]}</span></div>'
                     for i in insights)
    st.markdown(f'<div>{items}</div>', unsafe_allow_html=True)


def dq_status_badge(label: str, count, kind: str = "valid", help_text: str = None):
    """kind: 'valid' green, 'warning' amber, 'critical' red. help_text (if given)
    renders via the same custom popover used by KPI cards - the badge stays a
    compact number on normal pages while the full explanation is one hover/
    tap away, never a native browser tooltip.
    `count` may be a number (comma-formatted automatically) or an already-
    formatted string (e.g. a percentage) - kept as one component so every
    card in a Data Quality row renders at the same height."""
    css_class = {"valid": "efd-badge-valid", "warning": "efd-badge-warning", "critical": "efd-badge-critical"}[kind]
    count_str = f"{count:,}" if isinstance(count, (int, float)) else str(count)
    icon_html = info_popover(help_text)
    st.markdown(
        f'<div class="efd-dq-badge {css_class}"><span class="efd-dq-count">{count_str}</span>'
        f'<span class="efd-dq-label">{label}{icon_html}</span></div>',
        unsafe_allow_html=True,
    )
