# -*- coding: utf-8 -*-
"""
Synthetic portfolio-data generator.

This generator creates fully synthetic portfolio data.
It does not read, transform, anonymize, or derive records from
the original company dataset.

Every row in every sheet is independently sampled from the distributions
and templates defined below. No original workbook is opened, imported, or
referenced anywhere in this file. Names are built from fixed template
lists + numeric counters (never a third-party name-corpus library), so
there is zero chance of coincidentally reproducing a real business's
identifiers.

Run:
    python scripts/generate_synthetic_data.py

Output:
    data/sample_financial_data.xlsx  (8 sheets, matching the exact schema
    src/data_cleaning.py expects - see config.py:SHEET_* for sheet names)

Deterministic: re-running this script produces a byte-for-byte identical
workbook (fixed SEED below), so the "synthetic baseline" documented in the
README/tests is always reproducible from source.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

import config  # noqa: E402  (needs sys.path set up first)

SEED = 20240915
OUT_PATH = PROJECT_ROOT / "data" / "sample_financial_data.xlsx"

YEARS = [2022, 2023, 2024, 2025]
YEAR_WEIGHTS = {2022: 1.00, 2023: 1.12, 2024: 1.18, 2025: 1.08}  # deliberately
# NOT the real dataset's shape (which declined sharply in the final year) -
# this is an independently chosen synthetic trend.
MONTH_WEIGHTS = np.array([0.90, 0.88, 0.95, 1.00, 0.92, 0.85,
                           0.80, 0.90, 1.05, 1.10, 1.15, 1.30])  # mild Q4 push

# --------------------------------------------------------------------------
# Name templates (fixed lists + numeric counters only - never a Faker/name
# corpus, so there is no possibility of coincidentally regenerating a real
# business name).
# --------------------------------------------------------------------------
CUSTOMER_PREFIXES = ["شركة", "مؤسسة", "مصنع", "مجموعة"]
CUSTOMER_CORES = [
    "الأفق", "الريادة", "المدار", "النخبة", "الواحة", "السنابل", "البستان",
    "القمة", "الرواد", "الإتقان", "الشروق", "الازدهار", "الفجر", "المسار",
    "الينابيع", "الرياض المتحدة", "الخليج الحديثة", "التقدم", "الأمانة", "الوفاء",
]
CUSTOMER_SUFFIXES = ["التجارية", "للمقاولات", "للتجارة العامة", "للاستثمار", "للتوريدات"]

INTERNAL_SUPPLIER_CORES = [
    "الأصالة", "المتانة", "الاتحاد", "البناء الحديث", "الإعمار", "الصفوة",
    "المعالم", "الرافدين", "النجاح", "الكفاءة", "الإنجاز", "الثقة",
    "الجودة", "التميز", "الوفرة", "السهل", "النماء", "التطوير", "الابتكار",
    "المستقبل", "الرسالة", "الأمين", "الموثوق", "الدقة", "السرعة", "المرونة",
    "الشراكة", "التكامل", "الريادي", "العطاء",
]
INTERNAL_SUPPLIER_SUFFIXES = ["للتجارة", "للمواد", "للتوريدات العامة", "الصناعية"]

EXTERNAL_SUPPLIER_CORES = [
    "Global Foods Trading", "Northstar Ingredients", "Atlas Supply International",
    "Meridian Commodities", "Blue Harbor Exports", "Continental Parts Trading",
    "Silverline Industrial Supply", "Horizon Equipment Group", "Pacific Rim Sourcing",
    "Ironclad Components", "Vantage Global Trading", "Summit Machinery Exports",
    "Cascade Materials Co", "Beacon Freight & Supply", "Sterling Import Partners",
    "Anchor Point Trading",
]

COST_CENTERS = ["الرياض", "جدة", "الدمام", "القصيم", "المدينة", "أبها"]

SALES_TYPES = ["بيع نقدى", "بيع آجل", "خدمات"]
SALES_TYPE_WEIGHTS = [0.72, 0.20, 0.08]
SALES_RETURN_TYPES = ["مردود نقدى", "مردود آجل"]
PURCHASE_TYPES = ["نقدا", "آجل", "اعتماد"]
PURCHASE_TYPE_WEIGHTS = [0.55, 0.35, 0.10]
PURCHASE_RETURN_TYPES = ["مردود نقدي", "مردود أجل"]

VAT_RATE = config.STANDARD_VAT_RATE  # 0.15 - same public rate, not a secret


def _rng():
    return np.random.default_rng(SEED)


def _make_names(prefixes, cores, suffixes, count, rng):
    """Deterministically build `count` distinct fictional names from the
    template lists above, each tagged with a zero-padded counter so no two
    collide even if the template combination repeats."""
    names = []
    combo_idx = 0
    while len(names) < count:
        p = prefixes[combo_idx % len(prefixes)]
        c = cores[(combo_idx // len(prefixes)) % len(cores)]
        s = suffixes[(combo_idx // (len(prefixes) * len(cores))) % len(suffixes)]
        names.append(f"{p} {c} {s} {len(names) + 1:03d}")
        combo_idx += 1
    rng.shuffle(names)
    return names


def _make_external_names(cores, count, rng):
    names = [f"{cores[i % len(cores)]} {i + 1:03d}" for i in range(count)]
    rng.shuffle(names)
    return names


def _synthetic_vat_id(rng):
    """Structurally-valid-looking (15 digits, starts/ends '3' per the public
    KSA VAT-number format) but fully synthetic - never derived from a real ID."""
    middle = "".join(str(d) for d in rng.integers(0, 10, size=13))
    return "3" + middle + "3"


def _random_dates(n, rng):
    """Sample n dates across 2022-2025 with year weights (YEAR_WEIGHTS) and
    month seasonality (MONTH_WEIGHTS) - independent synthetic trend, not
    fit to any real time series."""
    year_p = np.array([YEAR_WEIGHTS[y] for y in YEARS])
    year_p = year_p / year_p.sum()
    years = rng.choice(YEARS, size=n, p=year_p)
    months = rng.choice(np.arange(1, 13), size=n, p=MONTH_WEIGHTS / MONTH_WEIGHTS.sum())
    days = rng.integers(1, 29, size=n)  # 28 keeps every month valid, incl. Feb
    return [pd.Timestamp(year=int(y), month=int(m), day=int(d)) for y, m, d in zip(years, months, days)]


def _round2(x):
    return np.round(x, 2)


# --------------------------------------------------------------------------
# SALES
# --------------------------------------------------------------------------
def build_sales(rng, customers_df):
    n = 15000
    dates = _random_dates(n, rng)
    types = rng.choice(SALES_TYPES, size=n, p=SALES_TYPE_WEIGHTS)

    # ~18% of transactions are generic walk-in cash sales (customer_no=1,
    # name 'نقدي'); the rest are drawn from the identifiable customer list
    # with a mild concentration skew (a handful of "regular" customers
    # transact more often) so the Top-Customers visual has real texture.
    is_generic = rng.random(n) < 0.18
    named_idx = rng.choice(len(customers_df), size=n, p=customers_df["_weight"].values)

    trnno = rng.integers(1, 40000, size=n)
    net = _round2(rng.gamma(shape=2.2, scale=650.0, size=n) + 15.0)
    vat = _round2(net * VAT_RATE)
    gross = _round2(net + vat)
    qty = rng.integers(1, 40, size=n)

    customer_no = np.where(is_generic, config.GENERIC_CASH_CUSTOMER_NO,
                            customers_df["customer_no"].values[named_idx])
    customer_name = np.where(is_generic, config.GENERIC_CASH_CUSTOMER_NAME,
                              customers_df["customer_name"].values[named_idx])
    customer_vat = np.where(is_generic, "", customers_df["vat_id"].values[named_idx])

    df = pd.DataFrame({
        "trnno": trnno,
        "trndat": dates,
        "type": types,
        "customer no": customer_no,
        "customer name": customer_name,
        "customer vat id": customer_vat,
        "Net invoice without tax": net,
        "total tax": vat,
        "total invoice with tax": gross,
        "quntity": qty,
    })
    df = df.sort_values("trndat").reset_index(drop=True)

    # One embedded grand-total row (trnno blank), monetary columns equal to
    # the sum of the real rows above it - this is the minimum structural
    # row the loader's null-key-row rule needs to exercise the Data Quality
    # "excluded analytical row" logic.
    total_row = pd.DataFrame([{
        "trnno": np.nan, "trndat": pd.NaT, "type": np.nan,
        "customer no": np.nan, "customer name": np.nan, "customer vat id": np.nan,
        "Net invoice without tax": df["Net invoice without tax"].sum(),
        "total tax": df["total tax"].sum(),
        "total invoice with tax": df["total invoice with tax"].sum(),
        "quntity": np.nan,
    }])
    return pd.concat([df, total_row], ignore_index=True), df


# --------------------------------------------------------------------------
# SALES RETURNS
# --------------------------------------------------------------------------
def build_sales_returns(rng, fact_sales_real):
    n = 950
    # Link a majority of returns to a genuinely-sampled synthetic sale (same
    # trnno + same date), so the app's best-effort match-status feature has
    # real "Matched" rows to demonstrate - the remainder are intentionally
    # unlinked ("Unmatched"), which is the realistic majority case even in
    # the original schema (trnno is not a reliable invoice key).
    sample = fact_sales_real.sample(n=min(n, len(fact_sales_real)), random_state=int(SEED)).reset_index(drop=True)
    link_mask = rng.random(len(sample)) < 0.35

    ref_no = np.arange(1, len(sample) + 1)
    dates = sample["trndat"].where(link_mask, other=pd.Series(_random_dates(len(sample), rng)))
    original_trnno_ref = sample["trnno"].where(link_mask, other=rng.integers(1, 40000, size=len(sample)))
    types = rng.choice(SALES_RETURN_TYPES, size=len(sample), p=[0.78, 0.22])

    value = _round2(rng.gamma(shape=1.8, scale=420.0, size=len(sample)) + 10.0)
    vat = _round2(value * VAT_RATE)
    total = _round2(value + vat)
    qty = rng.integers(1, 15, size=len(sample))

    df = pd.DataFrame({
        "رقم فاتورةالمردود": ref_no,
        "تاريخ الفاتورة": dates.values,
        "نوع الفاتورة": types,
        "رقم فاتورة المبيعات": original_trnno_ref,
        "اسم العميل": sample["customer name"].values,
        "القيمة": value,
        "الضريبة": vat,
        "الصافي بالضريبة": total,
        "الكمية": qty,
    })

    total_row = pd.DataFrame([{
        "رقم فاتورةالمردود": np.nan, "تاريخ الفاتورة": pd.NaT, "نوع الفاتورة": np.nan,
        "رقم فاتورة المبيعات": np.nan, "اسم العميل": "اجمالى التقرير",
        "القيمة": df["القيمة"].sum(), "الضريبة": df["الضريبة"].sum(),
        "الصافي بالضريبة": df["الصافي بالضريبة"].sum(), "الكمية": np.nan,
    }])
    return pd.concat([df, total_row], ignore_index=True)


# --------------------------------------------------------------------------
# LOCAL (INTERNAL) PURCHASES
# --------------------------------------------------------------------------
def build_local_purchases(rng, internal_suppliers):
    n = 2800
    dates = _random_dates(n, rng)
    types = rng.choice(PURCHASE_TYPES, size=n, p=PURCHASE_TYPE_WEIGHTS)

    # One supplier ("عام" - "general") deliberately carries an above-average
    # share, mirroring a real, documented, ALREADY-BUILT dashboard feature
    # (generic/unspecified-supplier exclusion from concentration ranking) -
    # not a fabricated data-quality error, a genuine business category the
    # app already knows how to explain.
    weights = np.ones(len(internal_suppliers))
    generic_pos = internal_suppliers.index("عام")
    weights[generic_pos] = 6.0
    weights = weights / weights.sum()
    supplier_idx = rng.choice(len(internal_suppliers), size=n, p=weights)
    suppliers = np.array(internal_suppliers)[supplier_idx]

    trnno = rng.integers(1, 40000, size=n)
    purtot = _round2(rng.gamma(shape=2.0, scale=900.0, size=n) + 20.0)
    tax = _round2(purtot * VAT_RATE)
    total = _round2(purtot + tax)
    qty = rng.integers(1, 60, size=n)

    df = pd.DataFrame({
        "trnno": trnno, "date": dates, "type": types, "supplier": suppliers,
        "purtot": purtot, "tax": tax, "total with tax": total, "qty": qty,
    })

    total_row = pd.DataFrame([{
        "trnno": np.nan, "date": pd.NaT, "type": np.nan, "supplier": np.nan,
        "purtot": df["purtot"].sum(), "tax": df["tax"].sum(),
        "total with tax": df["total with tax"].sum(), "qty": np.nan,
    }])
    return pd.concat([df, total_row], ignore_index=True)


# --------------------------------------------------------------------------
# FOREIGN (EXTERNAL) PURCHASES - no VAT field, purtot + addcost = total
# --------------------------------------------------------------------------
def build_foreign_purchases(rng, external_suppliers):
    n = 800
    dates = _random_dates(n, rng)
    types = rng.choice(PURCHASE_TYPES, size=n, p=PURCHASE_TYPE_WEIGHTS)
    supplier_idx = rng.integers(0, len(external_suppliers), size=n)
    suppliers = np.array(external_suppliers)[supplier_idx]

    trnno = rng.integers(1, 40000, size=n)
    purtot = _round2(rng.gamma(shape=2.4, scale=2800.0, size=n) + 100.0)
    addcost = _round2(purtot * rng.uniform(0.04, 0.14, size=n))
    total = _round2(purtot + addcost)  # exact - no synthetic reconciliation noise introduced
    qty = rng.integers(1, 200, size=n)

    df = pd.DataFrame({
        "trnno": trnno, "date": dates, "type": types, "supplier": suppliers,
        "purtot": purtot, "addcost": addcost, "total": total, "qty": qty,
    })

    total_row = pd.DataFrame([{
        "trnno": np.nan, "date": pd.NaT, "type": np.nan, "supplier": np.nan,
        "purtot": df["purtot"].sum(), "addcost": df["addcost"].sum(),
        "total": df["total"].sum(), "qty": np.nan,
    }])
    return pd.concat([df, total_row], ignore_index=True)


# --------------------------------------------------------------------------
# LOCAL PURCHASE RETURNS (Cost Center dimension - public-safe city names)
# --------------------------------------------------------------------------
def build_local_purchase_returns(rng):
    n = 380
    dates = _random_dates(n, rng)
    cost_centers = rng.choice(COST_CENTERS, size=n)
    movement_no = np.arange(1, n + 1)
    types = rng.choice(PURCHASE_RETURN_TYPES, size=n, p=[0.65, 0.35])
    item_code = [f"ITM-{c:05d}" for c in rng.integers(1, 99999, size=n)]

    cost = _round2(rng.gamma(shape=1.6, scale=480.0, size=n) + 15.0)
    discount = _round2(cost * rng.uniform(0.0, 0.05, size=n))
    vat = _round2((cost - discount) * VAT_RATE)
    total = _round2((cost - discount) + vat)
    qty = rng.integers(1, 25, size=n)

    # Exactly one intentional "Missing-Inferred-Zero" discount example -
    # demonstrates an existing Data Quality feature (a missing discount
    # value independently corroborated as zero because Cost + VAT = Total
    # reconciles exactly) without fabricating an unrealistic error rate.
    discount = discount.astype(object)
    discount[0] = np.nan
    total[0] = _round2(cost[0] + vat[0])  # Cost + VAT = Total exactly -> safe to infer zero

    df = pd.DataFrame({
        "رقم المستودع": cost_centers,
        "رقم الحركة": movement_no,
        "التاريخ": dates,
        "نوع الحركة": types,
        "رقم الصنف": item_code,
        "الكمية": qty,
        "التكلفة": cost,
        "الخصم": discount,
        "الضريبة": vat,
        "الإجمالي": total,
    })

    total_row = pd.DataFrame([{
        "رقم المستودع": np.nan, "رقم الحركة": np.nan, "التاريخ": pd.NaT, "نوع الحركة": np.nan,
        "رقم الصنف": np.nan, "الكمية": np.nan,
        "التكلفة": pd.to_numeric(df["التكلفة"]).sum(),
        "الخصم": pd.to_numeric(df["الخصم"], errors="coerce").sum(),
        "الضريبة": pd.to_numeric(df["الضريبة"]).sum(),
        "الإجمالي": pd.to_numeric(df["الإجمالي"]).sum(),
    }])
    return pd.concat([df, total_row], ignore_index=True)


# --------------------------------------------------------------------------
# PROFIT - independently sampled, never derived from Sales/Purchases here
# or anywhere downstream. Clearly different scale from the confidential
# internal figures.
# --------------------------------------------------------------------------
def build_profit(rng):
    base = rng.uniform(2_800_000, 3_400_000)
    factors = {2022: 1.00, 2023: 1.19, 2024: 1.31, 2025: 1.05}  # independent
    # synthetic trajectory - not fit to Sales/Purchases in any way.
    rows = []
    for y in YEARS:
        noise = rng.uniform(0.97, 1.03)
        rows.append({"السنه": y, "الارباح": round(base * factors[y] * noise, 2)})
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------
# SUPPLIER DEBT / SUPPLIER CREDITORS - static synthetic snapshots
# --------------------------------------------------------------------------
def build_supplier_balances(rng, supplier_pool, is_creditor: bool):
    n = 13 if not is_creditor else 12
    names = rng.choice(supplier_pool, size=n, replace=False)
    currencies = rng.choice(["SAR", "USD", "EUR"], size=n, p=[0.55, 0.30, 0.15])
    fx_rate = {"SAR": 1.0, "USD": 3.75, "EUR": 4.05}
    foreign_amount = _round2(rng.uniform(1000, 90000, size=n))
    local_amount = _round2(foreign_amount * np.array([fx_rate[c] for c in currencies]))
    if is_creditor:
        local_amount = -local_amount  # preserve the approved sign convention (creditors negative)
        foreign_amount = -foreign_amount

    df = pd.DataFrame({
        "اسم المورد": names, "العملة": currencies,
        "العملة الأجنبية": foreign_amount, "العملة المحلية": local_amount,
    })
    total_row = pd.DataFrame([{
        "اسم المورد": config.SUPPLIER_BALANCE_TOTAL_ROW_MARKER, "العملة": np.nan,
        "العملة الأجنبية": df["العملة الأجنبية"].sum(), "العملة المحلية": df["العملة المحلية"].sum(),
    }])
    return pd.concat([df, total_row], ignore_index=True)


def main():
    rng = _rng()
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    n_customers = 220
    customer_names = _make_names(CUSTOMER_PREFIXES, CUSTOMER_CORES, CUSTOMER_SUFFIXES, n_customers, rng)
    customer_no = np.arange(100001, 100001 + n_customers)
    # Mild power-law-ish concentration so a handful of customers are
    # visibly "top customers" without any single one being unrealistic.
    raw_weight = rng.pareto(a=2.2, size=n_customers) + 0.15
    weight = raw_weight / raw_weight.sum()
    vat_ids = [_synthetic_vat_id(rng) for _ in range(n_customers)]
    customers_df = pd.DataFrame({
        "customer_no": customer_no, "customer_name": customer_names,
        "vat_id": vat_ids, "_weight": weight,
    })

    n_internal = 30
    internal_suppliers = _make_names(["شركة", "مؤسسة"], INTERNAL_SUPPLIER_CORES,
                                      INTERNAL_SUPPLIER_SUFFIXES, n_internal - 1, rng)
    internal_suppliers.append(config.GENERIC_SUPPLIER_NAME)  # "عام" - existing feature, see build_local_purchases

    n_external = 16
    external_suppliers = _make_external_names(EXTERNAL_SUPPLIER_CORES, n_external, rng)

    # Structural audit requirement carried over from the internal project:
    # Internal and External supplier namespaces must stay 100% disjoint.
    assert set(internal_suppliers).isdisjoint(set(external_suppliers)), \
        "Internal/External supplier lists must never overlap"

    sales_with_total, sales_real = build_sales(rng, customers_df)
    sales_returns = build_sales_returns(rng, sales_real)
    local_purchases = build_local_purchases(rng, internal_suppliers)
    foreign_purchases = build_foreign_purchases(rng, external_suppliers)
    local_purchase_returns = build_local_purchase_returns(rng)
    profit = build_profit(rng)
    supplier_debt = build_supplier_balances(rng, np.array(internal_suppliers), is_creditor=False)
    supplier_creditors = build_supplier_balances(rng, np.array(internal_suppliers), is_creditor=True)

    sheets = {
        config.SHEET_SALES: sales_with_total,
        config.SHEET_PROFIT: profit,
        config.SHEET_SALES_RETURNS: sales_returns,
        config.SHEET_FOREIGN_PURCHASES: foreign_purchases,
        config.SHEET_LOCAL_PURCHASES: local_purchases,
        config.SHEET_LOCAL_PURCHASE_RETURNS: local_purchase_returns,
        config.SHEET_SUPPLIER_DEBT: supplier_debt,
        config.SHEET_SUPPLIER_CREDITORS: supplier_creditors,
    }

    with pd.ExcelWriter(OUT_PATH, engine="openpyxl") as writer:
        for sheet_name, df in sheets.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)

    print(f"Wrote {OUT_PATH}")
    for name, df in sheets.items():
        print(f"  {name}: {len(df)} rows")
    print(f"\nInternal suppliers ({len(internal_suppliers)}): includes generic 'عام' bucket")
    print(f"External suppliers ({len(external_suppliers)})")
    print(f"Customers ({n_customers}) + generic '{config.GENERIC_CASH_CUSTOMER_NAME}' cash bucket")


if __name__ == "__main__":
    main()
