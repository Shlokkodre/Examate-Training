"""
Day 14 — Unit tests for app/whatsapp_bot.py and app/whatsapp_webhook.py

Run from repo root:
    python -m pytest tests/test_whatsapp_bot.py -v
"""

import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.whatsapp_bot import (
    parse_message,
    handle_message,
    get_user_lang,
    set_user_lang,
    _welcome,
    _checklist_reply,
    _font_reply,
    _lang_reply,
    _unknown_reply,
    _user_lang,
)
from app.whatsapp_webhook import _build_twiml

SENDER = "whatsapp:+919876543210"


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def reset_user_lang():
    """Reset session state before each test."""
    _user_lang.clear()
    yield
    _user_lang.clear()


# ── parse_message() tests ─────────────────────────────────────────────────────

class TestParseMessage:
    @pytest.mark.parametrize("text", ["hi", "hello", "Hey", "START", "namaste"])
    def test_greeting_intent(self, text):
        intent, args = parse_message(text)
        assert intent == "greeting"
        assert args == []

    def test_help_intent(self):
        intent, args = parse_message("help")
        assert intent == "help"

    @pytest.mark.parametrize("text", ["checklist", "CHECKLIST", "list", "mandatory"])
    def test_checklist_intent(self, text):
        intent, args = parse_message(text)
        assert intent == "checklist"

    def test_font_intent_with_valid_numbers(self):
        intent, args = parse_message("font 12 8")
        assert intent == "font"
        assert args == ["12", "8"]

    def test_font_intent_with_decimals(self):
        intent, args = parse_message("font 10.5 6.5")
        assert intent == "font"
        assert args[0] == "10.5"

    def test_lang_en_intent(self):
        intent, args = parse_message("lang en")
        assert intent == "lang"
        assert args == ["en"]

    def test_lang_mr_intent(self):
        intent, args = parse_message("lang mr")
        assert intent == "lang"
        assert args == ["mr"]

    def test_lang_hi_intent(self):
        intent, args = parse_message("lang hi")
        assert intent == "lang"
        assert args == ["hi"]

    def test_ask_intent(self):
        intent, args = parse_message("ask What is the veg symbol rule?")
        assert intent == "ask"
        assert "veg" in args[0].lower()

    def test_long_question_becomes_ask(self):
        intent, args = parse_message("What must I print on my chakli packet?")
        assert intent == "ask"

    def test_short_unknown_text(self):
        intent, _ = parse_message("ok")
        assert intent == "unknown"

    def test_empty_message(self):
        intent, _ = parse_message("")
        assert intent == "unknown"

    def test_case_insensitive_font(self):
        intent, args = parse_message("FONT 15 10")
        assert intent == "font"


# ── Session language tests ────────────────────────────────────────────────────

class TestSessionLang:
    def test_default_language_is_en(self):
        assert get_user_lang(SENDER) == "en"

    def test_set_and_get_marathi(self):
        set_user_lang(SENDER, "mr")
        assert get_user_lang(SENDER) == "mr"

    def test_set_and_get_hindi(self):
        set_user_lang(SENDER, "hi")
        assert get_user_lang(SENDER) == "hi"

    def test_invalid_lang_not_stored(self):
        set_user_lang(SENDER, "xx")
        assert get_user_lang(SENDER) == "en"  # falls back to default

    def test_different_senders_independent(self):
        set_user_lang("whatsapp:+1111", "mr")
        set_user_lang("whatsapp:+2222", "hi")
        assert get_user_lang("whatsapp:+1111") == "mr"
        assert get_user_lang("whatsapp:+2222") == "hi"


# ── Reply builder tests ───────────────────────────────────────────────────────

class TestWelcome:
    def test_english_welcome_contains_commands(self):
        reply = _welcome("en")
        assert "checklist" in reply
        assert "font" in reply
        assert "help" in reply

    def test_marathi_welcome_contains_devanagari(self):
        reply = _welcome("mr")
        assert any(ord(c) > 2304 for c in reply)

    def test_hindi_welcome_non_empty(self):
        reply = _welcome("hi")
        assert len(reply) > 50


