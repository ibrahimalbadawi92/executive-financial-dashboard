# -*- coding: utf-8 -*-
"""
Centralized bilingual KPI definitions - the single source of truth for every
"what does this number mean" tooltip in the dashboard. Referenced by
ui_components.kpi_from_metrics() via metric_key, so a definition written here
once is automatically available everywhere that KPI is shown (Executive
Overview, Sales Performance, Purchasing Performance, VAT Analysis, Returns
Analysis, ...) - no page hardcodes its own copy of the text.

Each entry's key matches a financial_metrics.compute_period_metrics() output
key exactly, so lookup is a plain dict get by metric_key - no per-page wiring.
"""

KPI_METADATA = {
    "net_sales_before_vat": {
        "definition": {
            "en": "Net Sales = Gross Sales before VAT − Sales Returns before VAT.",
            "ar": "صافي المبيعات = إجمالي المبيعات قبل الضريبة − مردود المبيعات قبل الضريبة.",
        },
    },
    "gross_sales_before_vat": {
        "definition": {
            "en": "Gross Sales represents total sales before deducting sales returns and before VAT.",
            "ar": "إجمالي المبيعات يمثل قيمة المبيعات قبل خصم مردود المبيعات وقبل ضريبة القيمة المضافة.",
        },
    },
    "sales_returns_before_vat": {
        "definition": {
            "en": "Sales Returns represents the value of returned sales before VAT.",
            "ar": "مردود المبيعات يمثل قيمة المبيعات المرتجعة قبل ضريبة القيمة المضافة.",
        },
    },
    "sales_return_rate_pct": {
        "definition": {
            "en": "Sales Return Rate = Sales Returns before VAT ÷ Gross Sales before VAT × 100.",
            "ar": "نسبة مردود المبيعات = مردود المبيعات قبل الضريبة ÷ إجمالي المبيعات قبل الضريبة × 100.",
        },
    },
    "local_purchases_before_vat": {
        "definition": {
            "en": "Local Purchases represents domestic purchase value before VAT.",
            "ar": "المشتريات الداخلية تمثل قيمة المشتريات المحلية قبل ضريبة القيمة المضافة.",
        },
    },
    "local_purchase_vat": {
        "definition": {
            "en": "VAT charged on Local Purchases.",
            "ar": "ضريبة القيمة المضافة المحتسبة على المشتريات الداخلية.",
        },
    },
    "local_purchases_incl_vat": {
        "definition": {
            "en": "Local Purchases Including VAT = Local Purchases before VAT + Local Purchase VAT.",
            "ar": "المشتريات الداخلية شامل الضريبة = المشتريات الداخلية قبل الضريبة + ضريبة المشتريات الداخلية.",
        },
    },
    "foreign_purchase_base": {
        "definition": {
            "en": "The base purchase value of Foreign (import/LC) Purchases, before Additional Cost.",
            "ar": "القيمة الأساسية للمشتريات الخارجية (اعتماد/استيراد)، قبل التكلفة الإضافية.",
        },
    },
    "foreign_purchase_additional_cost": {
        "definition": {
            "en": "Additional costs recorded on Foreign Purchase transactions (e.g. freight, customs-related "
                  "charges). This amount is already included in the Foreign Purchase Total and must not be "
                  "added again when interpreting total foreign purchasing activity.",
            "ar": "التكاليف الإضافية المسجلة على حركات المشتريات الخارجية (مثل الشحن أو الرسوم الجمركية). هذه "
                  "القيمة مضمّنة بالفعل ضمن إجمالي المشتريات الخارجية، ولا يجب إضافتها مرة أخرى عند قراءة "
                  "إجمالي النشاط الشرائي الخارجي.",
        },
    },
    "foreign_purchase_total": {
        "definition": {
            "en": "Foreign Purchase Total = Foreign Purchase Base + Additional Foreign Purchase Cost. The "
                  "source data does not carry a domestic VAT field for Foreign Purchases.",
            "ar": "إجمالي المشتريات الخارجية = أساس المشتريات الخارجية + التكلفة الإضافية للمشتريات الخارجية. "
                  "لا تحتوي بيانات المصدر على حقل ضريبة قيمة مضافة محلية للمشتريات الخارجية.",
        },
    },
    "total_purchases_before_vat": {
        "definition": {
            "en": "Total Purchases = Local Purchases (before VAT) + Foreign Purchase Total. Two "
                  "VAT-exclusive purchasing bases combined - not purchasing activity net of returns, and not "
                  "Cost of Goods Sold.",
            "ar": "إجمالي المشتريات = المشتريات الداخلية (قبل الضريبة) + إجمالي المشتريات الخارجية. مجموع "
                  "قاعدتين شرائيتين قبل الضريبة - لا يمثل النشاط الشرائي بعد خصم المرتجعات، ولا يمثل تكلفة "
                  "البضاعة المباعة.",
        },
    },
    "local_purchase_returns_before_vat": {
        "definition": {
            "en": "Local Purchase Returns represents returned local-purchase value before VAT. Applies to "
                  "Local Purchases only - never subtracted from Foreign Purchases, and cannot be attributed "
                  "to an individual supplier (no supplier field exists on this data).",
            "ar": "مردود المشتريات الداخلية يمثل قيمة المشتريات الداخلية المرتجعة قبل الضريبة. يخص المشتريات "
                  "الداخلية فقط - ولا يُخصم إطلاقاً من المشتريات الخارجية، ولا يمكن نسبته لمورد محدد (لا يوجد "
                  "حقل مورد في هذه البيانات).",
        },
    },
    "local_purchase_returns_vat": {
        "definition": {
            "en": "VAT associated with Local Purchase Returns.",
            "ar": "ضريبة القيمة المضافة المرتبطة بمردود المشتريات الداخلية.",
        },
    },
    "gross_output_vat": {
        "definition": {
            "en": "VAT recorded on gross sales before deducting VAT associated with sales returns.",
            "ar": "ضريبة القيمة المضافة المسجلة على إجمالي المبيعات قبل خصم ضريبة مردود المبيعات.",
        },
    },
    "sales_return_vat": {
        "definition": {
            "en": "VAT associated with Sales Returns.",
            "ar": "ضريبة القيمة المضافة المرتبطة بمردود المبيعات.",
        },
    },
    "net_output_vat": {
        "definition": {
            "en": "Net Output VAT = Gross Output VAT − Sales Return VAT.",
            "ar": "صافي ضريبة المخرجات = إجمالي ضريبة المخرجات − ضريبة مردود المبيعات.",
        },
    },
    "gross_sales_incl_vat": {
        "definition": {
            "en": "Gross Sales Including VAT = total sales value including VAT, before deducting Sales "
                  "Returns.",
            "ar": "إجمالي المبيعات شامل الضريبة = قيمة المبيعات شاملة الضريبة قبل خصم مردود المبيعات.",
        },
    },
    "net_sales_incl_vat": {
        "definition": {
            "en": "Net Sales Including VAT = Gross Sales Including VAT − Sales Returns Including VAT.",
            "ar": "صافي المبيعات شامل الضريبة = إجمالي المبيعات شامل الضريبة − مردود المبيعات شامل الضريبة.",
        },
    },
    "profit": {
        "definition": {
            "en": "The displayed Profit value is read directly from the approved Profit sheet in the source "
                  "workbook. It is not calculated inside the dashboard from Sales or Purchases.",
            "ar": "قيمة الربح المعروضة مأخوذة مباشرة من شيت الأرباح المعتمد في ملف المصدر ولا يتم احتسابها "
                  "داخل لوحة المعلومات من المبيعات أو المشتريات.",
        },
    },
    "profit_yoy_change": {
        "definition": {
            "en": "Profit YoY Change = (Current Year Profit − Previous Year Profit) ÷ Previous Year Profit × "
                  "100 - a comparison of the approved supplied Profit values only.",
            "ar": "تغير الربح السنوي = (ربح السنة الحالية − ربح السنة السابقة) ÷ ربح السنة السابقة × 100 - "
                  "مقارنة بين قيم الربح المعتمدة المزوّدة فقط.",
        },
    },
    "cost_center": {
        "definition": {
            "en": "Cost Center as recorded directly in the source Local Purchase Returns data - used for "
                  "internal tracking only, not linked to specific purchases or suppliers.",
            "ar": "مركز التكلفة كما هو مسجل مباشرة في بيانات مردود المشتريات الداخلية المصدرية - لأغراض "
                  "المتابعة الداخلية فقط، ولا يرتبط بمشتريات أو موردين محددين.",
        },
    },
    "sales_transaction_count": {
        "definition": {
            "en": "Number of valid sales transaction rows in the source data.",
            "ar": "عدد حركات المبيعات الصحيحة المسجلة في بيانات المصدر.",
        },
    },
    "purchase_transaction_count": {
        "definition": {
            "en": "Number of valid purchase transaction rows in the source data.",
            "ar": "عدد حركات المشتريات الصحيحة المسجلة في بيانات المصدر.",
        },
    },
    "avg_sales_transaction_value": {
        "definition": {
            "en": "Average Sales Transaction Value = Net Sales ÷ Sales Transaction Count.",
            "ar": "متوسط قيمة حركة المبيعات = صافي المبيعات ÷ عدد حركات المبيعات.",
        },
    },
    "additional_cost": {
        "definition": {
            "en": "Additional costs recorded on purchase transactions, such as related expenses or charges "
                  "captured in the source data. This amount is already included in Net Purchases and must not "
                  "be added again when interpreting total purchasing activity.",
            "ar": "التكاليف الإضافية المسجلة على حركات المشتريات، مثل المصاريف أو التكاليف الملحقة المسجلة في "
                  "المصدر. هذه القيمة مضمّنة بالفعل ضمن صافي المشتريات، لذلك لا يجب إضافتها مرة أخرى عند قراءة "
                  "إجمالي النشاط الشرائي.",
        },
    },
    "supplier_count": {
        "definition": {
            "en": "Number of distinct suppliers with purchase activity in the current filter scope.",
            "ar": "عدد الموردين المختلفين الذين لديهم نشاط شرائي ضمن نطاق التصفية الحالي.",
        },
    },
    "top5_supplier_share_pct": {
        "definition": {
            "en": "Shows the share of total purchase value generated by the five largest suppliers. A higher "
                  "percentage indicates greater dependence on a limited number of suppliers and potentially "
                  "higher supply concentration risk.",
            "ar": "تمثل نسبة قيمة المشتريات من أكبر 5 موردين إلى إجمالي قيمة المشتريات. ارتفاع النسبة يعني "
                  "اعتماداً أكبر على عدد محدود من الموردين، مما قد يزيد مخاطر التوريد.",
        },
    },
    "top10_supplier_share_pct": {
        "definition": {
            "en": "Shows the share of total purchase value generated by the ten largest suppliers. A higher "
                  "percentage indicates greater purchasing concentration among fewer suppliers.",
            "ar": "تمثل نسبة قيمة المشتريات من أكبر 10 موردين إلى إجمالي قيمة المشتريات. ارتفاع النسبة يعني "
                  "تركزاً أكبر للمشتريات لدى عدد محدود من الموردين.",
        },
    },
    "top5_customer_share_pct": {
        "definition": {
            "en": "Shows the share of total identifiable-customer Net Sales generated by the five largest "
                  "customers. A higher percentage means a larger share of sales depends on a relatively small "
                  "number of customers. The generic cash/walk-in bucket is excluded from this analysis.",
            "ar": "تمثل نسبة صافي مبيعات العملاء المحددين من أكبر 5 عملاء إلى إجمالي صافي مبيعاتهم. ارتفاع "
                  "النسبة يعني اعتماد جزء أكبر من المبيعات على عدد محدود من العملاء. يُستبعد من هذا التحليل "
                  "عملاء 'نقدي' العامون.",
        },
    },
    "top10_customer_share_pct": {
        "definition": {
            "en": "Shows the share of total identifiable-customer Net Sales generated by the ten largest "
                  "customers. A higher percentage means sales depend on a smaller base of customers. The "
                  "generic cash/walk-in bucket is excluded from this analysis.",
            "ar": "تمثل نسبة صافي مبيعات العملاء المحددين من أكبر 10 عملاء إلى إجمالي صافي مبيعاتهم. ارتفاع "
                  "النسبة يعني اعتماد المبيعات على قاعدة أصغر من العملاء. يُستبعد من هذا التحليل عملاء 'نقدي' "
                  "العامون.",
        },
    },
    "sales_returns_quantity": {
        "definition": {
            "en": "Total quantity of units recorded across the currently filtered Sales Returns.",
            "ar": "إجمالي كمية الوحدات المسجلة ضمن مردود المبيعات وفق نطاق التصفية الحالي.",
        },
    },
    "purchase_returns_quantity": {
        "definition": {
            "en": "Total quantity of units recorded across the currently filtered Purchase Returns.",
            "ar": "إجمالي كمية الوحدات المسجلة ضمن مردود المشتريات وفق نطاق التصفية الحالي.",
        },
    },
    "match_matched": {
        "definition": {
            "en": "Return rows matched to a likely original sale using best-effort logic (transaction number "
                  "and date). Illustrative only - not used in any financial total.",
            "ar": "صفوف مرتجعات تمت مطابقتها بفاتورة أصلية محتملة باستخدام منطق استرشادي (رقم الحركة والتاريخ). "
                  "لأغراض الاستكشاف فقط - لا تدخل في أي إجمالي مالي.",
        },
    },
    "match_unmatched": {
        "definition": {
            "en": "Return rows for which no original sale could be matched using best-effort logic.",
            "ar": "صفوف مرتجعات لم يتم العثور على فاتورة أصلية مطابقة لها باستخدام المنطق الاسترشادي.",
        },
    },
    "match_ambiguous": {
        "definition": {
            "en": "Return rows where more than one possible original sale matched - inconclusive, illustrative "
                  "only.",
            "ar": "صفوف مرتجعات تطابقت مع أكثر من فاتورة أصلية محتملة - نتيجة غير حاسمة ولأغراض الاستكشاف فقط.",
        },
    },
    "total_supplier_debt": {
        "definition": {
            "en": "Sum of supplier debt balances (local currency), exactly as reported in the source "
                  "workbook's Supplier Debt sheet - a point-in-time snapshot, not a dated transaction total.",
            "ar": "مجموع أرصدة مديونية الموردين (بالعملة المحلية)، كما هي مسجلة تماماً في ورقة مديونية "
                  "الموردين المصدرية - رصيد لحظي، وليس إجمالي حركات مؤرخة.",
        },
    },
    "total_supplier_credit_balance": {
        "definition": {
            "en": "Sum of supplier creditor balances (local currency), exactly as reported in the source "
                  "workbook's Supplier Creditors sheet - a point-in-time snapshot. Shown separately from "
                  "Supplier Debt, not netted, since the two sheets' sign conventions have not been confirmed "
                  "as directly comparable.",
            "ar": "مجموع أرصدة دائنية الموردين (بالعملة المحلية)، كما هي مسجلة تماماً في ورقة دائنين الموردين "
                  "المصدرية - رصيد لحظي. تُعرض منفصلة عن مديونية الموردين دون خصم، لأن دلالة الإشارة في كل "
                  "ورقة لم يتم التحقق من كونها قابلة للمقارنة المباشرة.",
        },
    },
}


def get_kpi_tooltip(metric_key: str, lang: str) -> str | None:
    """Definition + optional note, joined into one concise tooltip string."""
    meta = KPI_METADATA.get(metric_key)
    if not meta:
        return None
    parts = [meta["definition"][lang]]
    if "note" in meta:
        parts.append(meta["note"][lang])
    return " ".join(parts)


def has_kpi_definition(metric_key: str) -> bool:
    return metric_key in KPI_METADATA
