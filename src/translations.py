# -*- coding: utf-8 -*-
"""
Single source of truth for every user-visible string in the project.
Phase 3 (Streamlit UI) must pull ALL labels from here via t(key, lang) -
no hardcoded Arabic or English strings are allowed in UI code.

One analytical layer (src/financial_metrics.py, src/data_cleaning.py) +
one localization layer (this file) = no duplicated logic between languages.
"""

LANGUAGES = ("en", "ar")

TRANSLATIONS = {
    # ---- App / navigation ----
    "app_title": {"en": "Executive Financial & Accounting Performance Dashboard",
                  "ar": "لوحة الأداء المالي والمحاسبي التنفيذية"},
    "lang_toggle_label": {"en": "العربية | English", "ar": "العربية | English"},
    "nav_executive_overview": {"en": "Executive Overview", "ar": "الملخص التنفيذي"},
    "nav_sales_performance": {"en": "Sales Performance", "ar": "أداء المبيعات"},
    "nav_purchasing_performance": {"en": "Purchasing Performance", "ar": "أداء المشتريات"},
    "nav_returns_analysis": {"en": "Returns Analysis", "ar": "تحليل المرتجعات"},
    "nav_vat_analysis": {"en": "VAT Analysis", "ar": "تحليل ضريبة القيمة المضافة"},
    "nav_customers_suppliers": {"en": "Customers & Suppliers", "ar": "العملاء والموردون"},
    "nav_yoy_analysis": {"en": "Year-over-Year Analysis", "ar": "المقارنة السنوية"},
    "nav_data_quality": {"en": "Data Quality & Reconciliation", "ar": "جودة البيانات والمطابقة"},
    "nav_supplier_balances": {"en": "Supplier Balances", "ar": "أرصدة الموردين"},

    # ---- Filters ----
    "filter_year": {"en": "Year", "ar": "السنة"},
    "filter_quarter": {"en": "Quarter", "ar": "الربع"},
    "filter_month": {"en": "Month", "ar": "الشهر"},
    "filter_date_range": {"en": "Date Range", "ar": "الفترة الزمنية"},
    "filter_transaction_type": {"en": "Transaction Type", "ar": "نوع الحركة"},
    "filter_customer": {"en": "Customer", "ar": "العميل"},
    "filter_supplier": {"en": "Supplier", "ar": "المورد"},
    "filter_supplier_internal": {"en": "Internal Supplier", "ar": "المورد الداخلي"},
    "filter_supplier_external": {"en": "External Supplier", "ar": "المورد الخارجي"},
    "filter_cost_center": {"en": "Cost Center", "ar": "مركز التكلفة"},
    "filter_all": {"en": "All", "ar": "الكل"},
    "filter_placeholder": {"en": "Choose options", "ar": "اختر"},

    # ---- Core financial KPIs ----
    "gross_sales_before_vat": {"en": "Gross Sales (before VAT)", "ar": "إجمالي المبيعات (بدون الضريبة)"},
    "sales_returns_before_vat": {"en": "Sales Returns (before VAT)", "ar": "مردود المبيعات (بدون الضريبة)"},
    "net_sales_before_vat": {"en": "Net Sales (before VAT)", "ar": "صافي المبيعات (بدون الضريبة)"},
    "gross_sales_incl_vat": {"en": "Gross Sales Including VAT (before Returns)",
                              "ar": "إجمالي المبيعات شامل الضريبة قبل المرتجعات"},
    "net_sales_incl_vat": {"en": "Net Sales Including VAT", "ar": "صافي المبيعات شامل الضريبة"},
    "sales_return_rate_pct": {"en": "Sales Return Rate", "ar": "نسبة مردود المبيعات"},
    "sales_transaction_count": {"en": "Sales Transaction Count", "ar": "عدد حركات المبيعات"},
    "avg_sales_transaction_value": {"en": "Average Sales Transaction Value", "ar": "متوسط قيمة حركة المبيعات"},

    "purchase_transaction_count": {"en": "Purchase Transaction Count", "ar": "عدد حركات المشتريات"},

    "gross_output_vat": {"en": "Gross Output VAT", "ar": "إجمالي ضريبة المخرجات"},
    "sales_return_vat": {"en": "Sales Return VAT", "ar": "ضريبة مردود المبيعات"},
    "net_output_vat": {"en": "Net Output VAT", "ar": "صافي ضريبة المخرجات"},

    # ---- Local / Foreign Purchases (management request: kept separate) ----
    "local_purchases_before_vat": {"en": "Domestic Purchases (before VAT)", "ar": "المشتريات الداخلية (قبل الضريبة)"},
    "local_purchase_vat": {"en": "Domestic Purchase VAT", "ar": "ضريبة المشتريات الداخلية"},
    "local_purchases_incl_vat": {"en": "Domestic Purchases (incl. VAT)", "ar": "المشتريات الداخلية (شامل الضريبة)"},
    "local_purchase_transaction_count": {"en": "Domestic Purchase Transaction Count", "ar": "عدد حركات المشتريات الداخلية"},
    "foreign_purchase_base": {"en": "Foreign Purchase Base", "ar": "أساس المشتريات الخارجية"},
    "foreign_purchase_additional_cost": {"en": "Additional Foreign Purchase Cost",
                                          "ar": "التكلفة الإضافية للمشتريات الخارجية"},
    "foreign_purchase_total": {"en": "Foreign Purchase Total", "ar": "إجمالي المشتريات الخارجية"},
    "foreign_purchase_transaction_count": {"en": "Foreign Purchase Transaction Count",
                                            "ar": "عدد حركات المشتريات الخارجية"},
    "total_purchases_before_vat": {"en": "Total Purchases", "ar": "إجمالي المشتريات"},
    "local_purchase_returns_before_vat": {"en": "Domestic Purchase Returns (before VAT)",
                                           "ar": "مردود المشتريات الداخلية (قبل الضريبة)"},
    "local_purchase_returns_vat": {"en": "Domestic Purchase Return VAT", "ar": "ضريبة مردود المشتريات الداخلية"},
    "cost_center": {"en": "Cost Center", "ar": "مركز التكلفة"},

    "cash_sales": {"en": "Cash Sales", "ar": "المبيعات النقدية"},
    "credit_sales": {"en": "Credit Sales", "ar": "المبيعات الآجلة"},
    "service_sales": {"en": "Service Sales", "ar": "مبيعات الخدمات"},
    "cash_purchases": {"en": "Cash Purchases", "ar": "المشتريات النقدية"},
    "credit_purchases": {"en": "Credit Purchases", "ar": "المشتريات الآجلة"},
    "lc_purchases": {"en": "Letter of Credit Purchases", "ar": "مشتريات الاعتماد"},

    # ---- Customers / Suppliers ----
    "top_customers": {"en": "Top Customers", "ar": "أفضل العملاء"},
    "top_suppliers": {"en": "Top Suppliers", "ar": "أفضل الموردين"},
    "customer_concentration": {"en": "Customer Concentration", "ar": "تركز العملاء"},
    "supplier_concentration": {"en": "Supplier Concentration", "ar": "تركز الموردين"},
    "top5_share": {"en": "Top 5 Share", "ar": "نسبة أفضل 5"},
    "top10_share": {"en": "Top 10 Share", "ar": "نسبة أفضل 10"},
    "cash_walkin_customers": {"en": "Cash / Walk-in Sales", "ar": "المبيعات النقدية / العملاء النقديون"},
    "cash_walkin_note": {
        "en": "'نقدي' is a generic point-of-sale cash/walk-in customer code, not one real customer entity, "
              "and is analyzed separately from named-customer concentration.",
        "ar": "'نقدي' هو رمز عام لعملاء البيع النقدي في نقاط البيع وليس عميلاً حقيقياً واحداً، "
              "ويتم تحليله بشكل منفصل عن تحليل تركز العملاء المسمّين."
    },

    # ---- Year-over-Year ----
    "yoy": {"en": "Year-over-Year", "ar": "المقارنة السنوية"},
    "yoy_vs_label": {"en": "vs", "ar": "مقابل"},
    "current_year": {"en": "Current Year", "ar": "السنة الحالية"},
    "previous_year": {"en": "Previous Year", "ar": "السنة السابقة"},
    "absolute_variance": {"en": "Absolute Variance", "ar": "الفرق المطلق"},
    "pct_variance": {"en": "% Change", "ar": "نسبة التغير"},

    # ---- Data quality / reconciliation ----
    "data_quality": {"en": "Data Quality", "ar": "جودة البيانات"},
    "reconciliation": {"en": "Reconciliation", "ar": "المطابقة"},
    "status_valid": {"en": "Valid", "ar": "سليم"},
    "status_reconciliation_review": {"en": "Reconciliation Review", "ar": "يتطلب مراجعة مطابقة"},
    "status_corrupt_excluded": {"en": "Corrupt - Excluded from VAT", "ar": "تالف - مستبعد من حساب الضريبة"},
    "status_missing": {"en": "Missing", "ar": "غير متوفر"},
    "total_source_records": {"en": "Total Source Records", "ar": "إجمالي السجلات المصدرية"},
    "analytical_records": {"en": "Analytical Records", "ar": "السجلات التحليلية"},
    "excluded_from_analytical_totals": {"en": "Excluded from Analytical Totals", "ar": "مستبعد من الإجماليات التحليلية"},

    "sales_returns_total_row_note": {
        "en": "One embedded grand-total row ('اجمالى التقرير') was found in the Sales Returns sheet and "
              "excluded from all calculations - its value exactly matched the sum of all real return rows.",
        "ar": "تم العثور على صف إجمالي مضمّن ('اجمالى التقرير') في صفحة مردود المبيعات وتم استبعاده من جميع "
              "الحسابات - حيث تطابقت قيمته تماماً مع مجموع كل صفوف المرتجعات الفعلية."
    },
    "purchase_tax_corrupt_note": {
        "en": "130 Purchase transactions contain an invalid tax value in the source data. These transactions "
              "remain fully included in Purchase Activity and Net Purchases; only their tax amount is excluded "
              "from Input VAT calculations.",
        "ar": "تحتوي 130 حركة شراء على قيمة ضريبة غير صحيحة في البيانات المصدرية. تبقى هذه الحركات مشمولة "
              "بالكامل ضمن النشاط الشرائي وصافي المشتريات، ويُستبعد فقط مبلغ الضريبة الخاص بها من حساب ضريبة المدخلات."
    },
    "sales_return_link_note": {
        "en": "Linkage between a Sales Return and its original sale is best-effort/illustrative only, based on "
              "matching transaction number and date. It is never used to aggregate monetary totals.",
        "ar": "يُعد الربط بين مردود المبيعات والفاتورة الأصلية اجتهاداً استرشادياً فقط، بناءً على تطابق رقم "
              "الحركة والتاريخ، ولا يُستخدم إطلاقاً في تجميع القيم المالية."
    },
    "purchase_return_no_supplier_note": {
        "en": "Purchase return data does not contain sufficient supplier linkage for supplier-level return "
              "attribution.",
        "ar": "بيانات مردود المشتريات لا تحتوي على معلومات ربط كافية لتوزيع المرتجعات على مستوى المورد."
    },
    "purchase_return_no_invoice_link_note": {
        "en": "Purchase returns cannot be reliably linked to a specific original purchase transaction in this "
              "data; any numeric overlap between reference numbers was tested and found to be coincidental.",
        "ar": "لا يمكن ربط مردودات المشتريات بشكل موثوق بحركة شراء أصلية محددة في هذه البيانات؛ تم اختبار أي "
              "تطابق رقمي بين أرقام المرجع وتبيّن أنه توافق عرضي غير حقيقي."
    },
    "transaction_count_terminology_note": {
        "en": "Transaction numbers in this workbook are recycled and are not unique invoice identifiers. "
              "'Transaction Count' therefore reflects the number of recorded transaction rows, not a count of "
              "uniquely numbered invoices.",
        "ar": "أرقام الحركات في هذا الملف يُعاد استخدامها ولا تمثل أرقام فواتير فريدة. لذلك يعكس 'عدد الحركات' "
              "عدد صفوف الحركات المسجلة، وليس عدد فواتير بأرقام فريدة."
    },

    # ---- Mandatory disclaimers ----
    "vat_disclaimer": {
        "en": "VAT figures shown in this dashboard are analytical indicators based on the available transaction "
              "data and should be reconciled against official accounting and tax records before filing.",
        "ar": "أرقام ضريبة القيمة المضافة المعروضة في هذا التقرير هي مؤشرات تحليلية مبنية على بيانات الحركات "
              "المتاحة ويجب مطابقتها مع السجلات المحاسبية والضريبية الرسمية قبل تقديم الإقرار."
    },
    "profit_limitation_disclaimer": {
        "en": "This dashboard analyzes sales, purchases, returns and VAT-related activity. It should not be "
              "interpreted as a complete Income Statement or as a calculation of accounting Net Profit unless "
              "all required inventory, cost and operating expense data is available.",
        "ar": "يقوم هذا التقرير بتحليل المبيعات والمشتريات والمرتجعات والحركات المتعلقة بضريبة القيمة المضافة، "
              "ولا يجب اعتباره قائمة دخل متكاملة أو حساباً لصافي الربح المحاسبي ما لم تتوفر جميع بيانات المخزون "
              "والتكلفة والمصروفات التشغيلية اللازمة."
    },
    # ---- Currency ----
    "currency_code": {"en": "SAR", "ar": "ريال سعودي"},

    # ---- Public portfolio-demo disclosure (unobtrusive, sidebar-only) ----
    "portfolio_disclaimer": {
        "en": "Portfolio Demo — All data shown is fully synthetic and does not represent actual company records.",
        "ar": "نسخة Portfolio تجريبية — جميع البيانات المعروضة اصطناعية بالكامل ولا تمثل سجلات فعلية للشركة.",
    },

    # ---- Executive insight templates (str.format placeholders) ----
    "insight_best_sales_year": {
        "en": "{year} was the strongest year for Net Sales at SAR {value}.",
        "ar": "كان عام {year} الأقوى من حيث صافي المبيعات بقيمة {value} ريال سعودي."
    },
    "insight_weakest_sales_year": {
        "en": "{year} was the weakest year for Net Sales at SAR {value}.",
        "ar": "كان عام {year} الأضعف من حيث صافي المبيعات بقيمة {value} ريال سعودي."
    },
    "insight_highest_yoy_sales_growth": {
        "en": "The strongest Net Sales growth was {comparison}, up {pct}% (SAR {value}).",
        "ar": "كان أقوى نمو في صافي المبيعات خلال {comparison}، بارتفاع {pct}% ({value} ريال سعودي)."
    },
    "insight_largest_sales_decline": {
        "en": "The largest Net Sales decline was {comparison}, down {pct}% (SAR {value}).",
        "ar": "كان أكبر انخفاض في صافي المبيعات خلال {comparison}، بانخفاض {pct}% ({value} ريال سعودي)."
    },
    "insight_highest_return_rate_year": {
        "en": "{year} had the highest Sales Return Rate at {pct}%.",
        "ar": "سجل عام {year} أعلى نسبة مردود مبيعات بلغت {pct}%."
    },
    "insight_lowest_return_rate_year": {
        "en": "{year} had the lowest Sales Return Rate at {pct}%.",
        "ar": "سجل عام {year} أدنى نسبة مردود مبيعات بلغت {pct}%."
    },
    "insight_highest_purchasing_year": {
        "en": "{year} recorded the highest Purchase Activity at SAR {value}.",
        "ar": "سجل عام {year} أعلى نشاط شرائي بقيمة {value} ريال سعودي."
    },
    "insight_customer_concentration": {
        "en": "The top 5 identifiable customers represent {pct}% of named-customer Net Sales.",
        "ar": "يمثل أفضل 5 عملاء محددين {pct}% من صافي مبيعات العملاء المسمّين."
    },
    "insight_supplier_concentration": {
        "en": "The top 5 suppliers represent {pct}% of total Purchase Activity.",
        "ar": "يمثل أفضل 5 موردين {pct}% من إجمالي النشاط الشرائي."
    },
    "insight_vat_position_latest_year": {
        "en": "In {year}, the Indicative VAT Position was SAR {value} ({direction}).",
        "ar": "في عام {year}، بلغ الموقف التقديري لضريبة القيمة المضافة {value} ريال سعودي ({direction})."
    },
    "insight_direction_payable": {"en": "net payable position", "ar": "موقف مدين صافي"},
    "insight_direction_receivable": {"en": "net receivable position", "ar": "موقف دائن صافي"},
    "insight_profit_latest_year": {
        "en": "{year} Profit (approved source) was SAR {value}.",
        "ar": "بلغ الربح المعتمد لعام {year} {value} ريال سعودي."
    },
    "insight_four_year_direction_up": {
        "en": "Net Sales grew {pct}% from 2022 to 2025 (SAR {value_2022} -> SAR {value_2025}).",
        "ar": "نما صافي المبيعات بنسبة {pct}% من عام 2022 إلى 2025 ({value_2022} -> {value_2025} ريال سعودي)."
    },
    "insight_four_year_direction_down": {
        "en": "Net Sales declined {pct}% from 2022 to 2025 (SAR {value_2022} -> SAR {value_2025}).",
        "ar": "انخفض صافي المبيعات بنسبة {pct}% من عام 2022 إلى 2025 ({value_2022} -> {value_2025} ريال سعودي)."
    },
    "insight_cash_walkin_dominance": {
        "en": "Generic cash/walk-in sales ('نقدي') represent {pct}% of total Net Sales value and are excluded "
              "from named-customer concentration analysis.",
        "ar": "تمثل المبيعات النقدية العامة ('نقدي') {pct}% من إجمالي قيمة صافي المبيعات، ويتم استبعادها من "
              "تحليل تركز العملاء المسمّين."
    },
    "insight_purchase_tax_corruption": {
        "en": "{count} purchase transactions ({pct}% of all purchases) had an invalid source tax value and were "
              "excluded from Input VAT only; they remain in Net Purchases.",
        "ar": "احتوت {count} حركة شراء ({pct}% من إجمالي المشتريات) على قيمة ضريبة مصدرية غير صحيحة تم "
              "استبعادها من ضريبة المدخلات فقط، وتبقى مشمولة ضمن صافي المشتريات."
    },

    # ---- Chart titles / section headers ----
    "annual_performance_comparison": {"en": "Annual Comparison (2022–2025)",
                                       "ar": 'المقارنة السنوية (<bdi dir="ltr">2022–2025</bdi>)'},
    "monthly_net_sales_trend": {"en": "Monthly Net Sales Trend", "ar": "الاتجاه الشهري لصافي المبيعات"},
    "net_sales_vs_net_purchases_trend": {"en": "Net Sales vs Total Purchases Trend",
                                          "ar": "اتجاه صافي المبيعات مقابل إجمالي المشتريات"},
    "sales_return_rate_trend": {"en": "Sales Return Rate Trend", "ar": "اتجاه نسبة مردود المبيعات"},
    "vat_movement": {"en": "VAT Movement", "ar": "حركة ضريبة القيمة المضافة"},
    "executive_insights": {"en": "Executive Insights", "ar": "الرؤى التنفيذية"},
    "key_risks_attention": {"en": "Key Management Risks / Attention Areas",
                             "ar": "المخاطر الإدارية الرئيسية / مجالات تتطلب الانتباه"},
    "gross_sales_vs_returns": {"en": "Gross Sales vs Sales Returns", "ar": "إجمالي المبيعات مقابل مردود المبيعات"},
    "sales_by_transaction_type": {"en": "Sales by Transaction Type", "ar": "المبيعات حسب نوع الحركة"},
    "sales_quantity_trend": {"en": "Sales Quantity Trend", "ar": "اتجاه كمية المبيعات"},
    "monthly_purchase_trend": {"en": "Monthly Purchase Trend", "ar": "الاتجاه الشهري للمشتريات"},
    "annual_purchase_trend": {"en": "Annual Purchase Trend", "ar": "الاتجاه السنوي للمشتريات"},
    "purchases_vs_purchase_returns": {"en": "Purchases vs Purchase Returns", "ar": "المشتريات مقابل مردود المشتريات"},
    "purchases_by_transaction_type": {"en": "Purchases by Transaction Type", "ar": "المشتريات حسب نوع الحركة"},
    "supplier_contribution": {"en": "Supplier Contribution", "ar": "مساهمة الموردين"},
    "top_suppliers_chart": {"en": "Top Suppliers by Purchase Value", "ar": "أفضل الموردين حسب قيمة المشتريات"},
    "local_vs_foreign_by_year": {"en": "Domestic vs Foreign Purchases by Year",
                                  "ar": "المشتريات الداخلية مقابل الخارجية حسب السنة"},
    "local_vs_foreign_by_month": {"en": "Domestic vs Foreign Purchases by Month",
                                   "ar": "المشتريات الداخلية مقابل الخارجية حسب الشهر"},
    "local_purchases_by_type": {"en": "Domestic Purchases by Transaction Type", "ar": "المشتريات الداخلية حسب نوع الحركة"},
    "foreign_purchases_by_supplier": {"en": "Foreign Purchases by Supplier", "ar": "المشتريات الخارجية حسب المورد"},
    "local_purchases_by_supplier": {"en": "Domestic Purchases by Supplier", "ar": "المشتريات الداخلية حسب المورد"},
    "local_purchase_returns_by_cost_center": {"en": "Domestic Purchase Returns by Cost Center",
                                               "ar": "مردود المشتريات الداخلية حسب مركز التكلفة"},
    "local_supplier_concentration": {"en": "Domestic Supplier Concentration", "ar": "تركز موردي المشتريات الداخلية"},
    "foreign_supplier_concentration": {"en": "Foreign Supplier Concentration", "ar": "تركز موردي المشتريات الخارجية"},
    "monthly_sales_4yr_comparison": {"en": "Monthly Net Sales - 4-Year Comparison",
                                      "ar": "صافي المبيعات الشهري - مقارنة 4 سنوات"},
    "sales_returns_section_title": {"en": "Sales Returns", "ar": "مردود المبيعات"},
    "purchase_returns_section_title": {"en": "Domestic Purchase Returns", "ar": "مردود المشتريات الداخلية"},
    "monthly_trend_sales_returns": {"en": "Sales Returns - Monthly Trend", "ar": "مردود المبيعات - الاتجاه الشهري"},
    "annual_trend_sales_returns": {"en": "Sales Returns - Annual Trend", "ar": "مردود المبيعات - الاتجاه السنوي"},
    "customers_highest_returns": {"en": "Customers with Highest Returns", "ar": "العملاء الأعلى في المرتجعات"},
    "customer_return_rate": {"en": "Customer Return Rate", "ar": "نسبة مردود العميل"},
    "original_sale_match_status": {"en": "Original Sale Match Status (illustrative only)",
                                    "ar": "حالة مطابقة الفاتورة الأصلية (استرشادي فقط)"},
    "match_status_disclaimer": {
        "en": "This match status is a Data Quality / illustrative indicator only. It is never used in any "
              "financial calculation shown in this dashboard.",
        "ar": "حالة المطابقة هذه مؤشر استرشادي لجودة البيانات فقط، ولا تُستخدم إطلاقاً في أي حساب مالي "
              "معروض في هذا التقرير."
    },
    "monthly_trend_purchase_returns": {"en": "Purchase Returns - Monthly Trend", "ar": "مردود المشتريات - الاتجاه الشهري"},
    "annual_trend_purchase_returns": {"en": "Purchase Returns - Annual Trend", "ar": "مردود المشتريات - الاتجاه السنوي"},
    "purchase_returns_by_warehouse": {"en": "Purchase Returns by Warehouse", "ar": "مردود المشتريات حسب المستودع"},
    "purchase_returns_by_type": {"en": "Purchase Returns by Transaction Type", "ar": "مردود المشتريات حسب نوع الحركة"},
    "vat_annual_comparison": {"en": "VAT - Annual Comparison", "ar": "ضريبة القيمة المضافة - المقارنة السنوية"},
    "vat_monthly_trend": {"en": "VAT - Monthly Trend", "ar": "ضريبة القيمة المضافة - الاتجاه الشهري"},
    "output_vs_input_vat": {"en": "Output VAT vs Input VAT", "ar": "ضريبة المخرجات مقابل ضريبة المدخلات"},
    "top_customers_net_sales": {"en": "Top Customers by Net Sales", "ar": "أفضل العملاء حسب صافي المبيعات"},
    "top_customers_gross_sales": {"en": "Top Customers by Gross Sales", "ar": "أفضل العملاء حسب إجمالي المبيعات"},
    "top_customers_returns": {"en": "Top Customers by Sales Returns", "ar": "أفضل العملاء حسب مردود المبيعات"},
    "customer_contribution": {"en": "Customer Contribution", "ar": "مساهمة العميل"},
    "supplier_purchase_trend": {"en": "Supplier Purchase Trend", "ar": "اتجاه مشتريات المورد"},
    "yoy_comparison_table": {"en": "Year-over-Year Comparison", "ar": "مقارنة سنة بعد أخرى"},
    "data_quality_scorecard": {"en": "Data Quality Scorecard", "ar": "بطاقة جودة البيانات"},
    "reconciliation_summary": {"en": "Reconciliation Summary", "ar": "ملخص المطابقة"},
    "total_records": {"en": "Total Records", "ar": "إجمالي السجلات"},
    "valid_records": {"en": "Valid Records", "ar": "سجلات سليمة"},
    "warning_records": {"en": "Warning Records", "ar": "سجلات تحذيرية"},
    "analytical_exclusions": {"en": "Analytical Exclusions", "ar": "استبعادات تحليلية"},
    "corrupt_vat_records": {"en": "Corrupt VAT Records (Purchases)", "ar": "سجلات ضريبة تالفة (المشتريات)"},
    "reconciliation_review_records": {"en": "Reconciliation Review Records", "ar": "سجلات تتطلب مراجعة مطابقة"},
    "reconciliation_success_rate": {"en": "Reconciliation Success Rate", "ar": "معدل نجاح المطابقة"},
    "sales_sheet": {"en": "Sales", "ar": "المبيعات"},
    "sales_returns_sheet": {"en": "Sales Returns", "ar": "مردود المبيعات"},
    "purchases_sheet": {"en": "Purchases", "ar": "المشتريات"},
    "purchase_returns_sheet": {"en": "Purchase Returns", "ar": "مردود المشتريات"},
    "warehouse": {"en": "Warehouse", "ar": "المستودع"},
    "item_code": {"en": "Item Code", "ar": "رقم الصنف"},
    "quantity": {"en": "Quantity", "ar": "الكمية"},
    "sales_returns_quantity_label": {"en": "Sales Returns Quantity", "ar": "كمية مردود المبيعات"},
    "purchase_returns_quantity_label": {"en": "Domestic Purchase Returns Quantity", "ar": "كمية مردود المشتريات الداخلية"},
    "cash_return": {"en": "Cash Return", "ar": "مردود نقدي"},
    "credit_return": {"en": "Credit Return", "ar": "مردود آجل"},
    "additional_cost": {"en": "Additional Purchase Cost", "ar": "تكلفة إضافية على المشتريات"},
    "supplier_count": {"en": "Supplier Count", "ar": "عدد الموردين"},
    "match_matched": {"en": "Best-Effort-Matched", "ar": "مطابقة استرشادية"},
    "match_unmatched": {"en": "Unmatched", "ar": "غير مطابقة"},
    "match_ambiguous": {"en": "Ambiguous", "ar": "غير محددة"},
    "selected_period": {"en": "Selected Period", "ar": "الفترة المحددة"},
    "not_available_supplier_scope": {"en": "Not available", "ar": "غير متاح"},
    "supplier_scope_limitation_note": {
        "en": "Not available when a Supplier filter is active: Purchase Returns cannot be attributed to an "
              "individual supplier in the source data, so netting them against a single supplier's purchase "
              "value would be misleading. Clear the Supplier filter to see this figure.",
        "ar": "غير متاح عند تفعيل عامل تصفية المورد: لا يمكن نسب مردود المشتريات إلى مورد محدد في البيانات "
              "المصدرية، لذا فإن خصمه من قيمة مشتريات مورد واحد قد يكون مضللاً. أزل عامل تصفية المورد لعرض "
              "هذه القيمة.",
    },
    "vat_tax_valid_note": {
        "en": "Purchase transactions whose recorded tax value passed validation and are included in Validated "
              "Purchase VAT.",
        "ar": "حركات المشتريات التي اجتازت قيمة الضريبة المسجلة لها اختبار التحقق وتم إدراجها ضمن ضريبة "
              "المشتريات المعتمدة.",
    },
    "yoy_global_scope_note": {
        "en": "Year-over-Year comparisons always use the full 2022-2025 dataset so that every year has its "
              "required prior-year comparison figure. The Year, Quarter, Customer and Supplier filters in the "
              "sidebar do not apply to this page.",
        "ar": "تعتمد مقارنات سنة بعد أخرى دائماً على كامل بيانات الفترة 2022–2025 حتى تتوفر لكل سنة قيمة "
              "المقارنة اللازمة من السنة السابقة. لا تنطبق عوامل تصفية السنة أو الربع أو العميل أو المورد في "
              "الشريط الجانبي على هذه الصفحة.",
    },
    "discount_reported_label": {"en": "Complete Discount Records", "ar": "سجلات الخصم المكتملة"},
    "discount_missing_inferred_zero_label": {"en": "Missing Discount (Inferred Zero)", "ar": "خصم مفقود تم استنتاجه بصفر"},
    "purchase_return_discount_missing_note": {
        "en": "One record has a missing Discount value in the source. A zero discount was accepted after "
              "validating that Cost + VAT = Total exactly. The record is therefore included in Purchase "
              "Returns, while remaining flagged as a Data Quality warning because the original Discount value "
              "was missing.",
        "ar": "يوجد سجل واحد كانت فيه قيمة الخصم مفقودة في المصدر. تم اعتماد الخصم بقيمة صفر بعد التحقق من أن "
              "التكلفة + ضريبة القيمة المضافة = الإجمالي بشكل مطابق. لذلك تم تضمين السجل ضمن مردود المشتريات، "
              "مع إبقائه كتنبيه لجودة البيانات لأن قيمة الخصم الأصلية كانت مفقودة.",
    },
    "data_quality_global_scope_note": {
        "en": "These counts describe the quality of the full approved source workbook and are intentionally "
              "NOT affected by the Year, Quarter, Customer or Supplier filters in the sidebar.",
        "ar": "تصف هذه الأرقام جودة كامل ملف البيانات المصدري المعتمد، وهي غير متأثرة عمداً بعوامل تصفية "
              "السنة أو الربع أو العميل أو المورد في الشريط الجانبي.",
    },
    "vat_tax_reconciliation_review_note": {
        "en": "Purchase transactions with a minor tax-value discrepancy flagged for review; still included in "
              "Validated Purchase VAT.",
        "ar": "حركات المشتريات التي بها فارق بسيط في قيمة الضريبة تم رصده للمراجعة، وتبقى مشمولة ضمن ضريبة "
              "المشتريات المعتمدة.",
    },
    "net_sales_definition": {
        "en": "Gross sales excluding VAT less sales returns excluding VAT.",
        "ar": "إجمالي المبيعات بدون ضريبة القيمة المضافة بعد خصم مردود المبيعات بدون الضريبة."
    },
    "net_purchases_definition": {
        "en": "Validated purchase activity (purchase base + additional cost) less company-wide purchase "
              "returns. This is NOT Cost of Goods Sold and does not reflect inventory consumption.",
        "ar": "النشاط الشرائي المعتمد (أساس الشراء + التكلفة الإضافية) بعد خصم مردود المشتريات على مستوى "
              "الشركة. هذا الرقم ليس تكلفة البضاعة المباعة ولا يعكس استهلاك المخزون."
    },
    "gap_definition": {
        "en": "Net Sales minus Net Purchases. Management activity comparison only - does not represent "
              "accounting gross profit or net profit.",
        "ar": "صافي المبيعات ناقص صافي المشتريات. مؤشر للمقارنة الإدارية فقط، ولا يمثل إجمالي الربح أو صافي "
              "الربح المحاسبي."
    },
    "sales_return_rate_definition": {
        "en": "Sales Returns (before VAT) divided by Gross Sales (before VAT).",
        "ar": "مردود المبيعات (بدون الضريبة) مقسوماً على إجمالي المبيعات (بدون الضريبة)."
    },
    "indicative_vat_position_definition": {
        "en": "Net Output VAT minus Net Input VAT. An analytical indicator only - not an official VAT filing.",
        "ar": "صافي ضريبة المخرجات ناقص صافي ضريبة المدخلات. مؤشر تحليلي فقط وليس إقراراً ضريبياً رسمياً."
    },
    "transaction_count_definition": {
        "en": "Count of recorded transaction rows. Transaction numbers in the source data are recycled and "
              "are not unique invoice identifiers.",
        "ar": "عدد صفوف الحركات المسجلة. أرقام الحركات في البيانات المصدرية يُعاد استخدامها ولا تمثل أرقام "
              "فواتير فريدة."
    },
    "no_data_for_filters": {
        "en": "No records match the current filter selection.",
        "ar": "لا توجد سجلات مطابقة لخيارات التصفية الحالية."
    },
    "nav_section_label": {"en": "Navigation", "ar": "التنقل"},
    "filters_section_label": {"en": "Filters", "ar": "عوامل التصفية"},
    "not_profit_badge": {"en": "Not Profit", "ar": "ليس ربحاً"},
    "management_attention": {"en": "Management Attention", "ar": "نقاط تستحق انتباه الإدارة"},
    "no_attention_items": {
        "en": "No items currently meet the risk threshold for this section.",
        "ar": "لا توجد بنود تستوفي حالياً معايير المخاطر لهذا القسم."
    },
    "attention_sales_decline": {
        "en": "Net Sales declined {pct}% in {comparison} - a sharp slowdown worth investigating.",
        "ar": "انخفض صافي المبيعات بنسبة {pct}% خلال {comparison} - تباطؤ حاد يستحق المراجعة."
    },
    "attention_return_rate_rising": {
        "en": "Sales Return Rate rose from {prev_pct}% to {cur_pct}% - returns are becoming more frequent.",
        "ar": "ارتفعت نسبة مردود المبيعات من {prev_pct}% إلى {cur_pct}% - المرتجعات في ازدياد."
    },

    # ---- Profit (approved source sheet only - never calculated in-dashboard) ----
    "profit": {"en": "Profit", "ar": "الربح"},
    "annual_profit": {"en": "Annual Profit", "ar": "الربح السنوي"},
    "profit_yoy_change": {"en": "Profit YoY Change", "ar": "تغير الربح السنوي"},
    "profit_not_available_quarterly": {"en": "Not available at quarterly grain", "ar": "غير متاح عند التصفية الربعية"},
    "profit_source_note": {
        "en": "The displayed Profit value is read directly from the approved Profit sheet in the source "
              "workbook. It is not calculated inside the dashboard from Sales or Purchases.",
        "ar": "قيمة الربح المعروضة مأخوذة مباشرة من شيت الأرباح المعتمد في ملف المصدر ولا يتم احتسابها داخل "
              "لوحة المعلومات من المبيعات أو المشتريات.",
    },
    "profit_single_year_label": {"en": "Profit ({year})", "ar": "الربح ({year})"},
    "profit_cumulative_label": {"en": "Cumulative Profit ({range})", "ar": "الربح التراكمي ({range})"},
    "profit_cumulative_note": {
        "en": "This is a CUMULATIVE sum of the approved Profit sheet's values for every selected year, not a "
              "single-year figure - shown explicitly labeled as cumulative so it is never mistaken for one "
              "year's Profit.",
        "ar": "هذا مجموع تراكمي لقيم شيت الأرباح المعتمد لكل السنوات المحددة، وليس رقم سنة واحدة - يُعرض بوضوح "
              "كمجموع تراكمي حتى لا يُفهم خطأً على أنه ربح سنة واحدة.",
    },

    # ---- Generic Local Purchases supplier bucket ----
    "generic_supplier_note": {
        "en": "'عام' is a generic/unspecified-supplier code used on {count:,} Domestic Purchase transactions, "
              "not one real identifiable supplier, and is excluded from Domestic Supplier concentration "
              "ranking (analogous to how 'نقدي' is excluded from customer concentration).",
        "ar": "'عام' هو رمز مورد عام/غير محدد استُخدم في {count:,} حركة من المشتريات الداخلية، وليس مورداً "
              "حقيقياً واحداً محدداً، ويُستبعد من ترتيب تركز الموردين الداخليين (بنفس منطق استبعاد 'نقدي' من "
              "تركز العملاء).",
    },

    # ---- Data Quality - clean executive-facing wording (no debug output) ----
    "coverage_complete": {"en": "Complete", "ar": "مكتملة"},
    "coverage_incomplete": {"en": "Incomplete", "ar": "غير مكتملة"},
    "annual_records_label": {"en": "annual records", "ar": "سجلات سنوية"},
    "available_years_label": {"en": "Available years", "ar": "السنوات المتاحة"},
    "coverage_label": {"en": "Coverage", "ar": "التغطية"},
    "matches_source_total": {"en": "matches source total", "ar": "مطابق لإجمالي المصدر"},
    "does_not_match_source_total": {"en": "does not match source total - review required",
                                     "ar": "لا يطابق إجمالي المصدر - يتطلب مراجعة"},
    "suppliers_label": {"en": "suppliers", "ar": "مورداً"},
    "customer_numeric_name_note": {
        "en": "{count} customer record(s) in the source data have a customer name that is itself just a plain "
              "number ({values}) - not a real business/person name, and not the generic 'نقدي' cash-customer "
              "code (which is handled separately). No alternate name field exists for these in the source, so "
              "none is invented; they appear as-is in the Customer filter.",
        "ar": "يوجد {count} سجل عميل في البيانات المصدرية اسم العميل فيه مجرد رقم ({values}) - وليس اسم منشأة أو "
              "شخص حقيقياً، وليس رمز عميل 'نقدي' العام (الذي يُعالج بشكل منفصل). لا يوجد حقل اسم بديل لهؤلاء في "
              "المصدر، ولذلك لم يتم افتراض أي اسم، ويظهرون كما هم في عامل تصفية العميل.",
    },
    "cost_center_numeric_code_note": {
        "en": "{count} of {total} Local Purchase Return rows ({numeric_distinct} distinct codes: {codes}) still "
              "record Cost Center as a legacy numeric warehouse code rather than a business name in the source "
              "data. No mapping sheet exists in the workbook to translate these codes to names, so none is "
              "invented here - they are shown exactly as sourced in the Cost Center filter and charts. "
              "Management/accounting confirmation of what each code represents is recommended.",
        "ar": "لا تزال {count} من إجمالي {total} حركة من مردود المشتريات الداخلية ({numeric_distinct} كوداً مختلفاً: "
              "{codes}) مسجلة بكود مستودع رقمي قديم بدلاً من اسم مركز تكلفة فعلي في البيانات المصدرية. لا يوجد في "
              "الملف أي جدول مطابقة يترجم هذه الأكواد إلى أسماء، ولذلك لم يتم افتراض أي مطابقة، وتُعرض هذه الأكواد "
              "كما هي في عامل تصفية مركز التكلفة والرسوم البيانية. يُنصح بالحصول على تأكيد من الإدارة/المحاسبة لما "
              "تمثله هذه الأكواد.",
    },

    # ---- 48-month continuous Sales trend (management request) ----
    "monthly_sales_full_history": {"en": "Monthly Net Sales Trend 2022-2025", "ar": "الاتجاه الشهري لصافي المبيعات 2022-2025"},
    "monthly_sales_full_history_note": {
        "en": "One continuous line of Net Sales (Gross Sales − Sales Returns) for every month from January 2022 "
              "through December 2025, in chronological order. This chart intentionally stays fixed at the full "
              "2022-2025 period and does not respond to the Year/Quarter filters, so it always shows the "
              "complete historical Sales journey.",
        "ar": "خط واحد متصل لصافي المبيعات (إجمالي المبيعات ناقص مردود المبيعات) لكل شهر من يناير 2022 حتى "
              "ديسمبر 2025، بالترتيب الزمني. يبقى هذا الرسم ثابتاً عمداً على كامل فترة 2022-2025 ولا يتأثر "
              "بعوامل تصفية السنة أو الربع، ليعرض دائماً المسار التاريخي الكامل للمبيعات.",
    },
    "full_period_2022_2025": {"en": "2022-2025 · Full Period", "ar": "2022-2025 · الفترة الكاملة"},
    "working_days_pending_calendar": {
        "en": "Not available until the holiday calendar is approved",
        "ar": "غير متاح حتى اعتماد تقويم الإجازات",
    },

    # ---- Working Days (management request - business calendar) ----
    "working_days": {"en": "Working Days", "ar": "أيام العمل"},
    "sales_per_working_day": {"en": "Sales per Working Day", "ar": "المبيعات لكل يوم عمل"},
    "working_days_note": {
        "en": "Working days exclude Fridays plus the configured one-week Eid Al-Fitr and one-week Eid Al-Adha "
              "holidays.",
        "ar": "يتم احتساب أيام العمل باستبعاد يوم الجمعة وأسبوع إجازة عيد الفطر وأسبوع إجازة عيد الأضحى وفق "
              "تقويم العمل المعتمد في التقرير.",
    },

    # ---- Supplier Balances (point-in-time source snapshots) ----
    "supplier_balances": {"en": "Supplier Balances", "ar": "أرصدة الموردين"},
    "total_supplier_debt": {"en": "Total Supplier Debt", "ar": "إجمالي مديونية الموردين"},
    "total_supplier_credit_balance": {"en": "Total Supplier Credit Balance", "ar": "إجمالي أرصدة الموردين الدائنة"},
    "supplier_debt_section": {"en": "Supplier Debt", "ar": "مديونية الموردين"},
    "supplier_creditors_section": {"en": "Supplier Creditors", "ar": "دائنين الموردين"},
    "top_supplier_debts": {"en": "Top Supplier Debts (Local Currency)", "ar": "أعلى مديونيات الموردين (بالعملة المحلية)"},
    "top_supplier_credits": {"en": "Top Supplier Credit Balances (Local Currency)",
                              "ar": "أعلى أرصدة الموردين الدائنة (بالعملة المحلية)"},
    "supplier_balance_detail": {"en": "Supplier Balance Detail", "ar": "تفاصيل أرصدة الموردين"},
    "currency_col": {"en": "Currency", "ar": "العملة"},
    "foreign_currency_amount_col": {"en": "Foreign Currency Amount", "ar": "القيمة بالعملة الأجنبية"},
    "local_currency_amount_col": {"en": "Local Currency Amount", "ar": "القيمة بالعملة المحلية"},
    "supplier_balance_snapshot_note": {
        "en": "Supplier Debt and Creditor balances are point-in-time snapshots from the source workbook - they "
              "have no transaction date and are not affected by the Year/Quarter filters.",
        "ar": "أرصدة مديونية ودائنية الموردين هي أرصدة لحظية من ملف المصدر - لا يوجد لها تاريخ حركة وهي غير "
              "متأثرة بعوامل تصفية السنة أو الربع.",
    },
    "supplier_balance_no_net_note": {
        "en": "Debt and Creditor balances are shown separately, not netted, because their sign conventions have "
              "not been confirmed as directly comparable.",
        "ar": "تُعرض أرصدة المديونية والدائنية بشكل منفصل دون خصم أحدهما من الآخر، لأن دلالة الإشارة (موجب/سالب) "
              "في كل منهما لم يتم التحقق من كونها قابلة للمقارنة المباشرة.",
    },
}


def t(key: str, lang: str = "en") -> str:
    """Looks up a translation key. Raises loudly on a missing key/lang rather
    than silently falling back, so a Phase 3 UI never ships a blank label."""
    if key not in TRANSLATIONS:
        raise KeyError(f"Missing translation key: '{key}'")
    entry = TRANSLATIONS[key]
    if lang not in entry:
        raise KeyError(f"Translation key '{key}' has no '{lang}' value")
    return entry[lang]


def direction(lang: str) -> str:
    return "rtl" if lang == "ar" else "ltr"


def localize_comparison_label(comparison: str, lang: str) -> str:
    """'2024 vs 2023' -> '2024 مقابل 2023' in Arabic. Centralized here so every
    caller that formats a YoY comparison string (KPI deltas, the YoY page,
    Executive Insights, Management Attention) localizes it the same way -
    confirmed bug: the raw English index string (built internally as
    f"{cur} vs {prev}") was leaking untranslated into Arabic narrative text
    wherever a caller forgot this step."""
    if lang != "ar" or " vs " not in comparison:
        return comparison
    cur, prev = comparison.split(" vs ")
    return f"{cur} {t('yoy_vs_label', lang)} {prev}"
