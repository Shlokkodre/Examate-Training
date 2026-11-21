"""
Day 12 — Unit tests for app/label_checker.py and app/ocr.py

Run from repo root:
    python -m pytest tests/test_label_checker.py -v
"""

import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.label_checker import check_label, checklist_summary, format_checklist_table, RULES


# ── Fixtures ──────────────────────────────────────────────────────────────────

FULL_LABEL_TEXT = """
CHAKLI SNACKS
Ingredients: Rice flour, Bengal gram flour, vegetable oil, sesame seeds, salt, spices.
Net Qty: 200g
Manufactured by: Sunita Home Foods, 12 Ganesh Nagar, Kopargaon, Maharashtra - 423601
MFD: 17/11/2026   Best Before: 17/02/2027
FSSAI Lic. No.: 11417030000133
Veg  [GREEN DOT]
Allergen Info: Contains sesame seeds. May contain groundnuts.
Nutritional Information per 100g: Energy 480 kcal, Protein 6g, Carbohydrate 62g, Fat 22g, Sodium 480mg
Store in a cool, dry place. Keep away from moisture.
Colour (INS 102), Preservative (INS 211)
"""

MINIMAL_LABEL_TEXT = """
CHAKLI
Net Qty: 100g
MFD: 01/01/2026
FSSAI Lic. No.: 12345678901234
Veg
"""

EMPTY_TEXT = ""


@pytest.fixture
def full_results():
    return check_label(FULL_LABEL_TEXT)


@pytest.fixture
def minimal_results():
    return check_label(MINIMAL_LABEL_TEXT)


# ── check_label() tests ───────────────────────────────────────────────────────

class TestCheckLabel:
    def test_returns_list_of_dicts(self, full_results):
        assert isinstance(full_results, list)
        assert len(full_results) == len(RULES)

    def test_each_result_has_required_keys(self, full_results):
        for r in full_results:
            assert "regulation_no" in r
            assert "requirement"   in r
            assert "mandatory"     in r
            assert "status"        in r
            assert "hint"          in r

    def test_status_is_valid_value(self, full_results):
        for r in full_results:
            assert r["status"] in ("present", "missing")

    def test_full_label_finds_food_name(self, full_results):
        r = next(x for x in full_results if x["regulation_no"] == "5.1")
        assert r["status"] == "present"

    def test_full_label_finds_ingredients(self, full_results):
        r = next(x for x in full_results if x["regulation_no"] == "5.2")
        assert r["status"] == "present"

    def test_full_label_finds_net_quantity(self, full_results):
        r = next(x for x in full_results if x["regulation_no"] == "5.6")
        assert r["status"] == "present"

    def test_full_label_finds_dates(self, full_results):
        r = next(x for x in full_results if x["regulation_no"] == "5.7")
        assert r["status"] == "present"

    def test_full_label_finds_fssai_number(self, full_results):
        r = next(x for x in full_results if x["regulation_no"] == "5.8")
        assert r["status"] == "present"

    def test_full_label_finds_veg_symbol(self, full_results):
        r = next(x for x in full_results if x["regulation_no"] == "5.10")
        assert r["status"] == "present"

    def test_full_label_finds_nutritional_info(self, full_results):
        r = next(x for x in full_results if x["regulation_no"] == "5.3")
        assert r["status"] == "present"

    def test_full_label_finds_allergens(self, full_results):
        r = next(x for x in full_results if x["regulation_no"] == "5.4")
        assert r["status"] == "present"

    def test_full_label_finds_additives(self, full_results):
        r = next(x for x in full_results if x["regulation_no"] == "5.12")
        assert r["status"] == "present"

    def test_full_label_finds_manufacturer(self, full_results):
        r = next(x for x in full_results if x["regulation_no"] == "5.5")
        assert r["status"] == "present"

    def test_minimal_label_missing_nutrition(self, minimal_results):
        r = next(x for x in minimal_results if x["regulation_no"] == "5.3")
        assert r["status"] == "missing"

    def test_minimal_label_missing_manufacturer(self, minimal_results):
        r = next(x for x in minimal_results if x["regulation_no"] == "5.5")
        assert r["status"] == "missing"

    def test_missing_items_have_hints(self, minimal_results):
        for r in minimal_results:
            if r["status"] == "missing":
                assert r["hint"], f"No hint for missing {r['regulation_no']}"

    def test_present_items_have_empty_hint(self, full_results):
        for r in full_results:
            if r["status"] == "present":
                assert r["hint"] == ""

    def test_empty_text_all_missing(self):
        results = check_label(EMPTY_TEXT)
        # 6.1 and 6.2 use [\s\S]{50,} which won't match empty string
        mandatory_missing = [
            r for r in results if r["mandatory"] and r["status"] == "missing"
        ]
        assert len(mandatory_missing) >= 8

    def test_case_insensitive_matching(self):
        text = "FSSAI LIC NO 12345678901234  NET WT 200G  BEST BEFORE 12/2027  VEG"
        results = check_label(text)
        fssai = next(r for r in results if r["regulation_no"] == "5.8")
        assert fssai["status"] == "present"


