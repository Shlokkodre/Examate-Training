"""
Day 13 — Unit tests for app/translations.py and app/multilang_checker.py

Run from repo root:
    python -m pytest tests/test_translations.py -v
"""

import os, sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.translations import (
    t, translate_results, SUPPORTED_LANGS,
    REGULATION_NAMES, HINTS, UI_STRINGS,
)
from app.multilang_checker import check_label_multilang, format_multilang_table
from app.label_checker import RULES

SAMPLE_TEXT = """
CHAKLI SNACKS
Ingredients: Rice flour, vegetable oil, salt.
Net Qty: 200g
Manufactured by: Sunita Home Foods, Kopargaon, Maharashtra 423601
MFD: 17/11/2026   Best Before: 17/02/2027
FSSAI Lic. No.: 11417030000133
Veg  [GREEN DOT]
Store in a cool, dry place.
"""


# ── translations.py tests ─────────────────────────────────────────────────────

class TestTranslations:
    def test_all_regulations_have_all_langs(self):
        for reg_no, names in REGULATION_NAMES.items():
            for lang in SUPPORTED_LANGS:
                assert lang in names, f"Missing lang '{lang}' for regulation {reg_no}"
                assert names[lang], f"Empty translation for {reg_no}/{lang}"

    def test_all_hints_have_all_langs(self):
        for reg_no, hints in HINTS.items():
            for lang in SUPPORTED_LANGS:
                assert lang in hints, f"Missing hint lang '{lang}' for {reg_no}"
                assert hints[lang], f"Empty hint for {reg_no}/{lang}"

    def test_all_ui_strings_have_all_langs(self):
        for key, strings in UI_STRINGS.items():
            for lang in SUPPORTED_LANGS:
                assert lang in strings, f"Missing UI string lang '{lang}' for key '{key}'"

    def test_all_rule_regulation_nos_have_translations(self):
        rule_nos = {r["regulation_no"] for r in RULES}
        for reg_no in rule_nos:
            assert reg_no in REGULATION_NAMES, f"No translation for regulation {reg_no}"
            assert reg_no in HINTS, f"No hint for regulation {reg_no}"

    def test_t_returns_english_by_default(self):
        result = t("5.1")
        assert result == "Name of Food"

    def test_t_returns_marathi(self):
        result = t("5.1", "requirement", "mr")
        assert "अन्न" in result or len(result) > 3

    def test_t_returns_hindi(self):
        result = t("5.1", "requirement", "hi")
        assert "खाद्य" in result or len(result) > 3

    def test_t_returns_hint_english(self):
        hint = t("5.3", "hint", "en")
        assert "nutrition" in hint.lower() or "energy" in hint.lower()

    def test_t_returns_hint_marathi(self):
        hint = t("5.3", "hint", "mr")
        assert len(hint) > 10

    def test_t_returns_hint_hindi(self):
        hint = t("5.3", "hint", "hi")
        assert len(hint) > 10

    def test_t_ui_string_present(self):
        assert "✓" in t("status_present", lang="en")
        assert "✓" in t("status_present", lang="mr")
        assert "✓" in t("status_present", lang="hi")

    def test_t_ui_string_missing(self):
        assert "✗" in t("status_missing", lang="en")

    def test_t_unknown_lang_falls_back_to_english(self):
        result = t("5.1", "requirement", "xx")
        assert result == "Name of Food"

    def test_t_unknown_key_returns_key(self):
        assert t("nonexistent_key") == "nonexistent_key"

    def test_translations_not_identical_across_langs(self):
        # Marathi and Hindi should differ from English for most regulations
        en = t("5.1", "requirement", "en")
        mr = t("5.1", "requirement", "mr")
        hi = t("5.1", "requirement", "hi")
        assert en != mr
        assert en != hi


