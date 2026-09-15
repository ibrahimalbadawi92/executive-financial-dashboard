# -*- coding: utf-8 -*-
"""
Plotly chart builders. Every chart pulls its labels from translations.t()
and its numbers from the already-computed analytical tables - no calculation
happens in this module, only presentation.
"""
import plotly.graph_objects as go
import pandas as pd

from src.translations import t
from src.formatting import format_money_full, format_pct

PALETTE = {
    "primary": "#20C7C7",     # teal (accent)
    "primary_dark": "#1A9E9E",
    "positive": "#3FA772",    # green
    "negative": "#D9574A",    # red
    "warning": "#D9A441",     # amber
    "neutral": "#7E93A7",     # muted blue-gray
    "series": ["#20C7C7", "#7E93A7", "#D9A441", "#D9574A", "#4C7BAF", "#8B6FB3"],
}
APP_BG = "#0B1720"
CARD_BG = "#142530"
GRID_COLOR = "rgba(255,255,255,0.07)"
TEXT_COLOR = "#F5F7FA"
MUTED_TEXT = "#AAB8C2"

_MONTH_ORDER = {
    "en": ["January", "February", "March", "April", "May", "June",
           "July", "August", "September", "October", "November", "December"],
    "ar": ["يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو",
           "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"],
}
_MONTH_ABBR = {
    "en": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
    "ar": ["ينا", "فبر", "مار", "أبر", "ماي", "يون", "يول", "أغس", "سبت", "أكت", "نوف", "ديس"],
}


def _base_layout(fig: go.Figure, title: str, lang: str, height: int = 320, show_title: bool = True) -> go.Figure:
    fig.update_layout(
        title=dict(text=title if show_title else "", font=dict(size=15, color=TEXT_COLOR), x=0.01, xanchor="left"),
        paper_bgcolor=CARD_BG,
        plot_bgcolor=CARD_BG,
        font=dict(family="Segoe UI, Tahoma, Arial, sans-serif", color=TEXT_COLOR, size=12),
        height=height,
        margin=dict(l=10, r=10, t=48 if show_title else 16, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.0, xanchor="right", x=1,
                    font=dict(size=11, color=MUTED_TEXT), bgcolor="rgba(0,0,0,0)"),
        hoverlabel=dict(bgcolor="#1F2E38", font_size=12, font_family="Segoe UI"),
        hovermode="x unified",
    )
    fig.update_xaxes(gridcolor=GRID_COLOR, zeroline=False, linecolor=GRID_COLOR)
    fig.update_yaxes(gridcolor=GRID_COLOR, zeroline=False, linecolor=GRID_COLOR)
    return fig


def annual_bar_chart(annual_df: pd.DataFrame, metric_key: str, lang: str,
                      color: str = None) -> go.Figure:
    """Single-metric bar chart across 2022-2025 (excludes the ALL_PERIOD row)."""
    df = annual_df.drop(index="ALL_PERIOD_2022_2025", errors="ignore")
    years = [str(y) for y in df.index]
    values = df[metric_key].values
    color = color or PALETTE["primary"]
    fig = go.Figure(go.Bar(
        x=years, y=values, marker_color=color,
        hovertemplate="%{x}<br>" + t(metric_key, lang) + ": %{customdata}<extra></extra>",
        customdata=[format_money_full(v, lang) for v in values],
    ))
    # Confirmed bug fix: Plotly auto-infers a LINEAR (numeric) x-axis from
    # purely-numeric-looking strings like "2022"/"2023" regardless of their
    # Python str type, producing fractional in-between ticks (2022.5, ...).
    # Years are discrete categories, never a continuous measurement - force
    # a category axis explicitly rather than relying on string conversion
    # alone (which is not sufficient on its own).
    fig.update_xaxes(type="category")
    return _base_layout(fig, t(metric_key, lang), lang)