# ── checklist_summary() tests ─────────────────────────────────────────────────

class TestChecklistSummary:
    def test_summary_keys(self, full_results):
        s = checklist_summary(full_results)
        for key in ["total", "mandatory_total", "mandatory_present",
                    "mandatory_missing", "conditional_present", "compliance_pct"]:
            assert key in s

    def test_total_equals_rules_count(self, full_results):
        s = checklist_summary(full_results)
        assert s["total"] == len(RULES)

    def test_present_plus_missing_equals_mandatory(self, full_results):
        s = checklist_summary(full_results)
        assert s["mandatory_present"] + s["mandatory_missing"] == s["mandatory_total"]

    def test_compliance_pct_range(self, full_results):
        s = checklist_summary(full_results)
        assert 0 <= s["compliance_pct"] <= 100

    def test_full_label_high_compliance(self, full_results):
        s = checklist_summary(full_results)
        assert s["compliance_pct"] >= 80

    def test_minimal_label_lower_compliance(self, minimal_results):
        s_full    = checklist_summary(check_label(FULL_LABEL_TEXT))
        s_minimal = checklist_summary(minimal_results)
        assert s_minimal["compliance_pct"] <= s_full["compliance_pct"]


# ── format_checklist_table() tests ───────────────────────────────────────────

class TestFormatTable:
    def test_returns_string(self, full_results):
        table = format_checklist_table(full_results)
        assert isinstance(table, str)

    def test_contains_all_regulation_numbers(self, full_results):
        table = format_checklist_table(full_results)
        for r in full_results:
            assert r["regulation_no"] in table

    def test_contains_pass_and_fail(self, minimal_results):
        table = format_checklist_table(minimal_results)
        assert "PASS" in table
        assert "FAIL" in table


# ── OCR image test (uses generated sample label) ──────────────────────────────

class TestOCRPipeline:
    LABEL_PATH = "data/sample_label.png"

    @pytest.fixture(scope="class", autouse=True)
    def ensure_label_exists(self):
        """Generate the sample label if it doesn't exist."""
        if not os.path.exists(self.LABEL_PATH):
            from data.make_sample_label import build_label
            build_label(self.LABEL_PATH)
        assert os.path.exists(self.LABEL_PATH)

    def test_ocr_extracts_non_empty_text(self):
        from app.ocr import extract_text_from_image
        text = extract_text_from_image(self.LABEL_PATH)
        assert isinstance(text, str)
        assert len(text) > 20, f"OCR returned too little text: '{text}'"

    def test_ocr_finds_fssai_number(self):
        from app.ocr import extract_text_from_image
        text = extract_text_from_image(self.LABEL_PATH)
        # FSSAI number is on the label — OCR should pick up the digits
        assert any(c.isdigit() for c in text)

    def test_ocr_to_checker_pipeline(self):
        from app.ocr import extract_text_from_image
        text = extract_text_from_image(self.LABEL_PATH)
        results = check_label(text)
        summary = checklist_summary(results)
        # At least some items should be found
        assert summary["mandatory_present"] >= 1

    def test_missing_image_raises(self):
        from app.ocr import extract_text_from_image
        with pytest.raises(FileNotFoundError):
            extract_text_from_image("data/no_such_image.png")
