"""
Day 13 — Multi-language translations for HealthLabelCheck
Provides English, Marathi (mr) and Hindi (hi) strings for:
  - Regulation requirement names
  - Compliance status labels
  - Hint messages
  - UI strings

Usage:
    from app.translations import t, SUPPORTED_LANGS
    print(t("5.1", "requirement", "mr"))  # Marathi name for Reg 5.1
    print(t("status_present", lang="hi")) # Hindi for "Present"
"""

from typing import Dict

SUPPORTED_LANGS = ["en", "mr", "hi"]

# ── Regulation requirement names ──────────────────────────────────────────────

REGULATION_NAMES: Dict[str, Dict[str, str]] = {
    "5.1": {
        "en": "Name of Food",
        "mr": "अन्नाचे नाव",
        "hi": "खाद्य पदार्थ का नाम",
    },
    "5.2": {
        "en": "List of Ingredients",
        "mr": "घटकांची यादी",
        "hi": "सामग्री की सूची",
    },
    "5.3": {
        "en": "Nutritional Information",
        "mr": "पोषण माहिती",
        "hi": "पोषण संबंधी जानकारी",
    },
    "5.4": {
        "en": "Allergen Declaration",
        "mr": "अ‍ॅलर्जन घोषणा",
        "hi": "एलर्जेन घोषणा",
    },
    "5.5": {
        "en": "Manufacturer Name & Address",
        "mr": "उत्पादकाचे नाव व पत्ता",
        "hi": "निर्माता का नाम और पता",
    },
    "5.6": {
        "en": "Net Quantity",
        "mr": "निव्वळ प्रमाण",
        "hi": "शुद्ध मात्रा",
    },
    "5.7": {
        "en": "Date of Manufacture & Best Before",
        "mr": "उत्पादन तारीख व बेस्ट बिफोर",
        "hi": "निर्माण तिथि और बेस्ट बिफोर",
    },
    "5.8": {
        "en": "FSSAI License Number",
        "mr": "FSSAI परवाना क्रमांक",
        "hi": "FSSAI लाइसेंस नंबर",
    },
    "5.9": {
        "en": "Country of Origin",
        "mr": "उत्पत्तीचा देश",
        "hi": "उत्पत्ति का देश",
    },
    "5.10": {
        "en": "Veg / Non-Veg Symbol",
        "mr": "शाकाहारी / मांसाहारी चिन्ह",
        "hi": "शाकाहारी / मांसाहारी चिह्न",
    },
    "5.11": {
        "en": "Storage / Usage Instructions",
        "mr": "साठवणूक / वापर सूचना",
        "hi": "भंडारण / उपयोग निर्देश",
    },
    "5.12": {
        "en": "Food Additive Declaration",
        "mr": "खाद्य मिश्रित घोषणा",
        "hi": "खाद्य योजक घोषणा",
    },
    "6.1": {
        "en": "Minimum Font Size (Reg 6.1)",
        "mr": "किमान अक्षर आकार (नियम 6.1)",
        "hi": "न्यूनतम फ़ॉन्ट आकार (नियम 6.1)",
    },
    "6.2": {
        "en": "Legibility & Contrast",
        "mr": "वाचनीयता व रंग फरक",
        "hi": "पठनीयता और कंट्रास्ट",
    },
}

# ── Hints (what to add if missing) ───────────────────────────────────────────

