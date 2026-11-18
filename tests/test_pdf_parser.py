"""
Day 11 — Unit tests for app/pdf_parser.py and app/pdf_to_records.py

Run from repo root:
    python -m pytest tests/test_pdf_parser.py -v
"""

import os
import sys
import json
import pytest

# Ensure repo root is on the path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.pdf_parser import (
    extract_text_from_pdf,
    split_into_sections,
    extract_fields_from_section,
    parse_pdf,
    parse_pdf_summary,
    merge_pages,
)
from app.pdf_to_records import (
    merge_with_curated,
    validate_and_clean,
    run_pdf_pipeline,
)

PDF_PATH = "data/raw/FSSAI_Sample_Labelling.pdf"


# ── fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def sample_pdf():
    """Generate the sample PDF if it doesn't exist, return its path."""
    if not os.path.exists(PDF_PATH):
        from data.make_sample_pdf import build_pdf
        build_pdf(PDF_PATH)
    assert os.path.exists(PDF_PATH), f"PDF not created at {PDF_PATH}"
    return PDF_PATH


@pytest.fixture(scope="module")
def parsed_records(sample_pdf):
    return parse_pdf(sample_pdf)


@pytest.fixture(scope="module")
def pdf_summary(sample_pdf):
    return parse_pdf_summary(sample_pdf)


# ── pdf_parser tests ──────────────────────────────────────────────────────────

class TestExtractText:
    def test_returns_pages_list(self, sample_pdf):
        pages = extract_text_from_pdf(sample_pdf)
        assert isinstance(pages, list)
        assert len(pages) >= 1

    def test_pages_have_text_and_number(self, sample_pdf):
        pages = extract_text_from_pdf(sample_pdf)
        for p in pages:
            assert "page" in p
            assert "text" in p
            assert isinstance(p["page"], int)
            assert p["page"] >= 1

    def test_total_text_is_substantial(self, sample_pdf):
        pages = extract_text_from_pdf(sample_pdf)
        total = sum(len(p["text"]) for p in pages)
        assert total > 500, f"Expected >500 chars, got {total}"

    def test_missing_pdf_raises(self):
        with pytest.raises(FileNotFoundError):
            extract_text_from_pdf("data/raw/does_not_exist.pdf")


class TestSplitSections:
    def test_finds_regulation_sections(self, sample_pdf):
        pages = extract_text_from_pdf(sample_pdf)
        combined = merge_pages(pages)
        sections = split_into_sections(combined)
        assert len(sections) >= 10, f"Expected >=10 sections, got {len(sections)}"

    def test_sections_have_required_keys(self, sample_pdf):
        pages = extract_text_from_pdf(sample_pdf)
        combined = merge_pages(pages)
        sections = split_into_sections(combined)
        for s in sections:
            assert "regulation_no" in s
            assert "title" in s
            assert "raw_text" in s
            assert "page" in s

    def test_regulation_numbers_are_valid(self, sample_pdf):
        pages = extract_text_from_pdf(sample_pdf)
        combined = merge_pages(pages)
        sections = split_into_sections(combined)
        import re
        for s in sections:
            assert re.match(r"^\d+\.\d+$", s["regulation_no"]), \
                f"Bad reg_no: {s['regulation_no']}"

    def test_no_duplicate_regulation_numbers(self, sample_pdf):
        pages = extract_text_from_pdf(sample_pdf)
        combined = merge_pages(pages)
        sections = split_into_sections(combined)
        reg_nos = [s["regulation_no"] for s in sections]
        assert len(reg_nos) == len(set(reg_nos)), "Duplicate regulation numbers found"


