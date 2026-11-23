"""
Day 14 — WhatsApp bot logic for HealthLabelCheck
Pure functions: parse an incoming WhatsApp message and build a reply.
No network calls here — all Twilio / HTTP concerns live in whatsapp_webhook.py.

Supported commands (case-insensitive):
  hi / hello / start      → welcome message + menu
  help                    → command list
  checklist               → 10 mandatory label items
  font <length> <width>   → minimum font size for given panel dimensions
  ask <question>          → RAG answer from FSSAI regulations
  lang mr / lang hi / lang en → switch reply language
  <anything else>         → treated as a question for the RAG pipeline
"""

import re
from typing import Tuple

from app.label_checker import check_label, checklist_summary
from app.translations import t, SUPPORTED_LANGS, UI_STRINGS
from app.multilang_checker import check_label_multilang
from app.models import get_min_font_size
from app.rag import ask as rag_ask

# ── Session state (in-memory, keyed by sender phone number) ──────────────────
# Stores per-user language preference.
# In production this would be a Redis / DB store.

_user_lang: dict = {}   # {phone_number: lang_code}

DEFAULT_LANG = "en"


def get_user_lang(sender: str) -> str:
    return _user_lang.get(sender, DEFAULT_LANG)


def set_user_lang(sender: str, lang: str) -> None:
    if lang in SUPPORTED_LANGS:
        _user_lang[sender] = lang


# ── Message parser ────────────────────────────────────────────────────────────

def parse_message(body: str) -> Tuple[str, list]:
    """
    Parse a raw WhatsApp message body into (intent, args).

    Returns:
        intent : str   — one of: greeting, help, checklist, font, ask, lang, unknown
        args   : list  — extra tokens (e.g. ["12", "8"] for font command)
    """
    text = body.strip().lower()

    if re.match(r"^(hi|hello|hey|start|namaste|नमस्ते|नमस्कार)$", text):
        return "greeting", []

    if text == "help":
        return "help", []

    if text in ("checklist", "list", "mandatory"):
        return "checklist", []

    m = re.match(r"^font\s+([\d.]+)\s+([\d.]+)$", text)
    if m:
        return "font", [m.group(1), m.group(2)]

    m = re.match(r"^lang\s+(en|mr|hi)$", text)
    if m:
        return "lang", [m.group(1)]

    m = re.match(r"^ask\s+(.+)$", text, re.DOTALL)
    if m:
        return "ask", [m.group(1).strip()]

    # Treat anything else ≥ 5 chars as a question
    if len(text) >= 5:
        return "ask", [body.strip()]

    return "unknown", []


# ── Reply builders ────────────────────────────────────────────────────────────

def _welcome(lang: str) -> str:
    titles = {
        "en": "🥘 *HealthLabelCheck*\nFSSAI Food Labelling Advisor",
        "mr": "🥘 *HealthLabelCheck*\nFSSAI अन्न लेबलिंग सल्लागार",
        "hi": "🥘 *HealthLabelCheck*\nFSSAI खाद्य लेबलिंग सलाहकार",
    }
    menus = {
        "en": (
            "Send any of these commands:\n"
            "• *checklist* — mandatory label items\n"
            "• *font 12 8* — min font size for 12×8 cm panel\n"
            "• *ask <question>* — FSSAI question\n"
            "• *lang mr* / *lang hi* / *lang en* — change language\n"
            "• *help* — show this menu\n\n"
            "Or just type your question!"
        ),
        "mr": (
            "हे संदेश पाठवा:\n"
            "• *checklist* — अनिवार्य लेबल बाबी\n"
            "• *font 12 8* — 12×8 सेमी पॅनेलसाठी किमान अक्षर आकार\n"
            "• *ask <प्रश्न>* — FSSAI प्रश्न\n"
            "• *lang en* / *lang hi* — भाषा बदला\n"
            "• *help* — हे मेनू दाखवा\n\n"
            "किंवा फक्त तुमचा प्रश्न टाइप करा!"
        ),
        "hi": (
            "ये संदेश भेजें:\n"
            "• *checklist* — अनिवार्य लेबल आइटम\n"
            "• *font 12 8* — 12×8 सेमी पैनल के लिए न्यूनतम फ़ॉन्ट\n"
            "• *ask <प्रश्न>* — FSSAI प्रश्न\n"
            "• *lang en* / *lang mr* — भाषा बदलें\n"
            "• *help* — यह मेनू दिखाएं\n\n"
            "या बस अपना प्रश्न टाइप करें!"
        ),
    }
    return titles.get(lang, titles["en"]) + "\n\n" + menus.get(lang, menus["en"])


def _checklist_reply(lang: str) -> str:
    """Return the 10 mandatory items in the target language."""
    from app.records import load_records, get_mandatory_checklist
    try:
        records  = load_records()
        checklist = get_mandatory_checklist(records)
    except Exception:
        return "Could not load checklist. Is the data file present?"

    headers = {
        "en": "✅ *Mandatory Label Requirements*",
        "mr": "✅ *अनिवार्य लेबल आवश्यकता*",
        "hi": "✅ *अनिवार्य लेबल आवश्यकताएं*",
    }
    lines = [headers.get(lang, headers["en"]), ""]
    for i, item in enumerate(checklist, 1):
        name = t(item["regulation_no"], "requirement", lang)
        lines.append(f"{i}. *{item['regulation_no']}* — {name}")
    return "\n".join(lines)