HINTS: Dict[str, Dict[str, str]] = {
    "5.1": {
        "en": "Print the common/generic name of your food product.",
        "mr": "तुमच्या खाद्य पदार्थाचे सामान्य नाव छापा.",
        "hi": "अपने खाद्य उत्पाद का सामान्य/सामान्य नाम प्रिंट करें।",
    },
    "5.2": {
        "en": "List all ingredients in descending order by weight.",
        "mr": "सर्व घटक वजनाच्या उतरत्या क्रमाने लिहा.",
        "hi": "सभी सामग्री को वजन के घटते क्रम में सूचीबद्ध करें।",
    },
    "5.3": {
        "en": "Add a nutrition table: Energy, Protein, Carbs, Fat, Sodium per 100 g.",
        "mr": "पोषण तक्ता जोडा: ऊर्जा, प्रथिने, कर्बोदके, चरबी, सोडियम प्रति 100 ग्रॅम.",
        "hi": "पोषण तालिका जोड़ें: ऊर्जा, प्रोटीन, कार्बोहाइड्रेट, वसा, सोडियम प्रति 100 ग्राम।",
    },
    "5.4": {
        "en": "If your product contains allergens, declare them: 'Contains: [allergen]'.",
        "mr": "जर उत्पादनात अ‍ॅलर्जन असेल तर घोषित करा: 'यात आहे: [अ‍ॅलर्जन]'.",
        "hi": "यदि उत्पाद में एलर्जेन हैं, तो घोषित करें: 'इसमें शामिल है: [एलर्जेन]'।",
    },
    "5.5": {
        "en": "Print full manufacturer name and address (street, city, state, pin code).",
        "mr": "उत्पादकाचे संपूर्ण नाव व पत्ता छापा (रस्ता, शहर, राज्य, पिन कोड).",
        "hi": "निर्माता का पूरा नाम और पता प्रिंट करें (सड़क, शहर, राज्य, पिन कोड)।",
    },
    "5.6": {
        "en": "Print net quantity in metric units, e.g. 'Net Qty: 200g'.",
        "mr": "मेट्रिक एककांमध्ये निव्वळ प्रमाण छापा, उदा. 'निव्वळ प्रमाण: 200 ग्रॅम'.",
        "hi": "मीट्रिक इकाइयों में शुद्ध मात्रा प्रिंट करें, जैसे 'शुद्ध मात्रा: 200 ग्राम'।",
    },
    "5.7": {
        "en": "Print MFD date and Best Before date in DD/MM/YYYY format.",
        "mr": "उत्पादन तारीख व बेस्ट बिफोर तारीख DD/MM/YYYY स्वरूपात छापा.",
        "hi": "उत्पादन तिथि और बेस्ट बिफोर तिथि DD/MM/YYYY प्रारूप में प्रिंट करें।",
    },
    "5.8": {
        "en": "Print 'FSSAI Lic. No.: XXXXXXXXXXXXXX' with the FSSAI logo.",
        "mr": "'FSSAI परवाना क्र.: XXXXXXXXXXXXXX' FSSAI लोगोसह छापा.",
        "hi": "'FSSAI लाइसेंस नं.: XXXXXXXXXXXXXX' FSSAI लोगो के साथ प्रिंट करें।",
    },
    "5.9": {
        "en": "For imported products, print 'Country of Origin: [country]'.",
        "mr": "आयात केलेल्या उत्पादनांसाठी 'उत्पत्तीचा देश: [देश]' छापा.",
        "hi": "आयातित उत्पादों के लिए 'उत्पत्ति का देश: [देश]' प्रिंट करें।",
    },
    "5.10": {
        "en": "Display the green (veg) or brown (non-veg) filled circle in a square, min 3 mm.",
        "mr": "हिरवे (शाकाहारी) किंवा तपकिरी (मांसाहारी) भरलेले वर्तुळ चौकोनात दाखवा, किमान 3 मिमी.",
        "hi": "हरे (शाकाहारी) या भूरे (मांसाहारी) भरे हुए वृत्त को वर्ग में दिखाएं, न्यूनतम 3 मिमी।",
    },
    "5.11": {
        "en": "If special storage is needed, print instructions (e.g. 'Store in a cool, dry place').",
        "mr": "विशेष साठवणूक आवश्यक असल्यास सूचना छापा (उदा. 'थंड, कोरड्या ठिकाणी ठेवा').",
        "hi": "यदि विशेष भंडारण की आवश्यकता है, तो निर्देश प्रिंट करें (जैसे 'ठंडी, सूखी जगह पर रखें')।",
    },
    "5.12": {
        "en": "If you use additives, declare them: e.g. 'Preservative (INS 211)'.",
        "mr": "जर मिश्रित पदार्थ वापरत असाल तर घोषित करा: उदा. 'संरक्षक (INS 211)'.",
        "hi": "यदि आप योजक का उपयोग करते हैं, तो घोषित करें: जैसे 'परिरक्षक (INS 211)'।",
    },
    "6.1": {
        "en": "Ensure mandatory text is printed at minimum 1.5 mm height for a 96 cm² panel.",
        "mr": "96 चौ.सेमी. पॅनेलसाठी अनिवार्य मजकूर किमान 1.5 मिमी उंचीने छापा.",
        "hi": "96 सेमी² पैनल के लिए अनिवार्य टेक्स्ट न्यूनतम 1.5 मिमी ऊंचाई पर प्रिंट करें।",
    },
    "6.2": {
        "en": "Print all mandatory info in a colour that contrasts with the background.",
        "mr": "सर्व अनिवार्य माहिती पार्श्वभूमीशी विरोधाभासी रंगात छापा.",
        "hi": "सभी अनिवार्य जानकारी को पृष्ठभूमि के विपरीत रंग में प्रिंट करें।",
    },
}

