"""
Day 14 — Twilio WhatsApp webhook router for HealthLabelCheck
Mounts at POST /whatsapp on the FastAPI app.

Twilio sends incoming WhatsApp messages as form-encoded POST data:
  From  : "whatsapp:+91XXXXXXXXXX"
  Body  : message text

This router:
1. Parses the Twilio form payload
2. Calls whatsapp_bot.handle_message()
3. Returns a TwiML MessagingResponse so Twilio delivers the reply

Setup:
  1. Create a free Twilio account at https://www.twilio.com
  2. Go to Messaging → Try it out → Send a WhatsApp message
  3. Follow the sandbox join instructions
  4. Set the sandbox "When a message comes in" webhook to:
       https://<your-render-url>/whatsapp
  5. Set TWILIO_AUTH_TOKEN in .env for signature validation (optional in dev)

Environment variables (all optional for local dev):
  TWILIO_ACCOUNT_SID   : Twilio account SID
  TWILIO_AUTH_TOKEN    : Used for webhook signature validation
  WHATSAPP_FROM        : Twilio sandbox number, e.g. whatsapp:+14155238886
"""

import os
from fastapi import APIRouter, Form, Request, HTTPException
from fastapi.responses import Response

router = APIRouter()


def _validate_twilio_signature(request: Request, auth_token: str) -> bool:
    """
    Optional: validate that the request really came from Twilio.
    Skip in development when TWILIO_AUTH_TOKEN is not set.
    """
    if not auth_token:
        return True   # skip validation in dev

    try:
        from twilio.request_validator import RequestValidator
        validator  = RequestValidator(auth_token)
        url        = str(request.url)
        # Twilio sends params as form data; we validate against the full URL
        signature  = request.headers.get("X-Twilio-Signature", "")
        return validator.validate(url, {}, signature)
    except Exception:
        return True   # don't block if validation library has issues


def _build_twiml(message: str) -> str:
    """Wrap a reply message in a minimal TwiML MessagingResponse."""
    # Escape XML special characters
    safe = (message
            .replace("&",  "&amp;")
            .replace("<",  "&lt;")
            .replace(">",  "&gt;")
            .replace('"',  "&quot;"))
    return (
        '<?xml version="1.0" encoding="UTF-8"?>'
        "<Response>"
        f"<Message>{safe}</Message>"
        "</Response>"
    )


@router.post("/whatsapp", tags=["Day 14 — WhatsApp Bot"])
async def whatsapp_webhook(
    request: Request,
    From: str = Form(...),
    Body: str = Form(default=""),
):
    """
    Twilio WhatsApp incoming message webhook.

    Twilio POSTs form data with at minimum:
        From : sender WhatsApp number
        Body : message text

    Returns TwiML XML that Twilio uses to send the reply.
    """
    auth_token = os.getenv("TWILIO_AUTH_TOKEN", "")
    if auth_token and not _validate_twilio_signature(request, auth_token):
        raise HTTPException(status_code=403, detail="Invalid Twilio signature.")

    from app.whatsapp_bot import handle_message
    reply = handle_message(sender=From, body=Body)
    twiml = _build_twiml(reply)

    return Response(content=twiml, media_type="application/xml")


@router.get("/whatsapp/health", tags=["Day 14 — WhatsApp Bot"])
def whatsapp_health():
    """Quick health check for the WhatsApp webhook route."""
    return {"status": "ok", "endpoint": "POST /whatsapp"}