def _font_reply(length_str: str, width_str: str, lang: str) -> str:
    """Calculate font size and reply in target language."""
    try:
        length = float(length_str)
        width  = float(width_str)
    except ValueError:
        errors = {
            "en": "Please send numbers, e.g. *font 12 8*",
            "mr": "कृपया संख्या पाठवा, उदा. *font 12 8*",
            "hi": "कृपया संख्याएं भेजें, जैसे *font 12 8*",
        }
        return errors.get(lang, errors["en"])

    area     = length * width
    min_font = get_min_font_size(area)

    replies = {
        "en": (
            f"📐 *Font Size — FSSAI Regulation 6.1*\n\n"
            f"Panel: {length} × {width} cm = {area:.1f} cm²\n"
            f"Minimum letter height: *{min_font} mm*\n\n"
            f"This applies to the name of food, net quantity, and all "
            f"mandatory declarations on the front panel."
        ),
        "mr": (
            f"📐 *अक्षर आकार — FSSAI नियम 6.1*\n\n"
            f"पॅनेल: {length} × {width} सेमी = {area:.1f} चौ.सेमी\n"
            f"किमान अक्षर उंची: *{min_font} मिमी*\n\n"
            f"हे अन्नाचे नाव, निव्वळ प्रमाण आणि सर्व अनिवार्य माहितीस लागू आहे."
        ),
        "hi": (
            f"📐 *फ़ॉन्ट आकार — FSSAI नियम 6.1*\n\n"
            f"पैनल: {length} × {width} सेमी = {area:.1f} वर्ग सेमी\n"
            f"न्यूनतम अक्षर ऊंचाई: *{min_font} मिमी*\n\n"
            f"यह खाद्य का नाम, शुद्ध मात्रा और सभी अनिवार्य घोषणाओं पर लागू होता है."
        ),
    }
    return replies.get(lang, replies["en"])


def _ask_reply(question: str, lang: str) -> str:
    """Run the RAG pipeline and format a WhatsApp-friendly reply."""
    try:
        result = rag_ask(question, top_k=5)
    except Exception as e:
        return f"Error: {e}"

    answer    = result.get("answer", "")
    citations = result.get("citations", [])
    source    = result.get("source", "")

    # Trim to WhatsApp message size limit (~1600 chars)
    if len(answer) > 900:
        answer = answer[:900] + "…"

    # Source badge
    badges = {
        "llm":        {"en": "🤖 AI answer", "mr": "🤖 AI उत्तर", "hi": "🤖 AI उत्तर"},
        "rule_based": {"en": "📚 Rule-based", "mr": "📚 नियम आधारित", "hi": "📚 नियम आधारित"},
        "out_of_scope": {
            "en": "⛔ Out of scope",
            "mr": "⛔ व्याप्तीबाहेर",
            "hi": "⛔ दायरे से बाहर",
        },
    }
    badge = badges.get(source, {}).get(lang, source)

    lines = [f"_{badge}_\n", answer]
    if citations:
        cite_label = {"en": "Regulations cited", "mr": "नियम उद्धृत", "hi": "नियम उद्धृत"}
        lines.append(f"\n📌 {cite_label.get(lang,'Regulations cited')}: {', '.join(citations)}")

    return "\n".join(lines)


def _lang_reply(new_lang: str) -> str:
    confirmations = {
        "en": "Language set to *English*. Send *help* for commands.",
        "mr": "भाषा *मराठी* वर सेट केली. आदेशांसाठी *help* पाठवा.",
        "hi": "भाषा *हिंदी* पर सेट की गई। आदेशों के लिए *help* भेजें।",
    }
    return confirmations.get(new_lang, confirmations["en"])


def _unknown_reply(lang: str) -> str:
    msgs = {
        "en": "Sorry, I didn't understand that. Send *help* to see available commands.",
        "mr": "माफ करा, मला ते समजले नाही. उपलब्ध आदेशांसाठी *help* पाठवा.",
        "hi": "क्षमा करें, मैं यह नहीं समझा। उपलब्ध आदेशों के लिए *help* भेजें।",
    }
    return msgs.get(lang, msgs["en"])


# ── Main entry point ──────────────────────────────────────────────────────────

def handle_message(sender: str, body: str) -> str:
    """
    Handle one incoming WhatsApp message and return the reply string.

    Args:
        sender : WhatsApp sender ID, e.g. "whatsapp:+919876543210"
        body   : Raw message text from Twilio webhook

    Returns:
        Reply string (plain text with WhatsApp markdown: *bold*, _italic_)
    """
    lang   = get_user_lang(sender)
    intent, args = parse_message(body)

    if intent == "greeting":
        return _welcome(lang)

    if intent == "help":
        return _welcome(lang)

    if intent == "checklist":
        return _checklist_reply(lang)

    if intent == "font":
        return _font_reply(args[0], args[1], lang)

    if intent == "lang":
        new_lang = args[0]
        set_user_lang(sender, new_lang)
        return _lang_reply(new_lang)

    if intent == "ask":
        return _ask_reply(args[0], lang)

    return _unknown_reply(lang)


# ── Standalone demo ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    sender = "whatsapp:+919876543210"

    test_cases = [
        "hi",
        "checklist",
        "font 12 8",
        "ask What is the vegetarian symbol rule?",
        "lang mr",
        "checklist",          # now in Marathi
        "font 10 6",
        "lang en",
    ]

    print("=" * 60)
    print("HealthLabelCheck WhatsApp Bot Demo")
    print("=" * 60)

    for msg in test_cases:
        print(f"\n📱 User: {msg}")
        reply = handle_message(sender, msg)
        print(f"🤖 Bot:\n{reply}")
        print("-" * 40)
