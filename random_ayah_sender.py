import requests
import os
import random
import json

# Configuration - use environment variables
WEBHOOK_URL = os.getenv("WEBHOOK_URL_QURAN") or "YOUR_DISCORD_WEBHOOK_URL"
QURAN_ROLE_ID = os.getenv("QURAN_ROLE_ID") or "YOUR_ROLE_ID"

BASE_API = "https://api.quran.com/api/v4"

def get_chapters():
    """Fetch all chapters from Quran API"""
    url = f"{BASE_API}/chapters"
    r = requests.get(url)
    r.raise_for_status()
    return r.json()["chapters"]

def get_random_ayah():
    """Get a random ayah with Arabic text and English translation"""
    chapters = get_chapters()
    chapter = random.choice(chapters)
    chapter_number = chapter["id"]
    chapter_name = chapter["name_simple"]
    verses_count = chapter["verses_count"]

    verse_number = random.randint(1, verses_count)

    # Fetch verse with Arabic text and translation
    url = f"{BASE_API}/verses/by_key/{chapter_number}:{verse_number}"
    params = {
        "translations": "131",  # Saheeh International translation ID
        "fields": "text_uthmani"  # Request Arabic text field
    }
    
    r = requests.get(url, params=params)
    r.raise_for_status()
    data = r.json()

    verse = data.get("verse", {})
    
    # Debug: Print full response to see structure
    print("=== DEBUG: Full verse JSON ===")
    print(json.dumps(verse, indent=2, ensure_ascii=False))
    print("=== END DEBUG ===")
    
    # Extract Arabic text
    arabic_text = verse.get("text_uthmani", "Arabic text not available")
    
    # Extract translation - check multiple possible locations
    translation = "Translation not available"
    
    # Try getting translation from translations array
    if "translations" in verse and verse["translations"]:
        translation = verse["translations"][0].get("text", "Translation not available")
    
    # If still not available, try from translation field directly
    if translation == "Translation not available" and "translation" in verse:
        translation = verse["translation"].get("text", "Translation not available")

    return {
        "chapter_name": chapter_name,
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