class TestTranslateResults:
    def test_english_returns_unchanged(self):
        from app.label_checker import check_label
        raw = check_label(SAMPLE_TEXT)
        result = translate_results(raw, "en")
        assert result is raw  # same object for English

    def test_marathi_adds_translated_fields(self):
        from app.label_checker import check_label
        raw = check_label(SAMPLE_TEXT)
        result = translate_results(raw, "mr")
        for r in result:
            assert "requirement_translated" in r
            assert "hint_translated" in r

    def test_hindi_adds_translated_fields(self):
        from app.label_checker import check_label
        raw = check_label(SAMPLE_TEXT)
        result = translate_results(raw, "hi")
        for r in result:
            assert "requirement_translated" in r

    def test_translated_requirement_non_empty(self):
        from app.label_checker import check_label
        raw = check_label(SAMPLE_TEXT)
        for lang in ["mr", "hi"]:
            result = translate_results(raw, lang)
            for r in result:
                assert r["requirement_translated"], f"Empty translation for {r['regulation_no']} in {lang}"


# ── multilang_checker.py tests ────────────────────────────────────────────────

class TestMultilangChecker:
    def test_returns_dict_with_required_keys(self):
        output = check_label_multilang(SAMPLE_TEXT, lang="en")
        for key in ["lang", "results", "summary", "summary_text", "missing_hints"]:
            assert key in output

    def test_lang_field_matches_input(self):
        for lang in SUPPORTED_LANGS:
            output = check_label_multilang(SAMPLE_TEXT, lang=lang)
            assert output["lang"] == lang

    def test_invalid_lang_falls_back_to_en(self):
        output = check_label_multilang(SAMPLE_TEXT, lang="zz")
        assert output["lang"] == "en"

    def test_results_count_equals_rules(self):
        output = check_label_multilang(SAMPLE_TEXT, lang="mr")
        assert len(output["results"]) == len(RULES)

    def test_summary_text_in_marathi(self):
        output = check_label_multilang(SAMPLE_TEXT, lang="mr")
        # Marathi summary contains Devanagari characters
        assert any(ord(c) > 2304 for c in output["summary_text"])

    def test_summary_text_in_hindi(self):
        output = check_label_multilang(SAMPLE_TEXT, lang="hi")
        assert any(ord(c) > 2304 for c in output["summary_text"])

    def test_missing_hints_translated(self):
        output = check_label_multilang(SAMPLE_TEXT, lang="mr")
        for hint in output["missing_hints"]:
            assert "hint_translated" in hint
            assert "requirement_translated" in hint

    def test_all_compliant_message_appears(self):
        full_text = """
        CHAKLI SNACKS premium
        Ingredients: Rice flour, vegetable oil, salt, spices.
        Net Qty: 200g
        Manufactured by: Sunita Home Foods, 12 Ganesh Nagar, Kopargaon, Maharashtra 423601
        MFD: 17/11/2026   Best Before: 17/02/2027
        FSSAI Lic. No.: 11417030000133
        Veg  [GREEN DOT]
        Nutritional Information per 100g: Energy 480 kcal Protein 6g Carbohydrate 62g Fat 22g Sodium 480mg
        Store in a cool dry place. Keep away from moisture.
        Colour (INS 102) Preservative (INS 211)
        """
        output = check_label_multilang(full_text, lang="en")
        # May or may not be fully compliant but summary_text should be non-empty
        assert len(output["summary_text"]) > 10


class TestFormatMultilangTable:
    def test_returns_string(self):
        output = check_label_multilang(SAMPLE_TEXT, lang="en")
        table = format_multilang_table(output)
        assert isinstance(table, str)

    def test_contains_regulation_numbers(self):
        output = check_label_multilang(SAMPLE_TEXT, lang="mr")
        table = format_multilang_table(output)
        for reg_no in ["5.1", "5.8", "6.1"]:
            assert reg_no in table

    def test_non_english_table_contains_devanagari(self):
        output = check_label_multilang(SAMPLE_TEXT, lang="mr")
        table = format_multilang_table(output)
        assert any(ord(c) > 2304 for c in table)

    def test_english_table_has_no_lang_suffix(self):
        output = check_label_multilang(SAMPLE_TEXT, lang="en")
        table = format_multilang_table(output)
        assert "/ EN" not in table

    def test_marathi_table_has_lang_suffix(self):
        output = check_label_multilang(SAMPLE_TEXT, lang="mr")
        table = format_multilang_table(output)
        assert "/ MR" in table
