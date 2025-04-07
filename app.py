from flask import Flask, request
from openai import OpenAI
import os
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Memory store: customer number → language
user_langs = {}

def detect_and_translate_to_english(message):
    prompt = f"What language is this? Just return the language name:\n\n{message}"
    lang_resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    detected_lang = lang_resp.choices[0].message.content.strip()

    translation_prompt = f"Translate this message to English:\n\n{message}"
    trans_resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": translation_prompt}],
        temperature=0
    )
    translated = trans_resp.choices[0].message.content.strip()

    return detected_lang, translated

def translate_back_to_original(message, lang):
    prompt = f"Translate this message to {lang}:\n\n{message}"
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    return response.choices[0].message.content.strip()

@app.route("/incoming", methods=["POST"])
def incoming_message():
    from_number = request.form.get("From")
    body = request.form.get("Body")

    resp = MessagingResponse()

    if from_number not in user_langs:
        lang, translated = detect_and_translate_to_english(body)
        user_langs[from_number] = lang
        print(f"[NEW] From {from_number}: Detected {lang}")
        resp.message(f"📩 [Translated from {lang}]\n{translated}")
    else:
        lang = user_langs[from_number]
        translated = translate_back_to_original(body, lang)
        print(f"[REPLY] To {from_number}: Translating to {lang}")
        resp.message(f"📤 [Translated to {lang}]\n{translated}")

    return str(resp)

if __name__ == "__main__":
    app.run(debug=True)