# ── UI strings ────────────────────────────────────────────────────────────────

UI_STRINGS: Dict[str, Dict[str, str]] = {
    "status_present": {
        "en": "Present ✓",
        "mr": "उपस्थित ✓",
        "hi": "मौजूद ✓",
    },
    "status_missing": {
        "en": "Missing ✗",
        "mr": "गहाळ ✗",
        "hi": "अनुपस्थित ✗",
    },
    "mandatory": {
        "en": "Mandatory",
        "mr": "अनिवार्य",
        "hi": "अनिवार्य",
    },
    "conditional": {
        "en": "Conditional",
        "mr": "सशर्त",
        "hi": "सशर्त",
    },
    "compliance_summary": {
        "en": "Mandatory compliance: {present}/{total} ({pct}%)",
        "mr": "अनिवार्य अनुपालन: {present}/{total} ({pct}%)",
        "hi": "अनिवार्य अनुपालन: {present}/{total} ({pct}%)",
    },
    "missing_items_header": {
        "en": "Missing items — what to add:",
        "mr": "गहाळ बाबी — काय जोडायचे:",
        "hi": "अनुपस्थित आइटम — क्या जोड़ें:",
    },
    "all_compliant": {
        "en": "All mandatory items are present on the label.",
        "mr": "लेबलवर सर्व अनिवार्य बाबी उपस्थित आहेत.",
        "hi": "लेबल पर सभी अनिवार्य आइटम मौजूद हैं।",
    },
    "app_title": {
        "en": "HealthLabelCheck",
        "mr": "हेल्थलेबलचेक",
        "hi": "हेल्थलेबलचेक",
    },
    "app_subtitle": {
        "en": "FSSAI Food Labelling Advisor",
        "mr": "FSSAI अन्न लेबलिंग सल्लागार",
        "hi": "FSSAI खाद्य लेबलिंग सलाहकार",
    },
}


# ── Lookup helper ─────────────────────────────────────────────────────────────

def t(key: str, field: str = "requirement", lang: str = "en") -> str:
    """
    Translate a key into the target language.

    Args:
        key   : regulation_no (e.g. "5.1") OR a UI string key (e.g. "status_present")
        field : "requirement" | "hint" (ignored for UI string keys)
        lang  : "en" | "mr" | "hi"

    Returns:
        Translated string, falling back to English if not found.
    """
    if lang not in SUPPORTED_LANGS:
        lang = "en"

    # Try regulation lookup first
    if key in REGULATION_NAMES:
        if field == "requirement":
            return REGULATION_NAMES[key].get(lang) or REGULATION_NAMES[key]["en"]
        elif field == "hint":
            return HINTS.get(key, {}).get(lang) or HINTS.get(key, {}).get("en", "")

    # Try UI string lookup
    if key in UI_STRINGS:
        return UI_STRINGS[key].get(lang) or UI_STRINGS[key]["en"]

    return key  # return key itself as fallback


def translate_results(results: list, lang: str = "en") -> list:
    """
    Add translated requirement and hint fields to check_label() output.

    Each result dict gets two extra keys:
        requirement_translated : str
        hint_translated        : str
    """
    if lang == "en":
        return results  # nothing to do

    translated = []
    for r in results:
        item = dict(r)
        item["requirement_translated"] = t(r["regulation_no"], "requirement", lang)
        item["hint_translated"] = t(r["regulation_no"], "hint", lang) if r["status"] == "missing" else ""
        translated.append(item)
    return translated


# ── Standalone test ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=== Translation samples ===\n")
    for reg_no in ["5.1", "5.3", "5.8", "5.10", "6.1"]:
        print(f"Reg {reg_no}:")
        for lang in SUPPORTED_LANGS:
            print(f"  [{lang}] {t(reg_no, 'requirement', lang)}")
        print()

    print("=== UI strings ===")
    for key in ["status_present", "status_missing", "mandatory", "compliance_summary"]:
        print(f"\n{key}:")
        for lang in SUPPORTED_LANGS:
            print(f"  [{lang}] {t(key, lang=lang)}")
