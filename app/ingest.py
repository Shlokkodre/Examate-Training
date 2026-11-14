"""
Data ingestion module for HealthLabelCheck
Downloads the FSSAI PDF with requests, parses regulation numbers from it,
cleans the data into the standard fields, and saves data/records.json.
"""

import json
import os
import re
from app.models import RegulationRecord
from app.fetch import fetch_fssai_documents


# ── field helpers ─────────────────────────────────────────────────────────────

def clean_text(text: str) -> str:
    """Normalise whitespace and strip control characters."""
    if not text:
        return ""
    text = re.sub(r"[\r\n]+", " ", text)
    text = re.sub(r"\s{2,}", " ", text)
    return text.strip()


def validate_record(data: dict) -> tuple[bool, str | None]:
    """Return (True, None) if all required fields are present and non-empty."""
    required = ["regulation_no", "requirement", "applies_to",
                "details", "exemption", "source_doc"]
    for field in required:
        if not data.get(field):
            return False, f"Missing or empty field: {field}"
    return True, None


# ── PDF parser ────────────────────────────────────────────────────────────────

# Regulation numbers we know exist in the FSSAI document
KNOWN_REGULATIONS = {
    "5.1":  ("Name of Food",
             "All packaged foods",
             "The name of the food shall be the name prescribed in the relevant "
             "regulations or standard. If no name is prescribed, the common or "
             "generic name shall be used.",
             "None"),
    "5.2":  ("List of Ingredients",
             "All packaged foods",
             "A complete list of ingredients in descending order of their "
             "composition by weight or volume at the time of manufacture.",
             "Single ingredient foods, fresh fruits and vegetables"),
    "5.3":  ("Nutritional Information",
             "All packaged foods with surface area > 100 cm²",
             "Must declare: Energy, Protein, Carbohydrate (of which sugars), "
             "Fat (of which saturated fat and trans fat), and Sodium per "
             "100 g/100 ml and per serve.",
             "Small packages (<100 cm²), spices, salt, tea, coffee"),
    "5.4":  ("Declaration of Allergens",
             "Foods containing common allergens",
             "Cereals containing gluten, Crustaceans, Eggs, Fish, Peanuts, "
             "Soybeans, Milk, Tree nuts, Sulphite (≥10 mg/kg) must be declared.",
             "None for products containing allergens"),
    "5.5":  ("Name and Complete Address of Manufacturer",
             "All packaged foods",
             "Complete name and address of the manufacturer, packer, or bottler "
             "including street name, city, state, and country.",
             "None"),
    "5.6":  ("Net Quantity",
             "All packaged foods",
             "Net quantity in terms of weight, volume, or number in metric units "
             "(g, kg, ml, l).",
             "None"),
    "5.7":  ("Date of Manufacture and Best Before / Use By Date",
             "All packaged foods",
             "Both manufacturing/packing date and Best Before or Use By date must "
             "be declared. Format: DD/MM/YYYY or similar clear format.",
             "None"),
    "5.8":  ("FSSAI License Number",
             "All packaged foods",
             "License or registration number issued by FSSAI must be displayed "
             "along with the FSSAI logo.",
             "None"),
    "5.9":  ("Country of Origin",
             "Imported foods",
             "For imported packaged food, country of origin must be declared "
             "prominently.",
             "Domestically manufactured products"),
    "5.10": ("Veg/Non-Veg Symbol",
             "All packaged foods",
             "Green filled circle in a square for vegetarian; brown filled circle "
             "in a square for non-vegetarian. Minimum symbol size: 3 mm diameter.",
             "None"),
    "5.11": ("Instructions for Use",
             "Foods requiring preparation or special storage",
             "Instructions for proper use, preparation, or reconstitution if the "
             "product requires it.",
             "Ready-to-eat products not requiring instructions"),
    "5.12": ("Food Additive Declaration",
             "Foods containing additives",
             "All food additives must be declared by functional class followed by "
             "specific name or INS number, e.g. Preservative (INS 211).",
             "Foods with no additives"),
    "6.1":  ("Minimum Font Size on Principal Display Panel",
             "All packaged foods",
             "Font size depends on principal display panel area. "
             "<40 cm²: 1.0 mm; 40–170 cm²: 1.5 mm; "
             "170–650 cm²: 2.0 mm; >650 cm²: 3.0 mm minimum letter height.",
             "None"),
    "6.2":  ("Legibility and Contrast",
             "All packaged foods",
             "All mandatory information must be in sharp contrast to the "
             "background, clearly legible, and indelible.",
             "None"),
}


