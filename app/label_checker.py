"""
Day 12 — Label checker for HealthLabelCheck
Matches OCR-extracted text from a label image against the 14 mandatory
FSSAI regulations and returns a green/red compliance table.

Usage:
    from app.label_checker import check_label
    results = check_label(ocr_text)
"""

import re
from typing import List, Dict


# ── Detection rules ───────────────────────────────────────────────────────────
# Each rule defines:
#   regulation_no : str
#   requirement   : str   (human-readable name)
#   mandatory     : bool  (False = conditional — counted separately)
#   patterns      : list of regex patterns; ANY match → present
#   hint          : what the user should add if missing

RULES = [
    {
        "regulation_no": "5.1",
        "requirement":   "Name of Food",
        "mandatory":     True,
        "patterns": [
            r"\b(chakli|laddoo|laddu|snack|biscuit|namkeen|farsan|mixture|"
            r"chips|wafer|murukku|mixture|chivda|poha|mathri)\b",
        ],
        "hint": "Print the common/generic name of your food product.",
    },
    {
        "regulation_no": "5.2",
        "requirement":   "List of Ingredients",
        "mandatory":     True,
        "patterns": [
            r"\bingredient",
            r"\bcontains\b.*\b(flour|oil|salt|sugar|spice)",
        ],
        "hint": "List all ingredients in descending order by weight.",
    },
    {
        "regulation_no": "5.3",
        "requirement":   "Nutritional Information",
        "mandatory":     True,
        "patterns": [
            r"\bnutrit",
            r"\benergy\b",
            r"\bprotein\b.*\bcarb",
            r"\bper\s*100\s*g",
            r"\bkcal\b",
        ],
        "hint": "Add a nutrition table: Energy, Protein, Carbs, Fat, Sodium per 100 g.",
    },
    {
        "regulation_no": "5.4",
        "requirement":   "Allergen Declaration",
        "mandatory":     False,  # conditional — only if product contains allergens
        "patterns": [
            r"\ballergen",
            r"\bcontains\b.*\b(peanut|groundnut|sesame|milk|egg|soy|wheat|gluten|tree nut|fish|crustacean)",
            r"\bmay contain\b",
        ],
        "hint": "If your product contains allergens, declare them: 'Contains: [allergen]'.",
    },
    {
        "regulation_no": "5.5",
        "requirement":   "Manufacturer Name & Address",
        "mandatory":     True,
        "patterns": [
            r"\bmanufactured\s+by\b",
            r"\bmfr\b",
            r"\bpacked\s+by\b",
            r"\b(nagar|road|street|colony|dist|pin|maharashtra|gujarat|karnataka|"
            r"delhi|mumbai|pune|bangalore|hyderabad|chennai)\b",
        ],
        "hint": "Print full manufacturer name and address (street, city, state, pin code).",
    },
    {
        "regulation_no": "5.6",
        "requirement":   "Net Quantity",
        "mandatory":     True,
        "patterns": [
            r"\bnet\s*(qty|quantity|wt|weight)\b",
            r"\b\d+\s*(g|kg|gm|gram|ml|l|litre|liter)\b",
        ],
        "hint": "Print net quantity in metric units, e.g. 'Net Qty: 200g'.",
    },
    {
        "regulation_no": "5.7",
        "requirement":   "Date of Manufacture & Best Before",
        "mandatory":     True,
        "patterns": [
            r"\b(mfd|mfg|manufactured|packed)\b.*\d{2}[\/\-\.]\d{2}[\/\-\.]\d{4}",
            r"\bbest\s+before\b",
            r"\buse\s+by\b",
            r"\bexpiry\b",
            r"\bexp\b.*\d",
            r"\d{2}[\/\-]\d{2}[\/\-]\d{4}",
        ],
        "hint": "Print MFD date and Best Before date in DD/MM/YYYY format.",
    },
    {
        "regulation_no": "5.8",
        "requirement":   "FSSAI License Number",
        "mandatory":     True,
        "patterns": [
            r"\bfssai\b",
            r"\blic\.?\s*no\.?\s*[:\-]?\s*\d{5,}",
            r"\bregistration\s*no\b",
            r"\b\d{14}\b",   # 14-digit FSSAI number
        ],
        "hint": "Print 'FSSAI Lic. No.: XXXXXXXXXXXXXX' with the FSSAI logo.",
    },
    {
        "regulation_no": "5.9",
        "requirement":   "Country of Origin",
        "mandatory":     False,  # mandatory only for imports
        "patterns": [
            r"\bcountry\s+of\s+origin\b",
            r"\bproduct\s+of\s+(india|china|usa|uk)\b",
            r"\bmade\s+in\b",
        ],
        "hint": "For imported products, print 'Country of Origin: [country]'.",
    },
    {
        "regulation_no": "5.10",
        "requirement":   "Veg / Non-Veg Symbol",
        "mandatory":     True,
        "patterns": [
            r"\bveg\b",
            r"\bnon.?veg\b",
            r"\bvegetarian\b",
            r"green\s+dot",
            r"\[green",
        ],
        "hint": "Display the green (veg) or brown (non-veg) filled circle in a square, min 3 mm.",
    },
    {
        "regulation_no": "5.11",
        "requirement":   "Storage / Usage Instructions",
        "mandatory":     False,
        "patterns": [
            r"\bstore\b",
            r"\bstorage\b",
            r"\bkeep\s+(in|away|cool|dry|refrigerat)",
            r"\bserving\s+suggestion\b",
            r"\bpreparat",
        ],
        "hint": "If special storage is needed, print instructions (e.g. 'Store in a cool, dry place').",
    },
    {
        "regulation_no": "5.12",
        "requirement":   "Food Additive Declaration",
        "mandatory":     False,
        "patterns": [
            r"\b(ins\s*\d{3})\b",
            r"\bpreservative\b",
            r"\bantioxidant\b",
            r"\bcolou?r\b.*\bins\b",
            r"\bflavou?r\b.*\b(natural|artificial|added)\b",
            r"\bemulsifier\b",
            r"\bstabiliser\b",
        ],
        "hint": "If you use additives, declare them: e.g. 'Preservative (INS 211)'.",
    },
    {
        "regulation_no": "6.1",
        "requirement":   "Minimum Font Size (Reg 6.1)",
        "mandatory":     True,
        "patterns": [
            # Can't verify font size from OCR text — treat as present if
            # the label text is legible (i.e. OCR found ≥50 characters)
            r"[\s\S]{50,}",
        ],
        "hint": "Ensure mandatory text is printed at minimum 1.5 mm height for a 96 cm² panel.",
    },
    {
        "regulation_no": "6.2",
        "requirement":   "Legibility & Contrast",
        "mandatory":     True,
        "patterns": [
            # Same proxy: OCR succeeded → text is legible enough
            r"[\s\S]{50,}",
        ],
        "hint": "Print all mandatory info in a colour that contrasts with the background.",
    },
]


