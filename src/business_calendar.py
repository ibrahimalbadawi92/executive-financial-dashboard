# -*- coding: utf-8 -*-
"""
Centralized, configurable business calendar (management request, new-workbook
update). Working Days = Calendar Days - unique Fridays - unique Eid holiday
dates falling in that month, computed programmatically from
config.BUSINESS_HOLIDAYS - never hardcoded per month, and never
double-subtracting a Friday that also falls inside an Eid block.

Only Friday + the two configured Eid blocks are excluded. Saturday and any
other public holiday (e.g. Saudi National Day) are deliberately NOT
subtracted unless management explicitly requests them later - see
config.BUSINESS_HOLIDAYS docstring.
"""
import pandas as pd

import config


def _all_eid_holiday_dates() -> set:
    """Every individual calendar date covered by a configured Eid block,
    across all years in config.BUSINESS_HOLIDAYS - a plain set of Timestamps,
    so a block that crosses a month or year boundary (e.g. Eid Al-Adha 2023:
    Jun 28 - Jul 4) is still attributed to the correct actual month."""
    dates = set()
    for holidays in config.BUSINESS_HOLIDAYS.values():
        for key in ("eid_fitr_start", "eid_adha_start"):
            start = pd.Timestamp(holidays[key])
            for i in range(config.EID_HOLIDAY_LENGTH_DAYS):
                dates.add((start + pd.Timedelta(days=i)).normalize())
    return dates


_EID_DATES = _all_eid_holiday_dates()


def working_days_in_month(year: int, month: int) -> int:
    """Working Days = Calendar Days - unique Fridays - unique Eid holiday
    dates within the month (union, not sum, so an Eid day that is also a
    Friday is subtracted only once)."""
    start = pd.Timestamp(year=year, month=month, day=1)
    end = start + pd.offsets.MonthEnd(0)
    days = pd.date_range(start, end, freq="D")
    non_working = {d for d in days if d.dayofweek in config.WEEKLY_NON_WORKING_DOW} | \
                  {d for d in days if d in _EID_DATES}
    return len(days) - len(non_working)


def working_days_table(years=config.ANALYSIS_YEARS) -> pd.DataFrame:
    """One row per (year, month) with its computed Working Days count -
    convenient for merging into monthly aggregates without recomputing per
    row. Also carries bilingual month names for chart labels."""
    from src.data_model import _MONTH_NAMES_EN, _MONTH_NAMES_AR

    rows = []
    for y in years:
        for m in range(1, 13):
            rows.append({
                "year": y,
                "month": m,
                "month_name_en": _MONTH_NAMES_EN[m - 1],
                "month_name_ar": _MONTH_NAMES_AR[m - 1],
                "working_days": working_days_in_month(y, m),
            })
    return pd.DataFrame(rows)
