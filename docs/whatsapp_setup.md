# WhatsApp Bot Setup — Day 14

HealthLabelCheck can answer FSSAI food labelling questions over WhatsApp
using the Twilio Sandbox (free, no WhatsApp Business Account needed).

---

## 1. Create a Twilio account

Go to https://www.twilio.com and sign up for a free account.
No credit card required for the sandbox.

---

## 2. Enable the WhatsApp Sandbox

1. In the Twilio Console, go to **Messaging → Try it out → Send a WhatsApp message**
2. Follow the on-screen instructions:
   - Save the Twilio sandbox number (e.g. `+14155238886`) to your WhatsApp contacts
   - Send the join code (e.g. `join example-word`) to that number
3. Your phone is now connected to the sandbox

---

## 3. Run the FastAPI server

```bash
# Install dependencies
pip install -r requirements.txt

# Start the server
python -m uvicorn app.main:app --reload --port 8000
```

---

## 4. Expose localhost to the internet (for development)

Twilio needs a public URL to send webhooks. Use ngrok:

```bash
# Install ngrok from https://ngrok.com
ngrok http 8000
```

Copy the HTTPS forwarding URL, e.g. `https://abc123.ngrok.io`

---

## 5. Set the webhook URL in Twilio

1. In the Twilio Console → Messaging → Try it out → Send a WhatsApp message
2. Under **Sandbox Configuration**, set:
   - **When a message comes in**: `https://abc123.ngrok.io/whatsapp`
   - Method: `HTTP POST`
3. Click **Save**

---

## 6. Add Twilio credentials to .env (optional)

```bash
# .env
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here
WHATSAPP_FROM=whatsapp:+14155238886
```

The bot works without credentials in development (signature validation is skipped).

---

## 7. Test the bot

Send these messages from your WhatsApp to the Twilio sandbox number:

| Message | Expected reply |
|---------|---------------|
| `hi` | Welcome message + command menu |
| `checklist` | 10 mandatory label items |
| `font 12 8` | Min font size for 12×8 cm panel → 1.5 mm |
| `ask What is the veg symbol rule?` | RAG answer with regulation citation |
| `lang mr` | Switch to Marathi |
| `checklist` | Checklist in Marathi |
| `lang en` | Switch back to English |

---

## 8. Deploy to Render

Once deployed (see `render.yaml`), set the Twilio webhook to your Render URL:

```
https://healthlabelcheck.onrender.com/whatsapp
```

Add `TWILIO_ACCOUNT_SID` and `TWILIO_AUTH_TOKEN` as environment variables
in the Render dashboard.

---

## Architecture

```
WhatsApp User
    ↓  (message)
Twilio API
    ↓  POST /whatsapp  (form: From, Body)
app/whatsapp_webhook.py
    ↓
app/whatsapp_bot.py  (parse intent, build reply)
    ├── checklist  → app/records.py + app/translations.py
    ├── font       → app/models.get_min_font_size()
    ├── ask        → app/rag.ask()
    └── lang       → per-user language session
    ↓
TwiML XML response
    ↓
Twilio delivers reply to WhatsApp
```

---

## Supported Commands

| Command | Description |
|---------|-------------|
| `hi` / `hello` / `start` | Welcome message |
| `help` | Command menu |
| `checklist` | 10 mandatory FSSAI label items |
| `font <length> <width>` | Minimum font size (Reg 6.1) |
| `ask <question>` | RAG answer from FSSAI regulations |
| `lang en` / `lang mr` / `lang hi` | Switch language |
| `<any question>` | Treated as an FSSAI question |
