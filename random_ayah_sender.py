import requests
import os
import random

# Configuration (set your Discord webhook and role ID)
WEBHOOK_URL = os.getenv("WEBHOOK_URL") or "YOUR_DISCORD_WEBHOOK_URL"
QURAN_ROLE_ID = os.getenv("QURAN_ROLE_ID") or "YOUR_ROLE_ID"

# Quran API info
# We will use https://api.quran.com/api/v4/chapters to get chapters,
# then pick a random ayah from a random chapter using https://api.quran.com/api/v4/verses/by_chapter/:chapter_id

API_BASE = "https://api.quran.com/api/v4"

def get_chapters():
    url = f"{API_BASE}/chapters"
    r = requests.get(url)
    r.raise_for_status()
    data = r.json()
    return data['chapters']

def get_random_ayah():
    chapters = get_chapters()
    chapter = random.choice(chapters)
    chapter_id = chapter['id']
    verses_count = chapter['verses_count']

    # pick random ayah number in chapter
    ayah_number = random.randint(1, verses_count)

    # fetch the ayah by chapter and verse number with translation (English)
    url = f"{API_BASE}/verses/by_chapter/{chapter_id}"
    params = {
        "language": "en",
        "page": 1,
        "per_page": verses_count
    }
    r = requests.get(url, params=params)
    r.raise_for_status()
    data = r.json()
    verses = data['verses']

    ayah = next((v for v in verses if v['verse_number'] == ayah_number), None)
    if not ayah:
        raise Exception("Ayah not found")

    # Extract Arabic text and English translation if available
    arabic_text = ayah['text_uthmani']
    english_translation = ""
    
    # Translation extraction - check if translations key exists
    if 'translations' in ayah and len(ayah['translations']) > 0:
        english_translation = ayah['translations'][0]['text']

    return {
        "chapter_name": chapter['name_simple'],
        "chapter_id": chapter_id,
        "ayah_number": ayah_number,
        "arabic_text": arabic_text,
        "english_translation": english_translation
    }

def send_to_discord(ayah):
    divider = "───────────────────────────────"
    message = (
        f"{divider}\n"
        f"<@&{QURAN_ROLE_ID}>\n\n"
        f"Arabic: {ayah['arabic_text']}\n\n"
        f"Translation: {ayah['english_translation']}\n\n"
        f"Chapter: {ayah['chapter_name']} (ID: {ayah['chapter_id']})\n"
        f"Verse: {ayah['ayah_number']}\n"
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