class TestParsePDF:
    def test_returns_14_regulations(self, parsed_records):
        assert len(parsed_records) == 14, \
            f"Expected 14 records, got {len(parsed_records)}"

    def test_all_expected_regs_present(self, parsed_records):
        expected = {"5.1","5.2","5.3","5.4","5.5","5.6","5.7",
                    "5.8","5.9","5.10","5.11","5.12","6.1","6.2"}
        found = {r["regulation_no"] for r in parsed_records}
        missing = expected - found
        assert not missing, f"Missing regulations: {missing}"

    def test_records_have_all_fields(self, parsed_records):
        required_fields = {"regulation_no","requirement","applies_to",
                           "details","exemption","source_doc"}
        for rec in parsed_records:
            assert required_fields.issubset(rec.keys()), \
                f"Missing fields in {rec.get('regulation_no')}: {required_fields - rec.keys()}"

    def test_details_are_non_empty(self, parsed_records):
        for rec in parsed_records:
            assert len(rec["details"]) >= 10, \
                f"Short details for {rec['regulation_no']}: '{rec['details']}'"

    def test_source_doc_is_set(self, parsed_records):
        for rec in parsed_records:
            assert rec["source_doc"], f"Empty source_doc for {rec['regulation_no']}"

    def test_veg_symbol_regulation(self, parsed_records):
        rec = next((r for r in parsed_records if r["regulation_no"] == "5.10"), None)
        assert rec is not None
        assert "veg" in rec["details"].lower() or "circle" in rec["details"].lower()

    def test_font_size_regulation(self, parsed_records):
        rec = next((r for r in parsed_records if r["regulation_no"] == "6.1"), None)
        assert rec is not None
        # Should mention mm or font
        assert any(kw in rec["details"].lower() for kw in ["mm", "font", "letter", "1.0", "1.5"])

    def test_allergen_regulation(self, parsed_records):
        rec = next((r for r in parsed_records if r["regulation_no"] == "5.4"), None)
        assert rec is not None
        assert any(kw in rec["details"].lower() for kw in ["allergen", "gluten", "peanut", "milk"])


class TestParsePDFSummary:
    def test_summary_keys(self, pdf_summary):
        for key in ["pdf_path", "total_pages", "total_chars",
                    "sections_found", "regulation_nos"]:
            assert key in pdf_summary

    def test_summary_counts(self, pdf_summary):
        assert pdf_summary["total_pages"] >= 1
        assert pdf_summary["total_chars"] > 500
        assert pdf_summary["sections_found"] >= 10
        assert len(pdf_summary["regulation_nos"]) >= 10


# ── pdf_to_records tests ─────────────────────────────────────────────────────

class TestMergeWithCurated:
    def test_always_returns_14_records(self, parsed_records):
        merged = merge_with_curated(parsed_records)
        assert len(merged) == 14

    def test_all_regulation_nos_present(self, parsed_records):
        merged = merge_with_curated(parsed_records)
        expected = {"5.1","5.2","5.3","5.4","5.5","5.6","5.7",
                    "5.8","5.9","5.10","5.11","5.12","6.1","6.2"}
        found = {r["regulation_no"] for r in merged}
        assert found == expected

    def test_merge_on_empty_pdf_records(self):
        """When PDF finds nothing, should still return 14 curated records."""
        merged = merge_with_curated([])
        assert len(merged) == 14

    def test_details_non_empty_after_merge(self, parsed_records):
        merged = merge_with_curated(parsed_records)
        for rec in merged:
            assert len(rec["details"]) > 10, \
                f"Empty details after merge for {rec['regulation_no']}"


class TestValidateAndClean:
    def test_valid_records_pass(self, parsed_records):
        merged = merge_with_curated(parsed_records)
        clean, errors = validate_and_clean(merged)
        assert len(errors) == 0, f"Unexpected errors: {errors}"
        assert len(clean) == 14

    def test_missing_field_causes_error(self):
        bad = [{"regulation_no": "5.1", "requirement": "Name"}]  # missing fields
        _, errors = validate_and_clean(bad)
        assert len(errors) >= 1

    def test_whitespace_is_normalised(self):
        rec = {
            "regulation_no": "5.1",
            "requirement":   "Name  of  Food",
            "applies_to":    "All  packaged  foods",
            "details":       "The  name  shall  be  prescribed.",
            "exemption":     "None",
            "source_doc":    "FSSAI.pdf",
        }
        clean, errors = validate_and_clean([rec])
        assert not errors
        assert "  " not in clean[0]["requirement"]


class TestFullPipeline:
    def test_pipeline_produces_records_json(self, sample_pdf, tmp_path):
        out = str(tmp_path / "records_test.json")
        records, errors = run_pdf_pipeline(sample_pdf, out)
        assert len(errors) == 0
        assert len(records) == 14
        assert os.path.exists(out)
        with open(out, encoding="utf-8") as f:
            saved = json.load(f)
        assert len(saved) == 14

    def test_pipeline_missing_pdf(self, tmp_path):
        out = str(tmp_path / "records_test.json")
        records, errors = run_pdf_pipeline("data/raw/no_such.pdf", out)
        assert len(records) == 0
        assert len(errors) >= 1
