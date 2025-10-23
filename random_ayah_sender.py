import requests
import os
import random

# Configuration - set via environment variables
WEBHOOK_URL = os.getenv("WEBHOOK_URL_QURAN") or "YOUR_DISCORD_WEBHOOK_URL"
QURAN_ROLE_ID = os.getenv("QURAN_ROLE_ID") or "YOUR_ROLE_ID"

# Quran.com API base URL
BASE_API = "https://api.quran.com/api/v4"

def get_chapters():
    """Fetch all chapters from Quran API"""
    url = f"{BASE_API}/chapters"
    r = requests.get(url)
    r.raise_for_status()
    return r.json()["chapters"]

def get_random_ayah():
    """Get a random ayah with Arabic text and English translation"""
    # Get all chapters
    chapters = get_chapters()
    
    # Pick a random chapter
    chapter = random.choice(chapters)
    chapter_number = chapter["id"]
    verses_count = chapter["verses_count"]
    
    # Pick a random verse number in that chapter
    verse_number = random.randint(1, verses_count)
    
    # Fetch the specific verse with translation
    url = f"{BASE_API}/verses/by_chapter/{chapter_number}"
    params = {
        "words": "false",
        "translations": "131",  # Saheeh International translation
        "page": verse_number,
        "per_page": 1
    }
    
    r = requests.get(url, params=params)
    r.raise_for_status()
    data = r.json()
    
    # Get the verse data
    verses = data.get("verses", [])
    if not verses:
        raise Exception("No verses found")
    
    verse = verses[0]
    
    # Extract fields based on official API response structure
    arabic_text = verse.get("text_uthmani", "Arabic text not available")
    translation = ""
    
    if "translations" in verse and len(verse["translations"]) > 0:
        translation = verse["translations"][0].get("text", "Translation not available")
    
    return {
        "chapter_name": chapter["name_simple"],
        "chapter_number": chapter_number,
        "verse_number": verse_number,
        "verse_key": verse.get("verse_key", f"{chapter_number}:{verse_number}"),
        "arabic_text": arabic_text,
        "translation": translation
    }

def send_to_discord(ayah):
    """Send formatted ayah message to Discord"""
    divider = "───────────────────────────────"
    
    message = (
        f"{divider}\n"
        f"<@&{QURAN_ROLE_ID}>\n\n"
        f"**Arabic:** {ayah['arabic_text']}\n\n"
        f"**Translation:** {ayah['translation']}\n\n"
        f"**Surah:** {ayah['chapter_name']} ({ayah['verse_key']})\n"
        f"**Verse:** {ayah['verse_number']}\n\n"
        f"_Source: Quran.com_\n"
        f"{divider}"
    )
    
    res = requests.post(WEBHOOK_URL, json={"content": message})
    if res.status_code not in (200, 204):
        print("Failed to send message:", res.text)
    else:
        print(f"Random Ayah sent to Discord: {ayah['verse_key']}")

if __name__ == "__main__":
    try:
        ayah = get_random_ayah()
        send_to_discord(ayah)
    except Exception as e:
        print("Error:", e)
