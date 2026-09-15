# -*- coding: utf-8 -*-
"""
Centralized bilingual chart/section explanations - the counterpart to
kpi_metadata.py for charts instead of KPI cards. Keyed by the SAME
translations.py key already used for that chart's section_header() text, so
one entry covers every page where that chart/section appears.

Each explanation is written to answer three questions concisely: what the
chart shows, how the main metric is calculated, and how management should
read it - never a long paragraph.
"""

CHART_METADATA = {
    # ---- Shared / Executive Overview ----
    "monthly_net_sales_trend": {
        "en": "Shows monthly Net Sales across years. Net Sales = Gross Sales before VAT − Sales Returns "
              "before VAT. Use it to identify seasonality and periods of growth or decline.",
        "ar": "يعرض صافي المبيعات لكل شهر ومقارنته بين السنوات. صافي المبيعات = إجمالي المبيعات قبل الضريبة "
              "− مردود المبيعات قبل الضريبة. يساعد الرسم على تحديد الاتجاهات الموسمية وفترات النمو أو التراجع.",
    },
    "annual_performance_comparison": {
        "en": "Compares financial performance across 2022–2025 and highlights changes in major KPIs from "
              "one year to another.",
        "ar": "يقارن الأداء المالي بين السنوات 2022–2025 ويوضح التغير في المؤشرات الرئيسية من سنة إلى أخرى.",
    },
    "sales_return_rate_trend": {
        "en": "Tracks Sales Return Rate over time. Sales Return Rate = Sales Returns before VAT ÷ Gross "
              "Sales before VAT × 100. A rising rate may require investigation.",
        "ar": "يعرض نسبة مردود المبيعات عبر الزمن. نسبة مردود المبيعات = مردود المبيعات قبل الضريبة ÷ "
              "إجمالي المبيعات قبل الضريبة × 100. ارتفاع النسبة قد يشير إلى حاجة لمراجعة أسباب المرتجعات.",
    },
    "annual_profit": {
        "en": "Annual Profit as read directly from the approved Profit sheet for each year - not calculated "
              "inside the dashboard from Sales or Purchases.",
        "ar": "الربح السنوي كما هو مسجل مباشرة في شيت الأرباح المعتمد لكل سنة - لا يتم احتسابه داخل لوحة "
              "المعلومات من المبيعات أو المشتريات.",
    },
    "monthly_sales_full_history": {
        "en": "One continuous line of Net Sales (Gross Sales − Sales Returns) for every month from January "
              "2022 through December 2025, in chronological order - the complete historical Sales journey. "
              "This chart always shows the full 2022-2025 period and does not respond to the Year/Quarter "
              "filters. Hover any point for that month's Net Sales and Working Days.",
        "ar": "خط واحد متصل لصافي المبيعات (إجمالي المبيعات ناقص مردود المبيعات) لكل شهر من يناير 2022 حتى "
              "ديسمبر 2025 بالترتيب الزمني - المسار التاريخي الكامل للمبيعات. يعرض هذا الرسم دائماً كامل فترة "
              "2022-2025 ولا يتأثر بعوامل تصفية السنة أو الربع. مرر المؤشر على أي نقطة لعرض صافي المبيعات "
              "وأيام العمل لذلك الشهر.",
    },
    "monthly_sales_4yr_comparison": {
        "en": "Shows monthly Net Sales with one line per year (2022–2025), so the same calendar month can be "
              "compared directly across years (e.g. every January side by side). Hover a point to see its "
              "Working Days count for that month.",
        "ar": "يعرض صافي المبيعات الشهري بخط منفصل لكل سنة (2022–2025)، بما يتيح مقارنة نفس الشهر التقويمي "
              "مباشرة بين السنوات (مثال: كل شهر يناير جنباً إلى جنب). مرر المؤشر على أي نقطة لعرض عدد أيام "
              "العمل لذلك الشهر.",
    },

    # ---- Sales Performance ----
    "gross_sales_vs_returns": {
        "en": "Compares Gross Sales with Sales Returns for each year, showing return volume relative to "
              "total sales activity.",
        "ar": "يقارن إجمالي المبيعات بمردود المبيعات لكل سنة، موضحاً حجم المرتجعات مقارنة بإجمالي نشاط المبيعات.",
    },
    "sales_by_transaction_type": {
        "en": "Breaks down sales value by transaction type (cash, credit, services), showing the sales mix.",
        "ar": "يوزع قيمة المبيعات حسب نوع الحركة (نقدي، آجل، خدمات)، موضحاً تركيبة المبيعات.",
    },
    "sales_quantity_trend": {
        "en": "Shows monthly sales quantity (units) across years - useful for spotting volume trends "
              "independent of price or VAT changes.",
        "ar": "يعرض كمية المبيعات الشهرية (بالوحدات) عبر السنوات - مفيد لرصد اتجاهات الحجم بمعزل عن تغيرات "
              "السعر أو الضريبة.",
    },

    # ---- Purchasing Performance (Local vs Foreign kept separate throughout) ----
    "local_vs_foreign_by_year": {
        "en": "Compares annual Local Purchases with Foreign Purchases across 2022–2025, kept as two distinct "
              "measures rather than one combined figure.",
        "ar": "يقارن المشتريات الداخلية السنوية بالمشتريات الخارجية بين أعوام 2022–2025، كمؤشرين منفصلين "
              "بدلاً من رقم واحد مجمّع.",
    },
    "local_vs_foreign_by_month": {
        "en": "Shows the monthly trend of Local Purchases and Foreign Purchases across years, useful for "
              "identifying purchasing seasonality in each channel separately.",
        "ar": "يعرض الاتجاه الشهري للمشتريات الداخلية والمشتريات الخارجية عبر السنوات، ومفيد لتحديد الموسمية "
              "الشرائية في كل قناة على حدة.",
    },
    "local_purchases_by_type": {
        "en": "Breaks down Local Purchases value by transaction type (cash or credit).",
        "ar": "يوزع قيمة المشتريات الداخلية حسب نوع الحركة (نقدي أو آجل).",
    },
    "foreign_purchases_by_supplier": {
        "en": "Ranks Foreign Purchase suppliers by purchase value, showing where foreign purchasing activity "
              "is concentrated. Local Purchase Returns cannot be attributed to individual suppliers.",
        "ar": "يرتب موردي المشتريات الخارجية حسب قيمة المشتريات، موضحاً أين يتركز النشاط الشرائي الخارجي. لا "
              "يمكن نسب مردود المشتريات الداخلية لموردين محددين.",
    },
    "local_purchases_by_supplier": {
        "en": "Ranks Local Purchase suppliers by purchase value, showing where local purchasing activity is "
              "concentrated.",
        "ar": "يرتب موردي المشتريات الداخلية حسب قيمة المشتريات، موضحاً أين يتركز النشاط الشرائي الداخلي.",
    },
    "local_supplier_concentration": {
        "en": "Top 5 / Top 10 Supplier Share within Local Purchases only - shows how much local purchasing "
              "activity depends on the largest local suppliers.",
        "ar": "توضح نسبة أفضل 5 / أفضل 10 موردين ضمن المشتريات الداخلية فقط - مدى اعتماد المشتريات الداخلية "
              "على أكبر الموردين المحليين.",
    },
    "foreign_supplier_concentration": {
        "en": "Top 5 / Top 10 Supplier Share within Foreign Purchases only - shows how much foreign "
              "purchasing activity depends on the largest foreign suppliers.",
        "ar": "توضح نسبة أفضل 5 / أفضل 10 موردين ضمن المشتريات الخارجية فقط - مدى اعتماد المشتريات الخارجية "
              "على أكبر الموردين الخارجيين.",
    },

    # ---- Returns Analysis ----
    "monthly_trend_sales_returns": {
        "en": "Shows monthly Sales Returns value across years, useful for spotting unusual return spikes.",
        "ar": "يعرض قيمة مردود المبيعات الشهرية عبر السنوات، ومفيد لرصد الارتفاعات غير المعتادة في المرتجعات.",
    },
    "annual_trend_sales_returns": {
        "en": "Compares annual Sales Returns value across 2022–2025.",
        "ar": "يقارن قيمة مردود المبيعات السنوية بين أعوام 2022–2025.",
    },
    "customers_highest_returns": {
        "en": "Ranks customers by total Sales Returns value, highlighting where returns are concentrated.",
        "ar": "يرتب العملاء حسب إجمالي قيمة مردود المبيعات، موضحاً أين تتركز المرتجعات.",
    },
    "original_sale_match_status": {
        "en": "Original-sale matching is exploratory only and is not used in financial calculations.",
        "ar": "الربط بالفاتورة الأصلية لأغراض الاستكشاف فقط ولا يدخل في الحسابات المالية.",
    },
    "monthly_trend_purchase_returns": {
        "en": "Shows the monthly value of Local Purchase Returns across years.",
        "ar": "يعرض القيمة الشهرية لمردود المشتريات الداخلية عبر السنوات.",
    },
    "annual_trend_purchase_returns": {
        "en": "Compares annual Local Purchase Returns value across 2022–2025.",
        "ar": "يقارن قيمة مردود المشتريات الداخلية السنوية بين أعوام 2022–2025.",
    },
    "local_purchase_returns_by_cost_center": {
        "en": "Shows Local Purchase Returns value by Cost Center, for internal tracking only - not linked to "
              "specific purchases or suppliers.",
        "ar": "يعرض قيمة مردود المشتريات الداخلية حسب مركز التكلفة، لأغراض المتابعة الداخلية فقط، ولا يرتبط "
              "بمشتريات أو موردين محددين.",
    },
    "purchase_returns_by_type": {
        "en": "Breaks down Local Purchase Returns value by transaction type (cash or credit return).",
        "ar": "يوزع قيمة مردود المشتريات الداخلية حسب نوع الحركة (مردود نقدي أو آجل).",
    },

    # ---- VAT Analysis (Output/Sales side only - Input VAT removed, management request) ----
    "vat_annual_comparison": {
        "en": "Compares Gross Output VAT, Sales Return VAT and Net Output VAT across 2022–2025.",
        "ar": "يقارن إجمالي ضريبة المخرجات وضريبة مردود المبيعات وصافي ضريبة المخرجات بين أعوام 2022–2025.",
    },
    "vat_monthly_trend": {
        "en": "Shows the monthly trend of Output VAT (VAT on sales) across years, before Sales Return VAT is "
              "netted off.",
        "ar": "يعرض الاتجاه الشهري لضريبة المخرجات (ضريبة المبيعات) عبر السنوات، قبل خصم ضريبة مردود المبيعات.",
    },

    # ---- Customers & Suppliers ----
    "top_customers": {
        "en": "Top 5 Customer Share shows how much of sales depends on the five largest customers. A "
              "higher percentage indicates greater concentration risk. The generic 'نقدي' cash/walk-in "
              "bucket is excluded from this analysis.",
        "ar": "نسبة أفضل 5 عملاء توضح مقدار اعتماد المبيعات على أكبر خمسة عملاء. ارتفاع النسبة يعني تركّزاً "
              "أعلى ومخاطر اعتماد أكبر. يُستبعد من هذا التحليل عملاء 'نقدي' العامون.",
    },
    "top_customers_net_sales": {
        "en": "Ranks identifiable customers by Net Sales value (generic 'نقدي' cash/walk-in sales excluded).",
        "ar": "يرتب العملاء المحددين حسب صافي المبيعات (يُستبعد عملاء 'نقدي' العامون).",
    },
    "top_customers_gross_sales": {
        "en": "Ranks identifiable customers by Gross Sales value, before returns and before VAT.",
        "ar": "يرتب العملاء المحددين حسب إجمالي المبيعات قبل المرتجعات وقبل الضريبة.",
    },
    "top_customers_returns": {
        "en": "Ranks identifiable customers by total Sales Returns value.",
        "ar": "يرتب العملاء المحددين حسب إجمالي قيمة مردود المبيعات.",
    },
    "customer_return_rate": {
        "en": "Shows each customer's Sales Return Rate (returns as a % of their gross sales), helping "
              "identify accounts with unusually high return activity.",
        "ar": "يعرض نسبة مردود المبيعات لكل عميل (المرتجعات كنسبة من إجمالي مبيعاته)، مما يساعد على تحديد "
              "الحسابات ذات نشاط المرتجعات المرتفع بشكل غير معتاد.",
    },

    # ---- Year-over-Year ----
    "yoy_comparison_table": {
        "en": "Compares each KPI with the previous year. % Change = (Current Year − Previous Year) ÷ "
              "Previous Year × 100.",
        "ar": "يقارن كل مؤشر بالسنة السابقة. نسبة التغير = (قيمة السنة الحالية − قيمة السنة السابقة) ÷ "
              "قيمة السنة السابقة × 100.",
    },
    "net_sales_vs_net_purchases_trend": {
        "en": "Compares Net Sales with Total Purchases (Local + Foreign) over time - two independent "
              "activity measures, not a profit calculation.",
        "ar": "يقارن صافي المبيعات بإجمالي المشتريات (الداخلية + الخارجية) عبر الزمن - مؤشران مستقلان "
              "للنشاط، وليسا حساباً للربح.",
    },

    # ---- Supplier Balances ----
    "top_supplier_debts": {
        "en": "Ranks suppliers by Supplier Debt balance (local currency), as reported in the source "
              "workbook snapshot.",
        "ar": "يرتب الموردين حسب رصيد مديونية المورد (بالعملة المحلية)، كما هو مسجل في لقطة ملف المصدر.",
    },
    "top_supplier_credits": {
        "en": "Ranks suppliers by Supplier Creditor balance (local currency), as reported in the source "
              "workbook snapshot. Signs are kept exactly as sourced.",
        "ar": "يرتب الموردين حسب رصيد دائنية المورد (بالعملة المحلية)، كما هو مسجل في لقطة ملف المصدر. تُحفظ "
              "الإشارات (موجب/سالب) تماماً كما وردت في المصدر.",
    },

    # ---- Data Quality ----
    "total_records": {
        "en": "The total number of transaction rows found across all source sheets (Sales, Sales Returns, "
              "Local Purchases, Foreign Purchases, Local Purchase Returns, Profit, Supplier Debt, Supplier "
              "Creditors).",
        "ar": "إجمالي عدد صفوف الحركات في جميع الأوراق المصدرية (المبيعات، مردود المبيعات، المشتريات "
              "الداخلية، المشتريات الخارجية، مردود المشتريات الداخلية، الأرباح، مديونية الموردين، دائنين "
              "الموردين).",
    },
    "valid_records": {
        "en": "Records that passed every reconciliation check with no discrepancy.",
        "ar": "السجلات التي اجتازت جميع اختبارات المطابقة دون أي فروقات.",
    },
    "warning_records": {
        "en": "Records with a minor discrepancy flagged for review - kept in every total, not excluded.",
        "ar": "سجلات تحتوي على فارق بسيط تم رصده للمراجعة - تبقى ضمن جميع الإجماليات ولا يتم استبعادها.",
    },
    "analytical_exclusions": {
        "en": "Records excluded from every calculation because they are not real transactions (e.g. an "
              "embedded report-total or subtotal row in the source file).",
        "ar": "سجلات مستبعدة من جميع الحسابات لأنها ليست حركات فعلية (مثل صف إجمالي أو مجموع فرعي مضمّن في "
              "الملف المصدري).",
    },
    "reconciliation_success_rate": {
        "en": "The percentage of checked records that reconciled exactly with no discrepancy.",
        "ar": "نسبة السجلات التي تمت مطابقتها بشكل تام دون أي فروقات، من إجمالي السجلات التي تم فحصها.",
    },
    "reconciliation_review_records": {
        "en": "Records with a small reported-vs-calculated difference that a finance user should review, "
              "shown separately by source sheet.",
        "ar": "سجلات بها فارق بسيط بين القيمة المُدخلة والمحسوبة يستحسن أن يراجعها فريق المالية، معروضة "
              "بشكل منفصل حسب الورقة المصدرية.",
    },
}


def get_chart_tooltip(key: str, lang: str) -> str | None:
    entry = CHART_METADATA.get(key)
    return entry[lang] if entry else None
