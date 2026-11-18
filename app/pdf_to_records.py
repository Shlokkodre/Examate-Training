"""
Day 11 — PDF-to-Records pipeline for HealthLabelCheck
Bridges pdf_parser.py output → clean records → data/records.json

This replaces the manual KNOWN_REGULATIONS table in ingest.py with
records parsed from the actual PDF, while keeping the curated table
as a merge/validation source.

Usage:
    python -m app.pdf_to_records
    python -m app.pdf_to_records --pdf data/raw/FSSAI_Sample_Labelling.pdf
"""

import argparse
import json
import os
import re
from typing import List, Dict, Tuple

from app.pdf_parser import parse_pdf, parse_pdf_summary
from app.ingest import KNOWN_REGULATIONS, clean_text, validate_record, save_records


# ── merging strategy ──────────────────────────────────────────────────────────

def merge_with_curated(pdf_records: List[Dict]) -> List[Dict]:
    """
    For each regulation found in the PDF:
      - Use the PDF-parsed applies_to / details / exemption if they are
        substantial (> 20 chars), otherwise fall back to the curated value.
      - Add any regulations from KNOWN_REGULATIONS that the PDF missed.

    This gives us the best of both worlds: real PDF provenance where the
    text was machine-readable, curated text as a safety net.
    """
    # Index PDF records by regulation number
    pdf_index: Dict[str, Dict] = {r["regulation_no"]: r for r in pdf_records}

    merged = []
    for reg_no, (req, applies, details, exemption) in KNOWN_REGULATIONS.items():
        pdf = pdf_index.get(reg_no, {})

        def pick(pdf_val: str, fallback: str, min_len: int = 20) -> str:
            v = clean_text(pdf_val or "")
            return v if len(v) >= min_len else fallback

        merged.append({
            "regulation_no": reg_no,
            "requirement":   pdf.get("requirement") or req,
            "applies_to":    pick(pdf.get("applies_to", ""), applies),
            "details":       pick(pdf.get("details",    ""), details),
            "exemption":     pick(pdf.get("exemption",  ""), exemption, min_len=5),
            "source_doc":    pdf.get("source_doc", "FSSAI_Labelling_Compendium_2022.pdf"),
        })

    return merged


def validate_and_clean(records: List[Dict]) -> Tuple[List[Dict], List[str]]:
    """Run validate_record + clean_text on every record."""
    clean, errors = [], []
    for rec in records:
        ok, err = validate_record(rec)
        if not ok:
            errors.append(f"{rec.get('regulation_no','?')}: {err}")
            continue
        clean.append({k: clean_text(v) for k, v in rec.items()})
    return clean, errors


# ── main pipeline ─────────────────────────────────────────────────────────────

def run_pdf_pipeline(
    pdf_path: str = "data/raw/FSSAI_Sample_Labelling.pdf",
    output_path: str = "data/records.json",
) -> Tuple[List[Dict], List[str]]:
    """
    1. Print PDF summary
    2. Parse regulation sections from PDF text
    3. Merge with curated table (PDF values preferred when substantial)
    4. Validate and clean
    5. Save to output_path
    """
    print("=" * 60)
    print("HealthLabelCheck — Day 11 PDF Pipeline")
    print("=" * 60)

    # Step 1: summary
    if os.path.exists(pdf_path):
        summary = parse_pdf_summary(pdf_path)
        print(f"\nPDF       : {summary['pdf_path']}")
        print(f"Pages     : {summary['total_pages']}")
        print(f"Chars     : {summary['total_chars']:,}")
        print(f"Sections  : {summary['sections_found']}")
        print(f"Found regs: {', '.join(summary['regulation_nos'])}")
    else:
        print(f"\nPDF not found: {pdf_path}")
        print("Run: python data/make_sample_pdf.py")
        return [], [f"PDF not found: {pdf_path}"]

    # Step 2: parse
    print("\n[1] Parsing PDF sections …")
    pdf_records = parse_pdf(pdf_path)
    print(f"    {len(pdf_records)} sections extracted from PDF")

    # Step 3: merge
    print("[2] Merging with curated regulation table …")
    merged = merge_with_curated(pdf_records)
    print(f"    {len(merged)} records after merge")

    # Step 4: validate
    print("[3] Validating and cleaning …")
    clean, errors = validate_and_clean(merged)
    if errors:
        print(f"    Warnings: {len(errors)}")
        for e in errors:
            print(f"      - {e}")
    else:
        print(f"    All {len(clean)} records valid")

    # Step 5: save
    print(f"[4] Saving to {output_path} …")
    ok, msg = save_records(clean, output_path)
    print(f"    {msg}")

    return clean, errors


# ── PDF coverage report ───────────────────────────────────────────────────────

def coverage_report(pdf_records: List[Dict]) -> None:
    """Print a table showing which regulations were found in the PDF."""
    found = {r["regulation_no"] for r in pdf_records}
    all_regs = list(KNOWN_REGULATIONS.keys())

    print("\nRegulation Coverage Report")
    print(f"{'Reg':>6}  {'Found in PDF':^14}  {'Requirement'}")
    print("-" * 55)
    for reg_no in all_regs:
        req = KNOWN_REGULATIONS[reg_no][0]
        status = "YES" if reg_no in found else "no"
        print(f"{reg_no:>6}  {status:^14}  {req}")

    hit_rate = len(found) / len(all_regs) * 100
    print(f"\nCoverage: {len(found)}/{len(all_regs)} ({hit_rate:.0f}%)")


# ── entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse FSSAI PDF → records.json")
    parser.add_argument(
        "--pdf", default="data/raw/FSSAI_Sample_Labelling.pdf",
        help="Path to FSSAI labelling PDF"
    )
    parser.add_argument(
        "--output", default="data/records.json",
        help="Output path for records.json"
    )
    parser.add_argument(
        "--report", action="store_true",
        help="Print coverage report"
    )
    args = parser.parse_args()

    records, errors = run_pdf_pipeline(args.pdf, args.output)

    if args.report and records:
        from app.pdf_parser import parse_pdf as _parse
        pdf_recs = _parse(args.pdf)
        coverage_report(pdf_recs)

    print(f"\nDone. {len(records)} records, {len(errors)} errors.")