def grouped_bar_by_year(annual_df: pd.DataFrame, metric_keys: list, lang: str,
                         title_key: str, colors: list = None, show_title: bool = True) -> go.Figure:
    """Multiple metrics compared side-by-side across years, e.g. Gross Sales vs Returns vs Net."""
    df = annual_df.drop(index="ALL_PERIOD_2022_2025", errors="ignore")
    years = [str(y) for y in df.index]
    colors = colors or PALETTE["series"]
    fig = go.Figure()
    for i, key in enumerate(metric_keys):
        values = df[key].values
        fig.add_trace(go.Bar(
            name=t(key, lang), x=years, y=values, marker_color=colors[i % len(colors)],
            hovertemplate="%{x}<br>" + t(key, lang) + ": %{customdata}<extra></extra>",
            customdata=[format_money_full(v, lang) for v in values],
        ))
    fig.update_layout(barmode="group")
    fig.update_xaxes(type="category")  # years are categories, not a numeric axis - see annual_bar_chart
    return _base_layout(fig, t(title_key, lang), lang, show_title=show_title)


def monthly_trend_multi_year(fact_df: pd.DataFrame, value_col: str, lang: str,
                              title_key: str, agg: str = "sum", show_title: bool = True,
                              working_days_df: pd.DataFrame = None) -> go.Figure:
    """
    One line per year, x-axis = chronologically-ordered month name - this is
    the "one 4-year monthly comparison chart" shape (management request):
    every calendar month sits at the same x position across all four year
    lines, so e.g. every January is directly comparable.

    working_days_df (optional, columns: year, month, working_days), when
    given, adds the Working Days count for that Year-Month to the hover -
    contextual information only, never a KPI on its own here.
    """
    if fact_df.empty or fact_df[value_col].notna().sum() == 0:
        return _empty_chart(t(title_key, lang), lang, show_title=show_title)
    grp = fact_df.groupby(["year", "month", "month_name_en" if lang == "en" else "month_name_ar"], observed=True)[value_col].agg(agg).reset_index()
    month_col = "month_name_en" if lang == "en" else "month_name_ar"
    order = _MONTH_ORDER[lang]
    if working_days_df is not None:
        grp = grp.merge(working_days_df[["year", "month", "working_days"]], on=["year", "month"], how="left")
    fig = go.Figure()
    years = sorted(grp["year"].dropna().unique())
    wd_label = t("working_days", lang)
    for i, y in enumerate(years):
        sub = grp[grp["year"] == y].set_index(month_col).reindex(order).reset_index()
        if working_days_df is not None:
            hover = ("%{x} " + str(int(y)) + "<br>%{customdata[0]}<br>" + wd_label + ": %{customdata[1]}<extra></extra>")
            customdata = [[format_money_full(v, lang), ("—" if pd.isna(wd) else int(wd))]
                          for v, wd in zip(sub[value_col], sub.get("working_days", pd.Series([None] * len(sub))))]
        else:
            hover = "%{x} " + str(int(y)) + "<br>%{customdata}<extra></extra>"
            customdata = [format_money_full(v, lang) for v in sub[value_col]]
        fig.add_trace(go.Scatter(
            x=sub[month_col], y=sub[value_col], mode="lines+markers", name=str(int(y)),
            line=dict(width=2.2, color=PALETTE["series"][i % len(PALETTE["series"])]),
            marker=dict(size=5),
            hovertemplate=hover,
            customdata=customdata,
        ))
    fig.update_xaxes(categoryorder="array", categoryarray=order)
    return _base_layout(fig, t(title_key, lang), lang, height=340, show_title=show_title)


