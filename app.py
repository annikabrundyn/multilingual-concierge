from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
from flask import Flask, request, render_template, redirect
from openai import OpenAI
import os
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@dataclass
class Message:
    """Represents a message from a guest with its translation details."""
    number: str
    original: str
    translated: str
    lang: str

class Config:
    """Configuration class to handle environment variables."""
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    TWILIO_PHONE_NUMBER: str = os.getenv("TWILIO_PHONE_NUMBER")
    PORT: int = int(os.environ.get("PORT", 5000))
    MODEL: str = "gpt-4o-mini"

class OpenAIService:
    """Service class for handling OpenAI operations."""
    def __init__(self):
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)

    def _get_completion(self, prompt: str) -> str:
        """Get completion from OpenAI API."""
        response = self.client.chat.completions.create(
            model=Config.MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        return response.choices[0].message.content.strip()

    def detect_and_translate_to_english(self, message: str) -> Tuple[str, str]:
        """Detect language and translate message to English."""
        lang_prompt = f"What language is this? Just return the language name:\n\n{message}"
        detected_lang = self._get_completion(lang_prompt)

        trans_prompt = f"Translate this message to English:\n\n{message}"
        translated = self._get_completion(trans_prompt)

        return detected_lang, translated

    def translate_back_to_original(self, message: str, lang: str) -> str:
        """Translate message back to original language."""
        prompt = f"Translate this message to {lang}:\n\n{message}"
        return self._get_completion(prompt)

class TwilioService:
    """Service class for handling Twilio operations."""
    def __init__(self):
        self.client = Client()
        self.from_number = os.getenv("TWILIO_PHONE_NUMBER")

        if not self.from_number:
            raise ValueError("Environment variable TWILIO_PHONE_NUMBER is not set")

    def send_whatsapp_message(self, to_number: str, message: str) -> None:
        """Send a WhatsApp message using Twilio."""

        # Ensure the 'to' number has whatsapp: prefix
        if not to_number.startswith("whatsapp:"):
            to_number = f"whatsapp:{to_number}"

        print(f"Sending WhatsApp message\nFrom: {self.from_number}\nTo: {to_number}\nMessage: {message}")

        self.client.messages.create(
            from_=self.from_number,
            to=f"whatsapp:{to_number}",
            body=message
        )

# Initialize services
app = Flask(__name__)
openai_service = OpenAIService()
twilio_service = TwilioService()

# Global state (in production, use a proper database)
user_langs: Dict[str, str] = {}
guest_messages: List[Message] = []

@app.route("/incoming", methods=["POST"])
def incoming_message():
    """Handle incoming WhatsApp messages."""
    from_number = request.form.get("From")
    body = request.form.get("Body")

    if not from_number or not body:
        return str(MessagingResponse())

    lang, translated = openai_service.detect_and_translate_to_english(body)
    user_langs[from_number] = lang

    guest_messages.append(Message(
        number=from_number,
        original=body,
        translated=translated,
        lang=lang
    ))

    return str(MessagingResponse())

@app.route("/inbox", methods=["GET"])
def inbox():
    """Display the staff inbox view."""
    return render_template("inbox.html", messages=guest_messages)

@app.route("/reply", methods=["POST"])
def reply():
    """Handle staff replies to guest messages."""
    try:
        number = request.form["number"]
        reply = request.form["reply"]
        name = request.form["name"]

        lang = user_langs.get(number, "English")
        full_reply = f"Hi, this is {name}. {reply}"
        translated = openai_service.translate_back_to_original(full_reply, lang)

        twilio_service.send_whatsapp_message(number, translated)
        return redirect("/inbox")

    except KeyError as e:
        # Log the error in production
        return redirect("/inbox")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=Config.PORT)