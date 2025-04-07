# Quick and Dirty: WhatsApp Concierge Translator

A real-time, AI-powered multilingual assistant built for luxury travel and hospitality teams — using OpenAI, Twilio and Render to translate guest messages via WhatsApp without disrupting the high-touch human experience.

## Problem

Luxury concierge and travel management teams often support high-net-worth international guests who prefer communicating via WhatsApp.

But when guests message in languages like Russian, Mandarin, or Spanish, staff either scramble for a translator, use clunky third-party apps, or worse, **don’t respond quickly enough**. This creates friction in a space where **speed, discretion, and warmth are critical**.


## Experimenting with solutions

This app acts as a **silent, behind-the-scenes translator**:

- Guests message a concierge via WhatsApp — just like they normally would
- The bot detects the message language and translates it to English
- Staff reply in English — and their message is re-translated back to the guest's language
- Conversations feel human, seamless, and instant while preserving brand identity and building up a database of all interactions with customers for future potential automation.
- A big benefit of this approach is also that the guests are still interacting with real experienced humans and not a chatbot and without downloading a specialized concierge app (Whatsapp is most convenient currently) but this opens up doors for future automation.


## How It Works

1. **Guest** sends a WhatsApp message to a business number (via Twilio Sandbox)
2. **Twilio Webhook** delivers the message to a Flask server
3. **Flask App**:
   - Detects language using OpenAI's GPT-4
   - Translates the message (if needed)
   - Stores sender and language info in memory
4. **Staff reply** in English via a simple GUI Dashboard - deciding whether to move this to Slack 
5. Bot auto-translates response and sends it back to the guest via Twilio


## Tech Stack

- Python + Flask
- OpenAI API (GPT-4)
- Twilio WhatsApp Sandbox
- Render (for hosted deployment)
- ngrok (for local testing)
- Logging via `print()` (expandable)
- Optional `.env` config


## Getting Started (Local Dev)

### 1. Clone this repo

```bash
git clone https://github.com/yourusername/whatsapp-concierge-translator.git
cd whatsapp-concierge-translator