def dual_series_monthly_trend(df_a: pd.DataFrame, col_a: str, name_a: str,
                               df_b: pd.DataFrame, col_b: str, name_b: str, lang: str,
                               title_key: str, show_title: bool = True) -> go.Figure:
    """
    Two lines (e.g. Local vs Foreign Purchases), x-axis = chronologically-
    ordered month name, values aggregated across every year currently in
    scope (not split by year - see monthly_trend_multi_year for the
    per-year-series shape).
    """
    month_col = "month_name_en" if lang == "en" else "month_name_ar"
    order = _MONTH_ORDER[lang]

    def _monthly_series(df, col):
        if df.empty:
            return pd.Series([0.0] * len(order), index=order)
        g = df.groupby(month_col, observed=True)[col].sum()
        return g.reindex(order).fillna(0.0)

    sa = _monthly_series(df_a, col_a)
    sb = _monthly_series(df_b, col_b)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=order, y=sa.values, mode="lines+markers", name=name_a,
                              line=dict(width=2.5, color=PALETTE["primary"]),
                              customdata=[format_money_full(v, lang) for v in sa.values],
                              hovertemplate="%{x}<br>" + name_a + ": %{customdata}<extra></extra>"))
    fig.add_trace(go.Scatter(x=order, y=sb.values, mode="lines+markers", name=name_b,
                              line=dict(width=2.5, color=PALETTE["neutral"], dash="dot"),
                              customdata=[format_money_full(v, lang) for v in sb.values],
                              hovertemplate="%{x}<br>" + name_b + ": %{customdata}<extra></extra>"))
    fig.update_xaxes(categoryorder="array", categoryarray=order)
    return _base_layout(fig, t(title_key, lang), lang, height=340, show_title=show_title)


def continuous_monthly_trend(monthly_df: pd.DataFrame, value_col: str, lang: str, title_key: str,
                              show_title: bool = True, working_days_df: pd.DataFrame = None,
                              tick_every: int = 3) -> go.Figure:
    """
    ONE continuous line across the full chronological range of `monthly_df`
    (management request, explicit correction: NOT four per-year lines - the
    x-axis never resets after December, Januarys from different years are
    never grouped together). `monthly_df` must have one row per (year,
    month), already sorted chronologically (see
    financial_metrics.monthly_net_sales_series) - every point is plotted and
    hoverable; only the axis TICK LABELS are thinned (every `tick_every`-th
    month, e.g. quarterly) to avoid clutter.
    """
    abbr = _MONTH_ABBR[lang]
    labels = [f"{abbr[int(m) - 1]} {int(y)}" for y, m in zip(monthly_df["year"], monthly_df["month"])]
    values = monthly_df[value_col].values

    if working_days_df is not None:
        merged = monthly_df.merge(working_days_df[["year", "month", "working_days"]], on=["year", "month"], how="left")
        wd_label = t("working_days", lang)
        customdata = [[format_money_full(v, lang), ("—" if pd.isna(w) else str(int(w)))]
                      for v, w in zip(values, merged["working_days"])]
        hover = "%{x}<br>%{customdata[0]}<br>" + wd_label + ": %{customdata[1]}<extra></extra>"
    else:
        customdata = [format_money_full(v, lang) for v in values]
        hover = "%{x}<br>%{customdata}<extra></extra>"

    fig = go.Figure(go.Scatter(
        x=labels, y=values, mode="lines+markers",
        line=dict(width=2.2, color=PALETTE["primary"]),
        marker=dict(size=4),
        hovertemplate=hover,
        customdata=customdata,
    ))
    fig.update_xaxes(categoryorder="array", categoryarray=labels,
                      tickmode="array", tickvals=labels[::tick_every], ticktext=labels[::tick_every])
    return _base_layout(fig, t(title_key, lang), lang, height=360, show_title=show_title)


def horizontal_top_n_bar(df: pd.DataFrame, label_col: str, value_col: str, lang: str,
                          title: str, n: int = 10, show_title: bool = True) -> go.Figure:
    top = df.head(n).iloc[::-1]  # reverse so #1 renders at the top
    fig = go.Figure(go.Bar(
        x=top[value_col], y=top[label_col], orientation="h",
        marker_color=PALETTE["primary"],
        hovertemplate="%{y}<br>%{customdata}<extra></extra>",
        customdata=[format_money_full(v, lang) for v in top[value_col]],
    ))
    fig.update_yaxes(automargin=True)
    return _base_layout(fig, title, lang, height=max(320, 28 * len(top) + 90), show_title=show_title)


