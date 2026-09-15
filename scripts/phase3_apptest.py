# -*- coding: utf-8 -*-
"""
Real end-to-end QA using Streamlit's official AppTest harness: actually runs
app.py inside a simulated session (unlike a plain python import), catches any
runtime exception via at.exception, and simulates the language toggle + every
sidebar navigation click, using the real widget keys assigned in app.py.
"""
import sys
import io
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from streamlit.testing.v1 import AppTest

NAV_KEYS = [
    "nav_executive_overview", "nav_sales_performance", "nav_purchasing_performance",
    "nav_returns_analysis", "nav_vat_analysis", "nav_customers_suppliers",
    "nav_yoy_analysis", "nav_supplier_balances", "nav_data_quality",
]


def report_exceptions(at, label):
    if at.exception:
        print(f"[FAIL] {label}: {len(at.exception)} exception(s)")
        for exc in at.exception:
            print(f"   -> {exc.value!r}")
        return False
    print(f"[OK]   {label}  (no exceptions)")
    return True


def main():
    ok = True

    at = AppTest.from_file(str(PROJECT_ROOT / "app.py"), default_timeout=60)
    at.run()
    ok &= report_exceptions(at, "Initial load (English, Executive Overview)")

    # Click through every nav page (English) using the real button keys
    for nav_key in NAV_KEYS:
        try:
            at.sidebar.button(key=f"nav_btn_{nav_key}").click().run()
            ok &= report_exceptions(at, f"Nav -> {nav_key} (English)")
        except Exception as e:
            ok = False
            print(f"[FAIL] Nav -> {nav_key} (English): harness error {e!r}")

    # Switch to Arabic via the segmented control
    try:
        at.sidebar.segmented_control(key="lang_seg").set_value("العربية").run()
        ok &= report_exceptions(at, "Language switch -> Arabic")
    except Exception as e:
        ok = False
        print(f"[FAIL] Language switch -> Arabic: harness error {e!r}")

    # Click through every nav page again in Arabic
    for nav_key in NAV_KEYS:
        try:
            at.sidebar.button(key=f"nav_btn_{nav_key}").click().run()
            ok &= report_exceptions(at, f"Nav -> {nav_key} (Arabic)")
        except Exception as e:
            ok = False
            print(f"[FAIL] Nav -> {nav_key} (Arabic): harness error {e!r}")

    # Switch back to English and confirm it round-trips cleanly
    try:
        at.sidebar.segmented_control(key="lang_seg").set_value("English").run()
        ok &= report_exceptions(at, "Language switch -> English (round trip)")
    except Exception as e:
        ok = False
        print(f"[FAIL] Language switch -> English: harness error {e!r}")

    print("\nALL APPTEST CHECKS PASSED" if ok else "\nSOME APPTEST CHECKS FAILED")
    return ok


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
