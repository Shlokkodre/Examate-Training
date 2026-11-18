"""
Day 11 — PDF Parser for HealthLabelCheck
Extracts regulation text from FSSAI labelling PDF documents using pypdf.

Responsibilities:
- Open a PDF, extract full text page by page
- Split text into per-regulation sections by detecting "Regulation X.Y" headers
- Return structured dicts with regulation_no, raw_text, page_number, source_doc

Usage:
    from app.pdf_parser import parse_pdf
    sections = parse_pdf("data/raw/FSSAI_Sample_Labelling.pdf")
    for s in sections:
        print(s["regulation_no"], s["raw_text"][:80])
"""

import os
import re
from typing import List, Dict

from pypdf import PdfReader


# Regex that matches "Regulation 5.1", "Regulation 6.2", etc.
REG_HEADER_RE = re.compile(
    r"Regulation\s+(\d+\.\d+)\s*[—\-–]?\s*([^\n]{3,80})", re.IGNORECASE
)

# Fields we try to extract per section
SECTION_FIELDS = ["Applies to", "Requirements", "Exemption"]


# ── low-level extraction ──────────────────────────────────────────────────────

def extract_text_from_pdf(pdf_path: str) -> List[Dict]:
    """
    Extract text from every page of a PDF.

    Returns a list of dicts:
        { "page": int (1-indexed), "text": str }
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    reader = PdfReader(pdf_path)
    pages = []
    for i, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        pages.append({"page": i, "text": text})
    return pages


def merge_pages(pages: List[Dict]) -> str:
    """Concatenate all page texts with page boundary markers."""
    parts = []
    for p in pages:
        parts.append(f"\n[PAGE {p['page']}]\n{p['text']}")
    return "\n".join(parts)


# ── section splitter ──────────────────────────────────────────────────────────

def split_into_sections(full_text: str) -> List[Dict]:
    """
    Split the full document text into per-regulation sections.

    Each section is a dict with:
        regulation_no : str   e.g. "5.1"
        title         : str   e.g. "Name of Food"
        raw_text      : str   the text block belonging to this regulation
        page          : int   page where the regulation header was found
    """
    # Find all regulation headers and their positions
    matches = list(REG_HEADER_RE.finditer(full_text))
    if not matches:
        return []

    sections = []
    for i, match in enumerate(matches):
        reg_no = match.group(1).strip()
        title  = match.group(2).strip()

        # Infer page number from the nearest preceding [PAGE n] marker
        page_match = re.findall(r"\[PAGE (\d+)\]", full_text[:match.start()])
        page = int(page_match[-1]) if page_match else 1

        # Text runs from this match to the start of the next match (or EOF)
        start = match.start()
        end   = matches[i + 1].start() if i + 1 < len(matches) else len(full_text)
        raw   = full_text[start:end].strip()

        sections.append({
            "regulation_no": reg_no,
            "title":         title,
            "raw_text":      raw,
            "page":          page,
        })

    return sections


# ── field extractor ───────────────────────────────────────────────────────────

def extract_fields_from_section(section: Dict) -> Dict:
    """
    Try to pull labelled fields (Applies to, Requirements, Exemption) out of
    a regulation section's raw text.  Falls back to the full raw text for
    details when the labels are not found.
    """
    text = section["raw_text"]

    def grab_field(label: str) -> str:
        """Extract text that follows 'label:' up to the next field label or end."""
        pattern = re.compile(
            rf"{re.escape(label)}:\s*(.+?)(?=(?:{'|'.join(SECTION_FIELDS)}):|$)",
            re.IGNORECASE | re.DOTALL,
        )
        m = pattern.search(text)
        if m:
            return re.sub(r"\s+", " ", m.group(1)).strip()
        return ""

    applies_to = grab_field("Applies to")
    details    = grab_field("Requirements")
    exemption  = grab_field("Exemption")

    # Fallback: use the first 400 chars after the header as details
    if not details:
        # Strip the first line (the header itself) and use the rest
        lines = text.split("\n")
        details = " ".join(lines[1:4]).strip()
        details = re.sub(r"\s+", " ", details)[:400]

    return {
        "regulation_no": section["regulation_no"],
        "requirement":   section["title"],
        "applies_to":    applies_to or "All packaged foods",
        "details":       details,
        "exemption":     exemption or "None",
        "page":          section["page"],
    }


# ── public API ────────────────────────────────────────────────────────────────

def parse_pdf(pdf_path: str) -> List[Dict]:
    """
    Full pipeline: open PDF → extract text → split into sections →
    extract fields per section.

    Returns a list of regulation dicts ready for ingest_from_list().
    Each dict has: regulation_no, requirement, applies_to, details,
                   exemption, source_doc, page.
    """
    source_doc = os.path.basename(pdf_path)

    pages    = extract_text_from_pdf(pdf_path)
    combined = merge_pages(pages)
    sections = split_into_sections(combined)

    records = []
    for section in sections:
        rec = extract_fields_from_section(section)
        rec["source_doc"] = source_doc
        records.append(rec)

    return records


def parse_pdf_summary(pdf_path: str) -> Dict:
    """Return high-level stats about a PDF without returning all records."""
    pages = extract_text_from_pdf(pdf_path)
    total_chars = sum(len(p["text"]) for p in pages)
    combined = merge_pages(pages)
    sections = split_into_sections(combined)
    reg_numbers = [s["regulation_no"] for s in sections]

    return {
        "pdf_path":        pdf_path,
        "total_pages":     len(pages),
        "total_chars":     total_chars,
        "sections_found":  len(sections),
        "regulation_nos":  reg_numbers,
    }


# ── standalone test ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    import json

    PDF = "data/raw/FSSAI_Sample_Labelling.pdf"

    print(f"Parsing: {PDF}\n")
    summary = parse_pdf_summary(PDF)
    print(f"Pages         : {summary['total_pages']}")
    print(f"Total chars   : {summary['total_chars']:,}")
    print(f"Sections found: {summary['sections_found']}")
    print(f"Regulations   : {', '.join(summary['regulation_nos'])}")

    print("\n--- First 3 parsed records ---")
    records = parse_pdf(PDF)
    for rec in records[:3]:
        print(json.dumps(rec, indent=2, ensure_ascii=False))
