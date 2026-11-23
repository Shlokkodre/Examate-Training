"""
Day 13 — Multi-language label checker for HealthLabelCheck
Wraps label_checker.check_label() and returns the compliance table
with requirement names and hints translated into the requested language.

Supported languages: en (English), mr (Marathi), hi (Hindi)

Usage:
    from app.multilang_checker import check_label_multilang
    results = check_label_multilang(ocr_text, lang="mr")
"""

from typing import List, Dict

from app.label_checker import check_label, checklist_summary
from app.translations import translate_results, t, SUPPORTED_LANGS, UI_STRINGS


def check_label_multilang(ocr_text: str, lang: str = "en") -> Dict:
    """
    Run the FSSAI compliance check and return results translated into lang.

    Args:
        ocr_text : Raw text extracted from the label (by app/ocr.py).
        lang     : Language code — "en", "mr", or "hi". Falls back to "en".

    Returns dict with:
        lang            : language code used
        results         : list of compliance dicts with translated fields
        summary         : mandatory_present, mandatory_missing, compliance_pct
        summary_text    : human-readable summary in the target language
        missing_hints   : translated actionable hints for missing items
    """
    if lang not in SUPPORTED_LANGS:
        lang = "en"

    raw_results = check_label(ocr_text)
    summary     = checklist_summary(raw_results)
    translated  = translate_results(raw_results, lang)

    # Build human-readable summary string
    summary_template = UI_STRINGS["compliance_summary"].get(lang, UI_STRINGS["compliance_summary"]["en"])
    summary_text = summary_template.format(
        present=summary["mandatory_present"],
        total=summary["mandatory_total"],
        pct=summary["compliance_pct"],
    )

    # Build missing hints in the target language
    missing_hints = []
    for r in translated:
        if r["status"] == "missing":
            missing_hints.append({
                "regulation_no":          r["regulation_no"],
                "requirement":            r["requirement"],
                "requirement_translated": r.get("requirement_translated", r["requirement"]),
                "hint":                   r["hint"],
                "hint_translated":        r.get("hint_translated", r["hint"]),
            })

    # All-compliant message
    if not missing_hints:
        summary_text += "  " + UI_STRINGS["all_compliant"].get(lang, UI_STRINGS["all_compliant"]["en"])

    return {
        "lang":          lang,
        "results":       translated,
        "summary":       summary,
        "summary_text":  summary_text,
        "missing_hints": missing_hints,
    }


def format_multilang_table(check_output: Dict) -> str:
    """
    Render a plain-text compliance table from check_label_multilang() output.
    Shows both English and translated requirement names when lang != "en".
    """
    lang    = check_output["lang"]
    results = check_output["results"]

    lines = [
        f"{'Reg':>6}  {'Status':^9}  {'Req':^6}  Requirement"
        + (f" / {lang.upper()}" if lang != "en" else ""),
        "-" * 80,
    ]

    for r in results:
        status = "PASS" if r["status"] == "present" else "FAIL"
        req    = "YES"  if r["mandatory"]             else "cond"
        name   = r["requirement"]
        if lang != "en" and "requirement_translated" in r:
            name = f"{name}  [{r['requirement_translated']}]"
        lines.append(f"{r['regulation_no']:>6}  {status:^9}  {req:^6}  {name}")

    lines.append("")
    lines.append(check_output["summary_text"])

    missing = check_output["missing_hints"]
    if missing:
        header = UI_STRINGS["missing_items_header"].get(lang, UI_STRINGS["missing_items_header"]["en"])
        lines.append(f"\n{header}")
        for m in missing:
            hint = m["hint_translated"] if lang != "en" and m["hint_translated"] else m["hint"]
            lines.append(f"  [{m['regulation_no']}] {hint}")

    return "\n".join(lines)


# ── Standalone demo ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    sample_text = """
    CHAKLI SNACKS
    Ingredients: Rice flour, vegetable oil, salt.
    Net Qty: 200g
    Manufactured by: Sunita Home Foods, Kopargaon, Maharashtra - 423601
    MFD: 17/11/2026   Best Before: 17/02/2027
    FSSAI Lic. No.: 11417030000133
    Veg  [GREEN DOT]
    Store in a cool, dry place.
    """

    for lang in ["en", "mr", "hi"]:
        print(f"\n{'='*60}")
        print(f"Language: {lang}")
        print("=" * 60)
        output = check_label_multilang(sample_text, lang=lang)
        print(format_multilang_table(output))