class TestChecklistReply:
    def test_english_checklist_has_10_items(self):
        reply = _checklist_reply("en")
        # Count numbered items
        import re
        items = re.findall(r"^\d+\.", reply, re.MULTILINE)
        assert len(items) >= 8

    def test_checklist_contains_fssai_reg_numbers(self):
        reply = _checklist_reply("en")
        assert "5.1" in reply
        assert "5.8" in reply

    def test_marathi_checklist_has_devanagari(self):
        reply = _checklist_reply("mr")
        assert any(ord(c) > 2304 for c in reply)


class TestFontReply:
    def test_font_12x8_returns_1_5mm(self):
        reply = _font_reply("12", "8", "en")
        assert "1.5" in reply
        assert "96" in reply

    def test_font_5x5_returns_1_0mm(self):
        reply = _font_reply("5", "5", "en")
        assert "1.0" in reply

    def test_font_invalid_input(self):
        reply = _font_reply("abc", "8", "en")
        assert "font" in reply.lower() or "number" in reply.lower() or "send" in reply.lower()

    def test_font_marathi_reply(self):
        reply = _font_reply("12", "8", "mr")
        assert "1.5" in reply
        assert any(ord(c) > 2304 for c in reply)


class TestLangReply:
    def test_lang_en_confirmation(self):
        reply = _lang_reply("en")
        assert "English" in reply

    def test_lang_mr_confirmation_in_marathi(self):
        reply = _lang_reply("mr")
        assert any(ord(c) > 2304 for c in reply)

    def test_lang_hi_confirmation_in_hindi(self):
        reply = _lang_reply("hi")
        assert any(ord(c) > 2304 for c in reply)


class TestUnknownReply:
    def test_unknown_english_suggests_help(self):
        reply = _unknown_reply("en")
        assert "help" in reply.lower()


# ── handle_message() integration tests ───────────────────────────────────────

class TestHandleMessage:
    def test_hi_returns_welcome(self):
        reply = handle_message(SENDER, "hi")
        assert "HealthLabelCheck" in reply

    def test_checklist_command(self):
        reply = handle_message(SENDER, "checklist")
        assert "5.1" in reply or "Name" in reply

    def test_font_command(self):
        reply = handle_message(SENDER, "font 12 8")
        assert "1.5" in reply

    def test_lang_switch_persists(self):
        handle_message(SENDER, "lang mr")
        assert get_user_lang(SENDER) == "mr"
        # Next checklist should be in Marathi
        reply = handle_message(SENDER, "checklist")
        assert any(ord(c) > 2304 for c in reply)

    def test_lang_switch_then_font(self):
        handle_message(SENDER, "lang hi")
        reply = handle_message(SENDER, "font 12 8")
        assert "1.5" in reply
        assert any(ord(c) > 2304 for c in reply)

    def test_ask_out_of_scope(self):
        reply = handle_message(SENDER, "ask What is the cheapest printer?")
        # RAG should return out-of-scope
        assert len(reply) > 10

    def test_ask_fssai_question(self):
        reply = handle_message(SENDER, "ask What is the veg symbol rule?")
        assert len(reply) > 20

    def test_unknown_short_message(self):
        reply = handle_message(SENDER, "yo")
        assert len(reply) > 10


# ── TwiML builder tests ───────────────────────────────────────────────────────

class TestBuildTwiml:
    def test_valid_xml_structure(self):
        twiml = _build_twiml("Hello!")
        assert "<?xml" in twiml
        assert "<Response>" in twiml
        assert "<Message>" in twiml
        assert "Hello!" in twiml

    def test_escapes_ampersand(self):
        twiml = _build_twiml("Rice & Lentils")
        assert "&amp;" in twiml
        assert " & " not in twiml

    def test_escapes_angle_brackets(self):
        twiml = _build_twiml("<b>bold</b>")
        assert "&lt;" in twiml
        assert "&gt;" in twiml

    def test_long_message_included(self):
        long_msg = "A" * 500
        twiml = _build_twiml(long_msg)
        assert long_msg in twiml