def type_mix_bar(series: dict, lang: str, title: str, key_labels: dict, show_title: bool = True) -> go.Figure:
    """series: {normalized_type_key: value}. key_labels: {normalized_type_key: translation_key}."""
    labels = [t(key_labels.get(k, k), lang) if key_labels.get(k) else k for k in series.keys()]
    values = list(series.values())
    fig = go.Figure(go.Bar(
        x=labels, y=values, marker_color=PALETTE["series"][:len(values)],
        hovertemplate="%{x}<br>%{customdata}<extra></extra>",
        customdata=[format_money_full(v, lang) for v in values],
    ))
    return _base_layout(fig, title, lang, show_title=show_title)


def dual_line_chart(annual_df: pd.DataFrame, key_a: str, key_b: str, lang: str,
                     title_key: str, show_title: bool = True) -> go.Figure:
    df = annual_df.drop(index="ALL_PERIOD_2022_2025", errors="ignore")
    years = [str(y) for y in df.index]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=years, y=df[key_a], mode="lines+markers", name=t(key_a, lang),
                              line=dict(width=2.5, color=PALETTE["primary"]),
                              customdata=[format_money_full(v, lang) for v in df[key_a]],
                              hovertemplate="%{x}<br>" + t(key_a, lang) + ": %{customdata}<extra></extra>"))
    fig.add_trace(go.Scatter(x=years, y=df[key_b], mode="lines+markers", name=t(key_b, lang),
                              line=dict(width=2.5, color=PALETTE["neutral"], dash="dot"),
                              customdata=[format_money_full(v, lang) for v in df[key_b]],
                              hovertemplate="%{x}<br>" + t(key_b, lang) + ": %{customdata}<extra></extra>"))
    fig.update_xaxes(type="category")  # years are categories, not a numeric axis - see annual_bar_chart
    return _base_layout(fig, t(title_key, lang), lang, show_title=show_title)


def rate_trend_chart(annual_df: pd.DataFrame, metric_key: str, lang: str, title_key: str,
                      show_title: bool = True) -> go.Figure:
    df = annual_df.drop(index="ALL_PERIOD_2022_2025", errors="ignore")
    years = [str(y) for y in df.index]
    fig = go.Figure(go.Scatter(
        x=years, y=df[metric_key], mode="lines+markers+text",
        line=dict(width=2.5, color=PALETTE["warning"]), marker=dict(size=8),
        text=[format_pct(v) for v in df[metric_key]], textposition="top center",
        textfont=dict(color=MUTED_TEXT, size=11),
        hovertemplate="%{x}: %{text}<extra></extra>",
    ))
    fig.update_xaxes(type="category")  # years are categories, not a numeric axis - see annual_bar_chart
    return _base_layout(fig, t(title_key, lang), lang, show_title=show_title)


def reconciliation_status_bar(counts_by_sheet: dict, lang: str, title: str, show_title: bool = True) -> go.Figure:
    """counts_by_sheet: {sheet_label: {"Valid": n, "Reconciliation-Review": n, ...}}"""
    status_keys = ["status_valid", "status_reconciliation_review", "status_corrupt_excluded"]
    status_raw = ["Valid", "Reconciliation-Review", "Corrupt-Excluded"]
    colors = [PALETTE["positive"], PALETTE["warning"], PALETTE["negative"]]
    sheets = list(counts_by_sheet.keys())
    fig = go.Figure()
    for raw_status, key, color in zip(status_raw, status_keys, colors):
        values = [counts_by_sheet[s].get(raw_status, 0) for s in sheets]
        if sum(values) == 0:
            continue
        fig.add_trace(go.Bar(name=t(key, lang), x=sheets, y=values, marker_color=color))
    fig.update_layout(barmode="stack")
    return _base_layout(fig, title, lang, height=340, show_title=show_title)


def _empty_chart(title: str, lang: str, show_title: bool = True) -> go.Figure:
    fig = go.Figure()
    fig.add_annotation(text="—", showarrow=False, font=dict(size=14, color=MUTED_TEXT))
    return _base_layout(fig, title, lang, height=280, show_title=show_title)