# ── Core checker ──────────────────────────────────────────────────────────────

def check_label(ocr_text: str) -> List[Dict]:
    """
    Match OCR text against each FSSAI regulation rule.

    Returns a list of dicts, one per regulation:
        regulation_no : str
        requirement   : str
        mandatory     : bool
        status        : "present" | "missing"
        hint          : str  (what to add if missing)
    """
    text_lower = ocr_text.lower()
    results = []

    for rule in RULES:
        found = any(
            re.search(pattern, text_lower, re.IGNORECASE)
            for pattern in rule["patterns"]
        )
        results.append({
            "regulation_no": rule["regulation_no"],
            "requirement":   rule["requirement"],
            "mandatory":     rule["mandatory"],
            "status":        "present" if found else "missing",
            "hint":          rule["hint"] if not found else "",
        })

    return results


def checklist_summary(results: List[Dict]) -> Dict:
    """
    Compute summary statistics from check_label() output.

    Returns:
        total, mandatory_total, mandatory_present, mandatory_missing,
        conditional_present, compliance_pct
    """
    mandatory   = [r for r in results if r["mandatory"]]
    conditional = [r for r in results if not r["mandatory"]]

    mand_present = sum(1 for r in mandatory   if r["status"] == "present")
    cond_present = sum(1 for r in conditional if r["status"] == "present")

    pct = round(mand_present / len(mandatory) * 100) if mandatory else 0

    return {
        "total":               len(results),
        "mandatory_total":     len(mandatory),
        "mandatory_present":   mand_present,
        "mandatory_missing":   len(mandatory) - mand_present,
        "conditional_present": cond_present,
        "compliance_pct":      pct,
    }


def format_checklist_table(results: List[Dict]) -> str:
    """Return a plain-text compliance table for CLI / logging."""
    lines = [
        f"{'Reg':>6}  {'Status':^9}  {'Req/Mandatory':^6}  Requirement",
        "-" * 70,
    ]
    for r in results:
        icon   = "PASS" if r["status"] == "present" else "FAIL"
        req    = "YES"  if r["mandatory"]             else "cond"
        lines.append(f"{r['regulation_no']:>6}  {icon:^9}  {req:^6}  {r['requirement']}")
    return "\n".join(lines)


# ── Standalone test ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    import json

    sample_text = """
    CHAKLI SNACKS
    Ingredients: Rice flour, Bengal gram flour, vegetable oil, sesame seeds, salt, spices.
    Net Qty: 200g
    Manufactured by: Sunita Home Foods, 12 Ganesh Nagar, Kopargaon, Maharashtra - 423601
    MFD: 17/11/2026   Best Before: 17/02/2027
    FSSAI Lic. No.: 11417030000133
    Veg  [GREEN DOT]
    Allergen Info: Contains sesame seeds.
    Store in a cool, dry place.
    """

    results = check_label(sample_text)
    print(format_checklist_table(results))
    print()
    summary = checklist_summary(results)
    print(f"Mandatory compliance: {summary['mandatory_present']}/{summary['mandatory_total']} ({summary['compliance_pct']}%)")
    print(f"Conditional present : {summary['conditional_present']}")

    missing = [r for r in results if r["status"] == "missing"]
    if missing:
        print("\nMissing items:")
        for r in missing:
            print(f"  [{r['regulation_no']}] {r['requirement']}: {r['hint']}")