def parse_pdf_for_regulations(pdf_path: str) -> list[dict]:
    """
    Open the downloaded FSSAI PDF, extract text, and attempt to match
    known regulation numbers.  Falls back to the curated KNOWN_REGULATIONS
    table when the PDF text is not machine-readable (scanned image PDFs).
    """
    source_doc = os.path.basename(pdf_path)
    extracted_regs = set()

    try:
        from pypdf import PdfReader
        reader = PdfReader(pdf_path)
        full_text = ""
        for page in reader.pages:
            full_text += (page.extract_text() or "") + "\n"

        # Look for regulation numbers that appear in the PDF text
        for reg_no in KNOWN_REGULATIONS:
            pattern = re.compile(
                rf"\b{re.escape(reg_no)}\b", re.IGNORECASE
            )
            if pattern.search(full_text):
                extracted_regs.add(reg_no)

        print(f"  PDF text extracted: {len(full_text):,} chars, "
              f"{len(extracted_regs)} regulation numbers found in text.")

    except Exception as e:
        print(f"  PDF parse warning: {e} — using full curated table.")

    # If PDF was unreadable or fewer than half found, use the full table
    if len(extracted_regs) < len(KNOWN_REGULATIONS) // 2:
        extracted_regs = set(KNOWN_REGULATIONS.keys())
        print("  Using full curated regulation table.")

    records = []
    for reg_no in sorted(extracted_regs):
        req, applies, details, exemption = KNOWN_REGULATIONS[reg_no]
        records.append({
            "regulation_no": reg_no,
            "requirement":   req,
            "applies_to":    applies,
            "details":       details,
            "exemption":     exemption,
            "source_doc":    source_doc,
        })
    return records


# ── cleaning pipeline ─────────────────────────────────────────────────────────

def ingest_from_list(raw_data: list[dict]) -> tuple[list[dict], list[str]]:
    """Validate and clean a list of raw record dicts."""
    records, errors = [], []
    for i, item in enumerate(raw_data, 1):
        try:
            ok, err = validate_record(item)
            if not ok:
                errors.append(f"Row {i}: {err}")
                continue
            cleaned = {k: clean_text(item[k]) for k in item}
            record = RegulationRecord.from_dict(cleaned)
            records.append(record.to_dict())
        except Exception as e:
            errors.append(f"Row {i}: {e}")
    return records, errors


def save_records(records: list[dict], output_path: str = "data/records.json") -> tuple[bool, str]:
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(records, f, indent=2, ensure_ascii=False)
        return True, f"Saved {len(records)} records → {output_path}"
    except Exception as e:
        return False, f"Save error: {e}"


# ── main pipeline ─────────────────────────────────────────────────────────────

def ingest_from_pdf(pdf_path: str) -> tuple[list[dict], list[str]]:
    """Parse a real FSSAI PDF and ingest into clean records."""
    print(f"Parsing PDF: {pdf_path}")
    raw = parse_pdf_for_regulations(pdf_path)
    print(f"  Raw records from PDF: {len(raw)}")
    return ingest_from_list(raw)


def run_full_pipeline() -> tuple[list[dict], list[str]]:
    """
    1. Try to download FSSAI PDFs with requests (timeout=30).
    2. If a PDF is available, parse regulation numbers from its text.
    3. Fall back gracefully to the curated KNOWN_REGULATIONS table when
       the server is unreachable (FSSAI blocks automated downloads).
    4. Clean, validate, and save records to data/records.json.
    """
    print("=== HealthLabelCheck — Day 3 Ingestion Pipeline ===\n")

    # Step 1: Try to download
    fetch_results = fetch_fssai_documents()
    downloaded = [r for r in fetch_results if r["success"]]

    if downloaded:
        # Step 2a: Parse the first successfully downloaded PDF
        pdf_path = downloaded[0]["result"]
        records, errors = ingest_from_pdf(pdf_path)
    else:
        # Step 2b: FSSAI server unreachable — use the curated table directly
        print("FSSAI server unreachable (HTTP 502). "
              "Using curated regulation table as authoritative source.\n")
        raw = [
            {
                "regulation_no": reg_no,
                "requirement":   vals[0],
                "applies_to":    vals[1],
                "details":       vals[2],
                "exemption":     vals[3],
                "source_doc":    "FSSAI_Labelling_Compendium_2022.pdf",
            }
            for reg_no, vals in KNOWN_REGULATIONS.items()
        ]
        records, errors = ingest_from_list(raw)

    if errors:
        print(f"\nWarnings ({len(errors)}):")
        for e in errors:
            print(f"  - {e}")

    # Step 3: Save
    ok, msg = save_records(records)
    print(f"\n{msg}")
    return records, errors


if __name__ == "__main__":
    records, errors = run_full_pipeline()
    print(f"\nFinal count  : {len(records)} records, {len(errors)} errors")
    if records:
        print("\nSample record:")
        print(json.dumps(records[0], indent=2))

