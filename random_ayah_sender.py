import requests
import os
import random

WEBHOOK_URL = os.getenv("WEBHOOK_URL_QURAN") or "YOUR_DISCORD_WEBHOOK_URL"
QURAN_ROLE_ID = os.getenv("QURAN_ROLE_ID") or "YOUR_ROLE_ID"

BASE_API = "https://api.quran.com/api/v4"

def get_chapters():
    url = f"{BASE_API}/chapters"
    r = requests.get(url)
    r.raise_for_status()
    return r.json()["chapters"]

def get_ayah(chapter_number, verse_number):
    url = f"{BASE_API}/verses/by_key/{chapter_number}:{verse_number}"
    params = {
        "language": "ar",
        "words": False,
        "translations": 131  # Saheeh International ID
    }
    r = requests.get(url, params=params)
    r.raise_for_status()
    return r.json()["verse"]

def get_random_ayah():
    chapters = get_chapters()
    chapter = random.choice(chapters)
    chapter_number = chapter["id"]
    verses_count = chapter["verses_count"]

    verse_number = random.randint(1, verses_count)
    ayah = get_ayah(chapter_number, verse_number)

    arabic_text = ayah["text_uthmani"]
    translation = ""
    if "translations" in ayah and len(ayah["translations"]) > 0:
        translation = ayah["translations"][0]["text"]

    return {
        "chapter_name": chapter["name_simple"],
        "chapter_number": chapter_number,
        "verse_number": verse_number,
        "arabic_text": arabic_text,
        "translation": translation
    }

def send_to_discord(ayah):
    divider = "───────────────────────────────"
    message = (
        f"{divider}\n"
        f"<@&{QURAN_ROLE_ID}>\n\n"
        f"Arabic: {ayah['arabic_text']}\n\n"
        f"Translation: {ayah['translation']}\n\n"
        f"Chapter: {ayah['chapter_name']} (#{ayah['chapter_number']})\n"
        f"Verse: {ayah['verse_number']}\n"
        f"{divider}"
    )
    res = requests.post(WEBHOOK_URL, json={"content": message})
    if res.status_code not in (200, 204):
        print("Failed to send message:", res.text)
    else:
        print("Random Ayah sent to Discord.")

if __name__ == "__main__":
    try:
        ayah = get_random_ayah()
        send_to_discord(ayah)
    except Exception as e:
        print("Error:", e)
