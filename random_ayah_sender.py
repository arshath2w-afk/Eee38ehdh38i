import requests
import os
import random

# Configuration - use environment variables
WEBHOOK_URL = os.getenv("WEBHOOK_URL_QURAN") or "YOUR_DISCORD_WEBHOOK_URL"
QURAN_ROLE_ID = os.getenv("QURAN_ROLE_ID") or "YOUR_ROLE_ID"

BASE_API = "https://quranapi.pages.dev/api"

def get_chapters():
    """Fetch all chapters from Quran API"""
    url = f"{BASE_API}/surah.json"
    r = requests.get(url)
    r.raise_for_status()
    return r.json()

def get_random_ayah():
    """Get a random ayah with Arabic text and English translation"""
    chapters = get_chapters()
    chapter = random.choice(chapters)
    surah_no = chapter["surahNo"]
    surah_name = chapter["surahName"]
    total_ayah = chapter["totalAyah"]

    ayah_no = random.randint(1, total_ayah)

    # Fetch the specific ayah
    url = f"{BASE_API}/{surah_no}/{ayah_no}.json"
    r = requests.get(url)
    r.raise_for_status()
    ayah = r.json()

    # Extract fields based on official API response structure
    arabic_text = ayah.get("arabic1", ayah.get("arabic2", "Arabic text not available"))
    english_translation = ayah.get("english", "Translation not available")

    return {
        "surah_name": surah_name,
        "surah_no": surah_no,
        "ayah_no": ayah_no,
        "arabic_text": arabic_text,
        "english_translation": english_translation,
        "verse_key": f"{surah_no}:{ayah_no}"
    }

def get_tafsir(surah_no, ayah_no):
    """Fetch tafsir (tafseer) for a specific verse"""
    url = f"{BASE_API}/tafsir/{surah_no}_{ayah_no}.json"
    r = requests.get(url)
    r.raise_for_status()
    return r.json()

def send_to_discord(ayah, tafsir_data):
    """Send formatted ayah with tafsir message to Discord"""
    divider = "───────────────────────────────"
    
    # Extract tafsirs
    tafsirs = tafsir_data.get("tafsirs", [])
    tafsir_text = ""
    
    if tafsirs:
        # Use Ibn Kathir tafsir if available
        ibn_kathir = next((t for t in tafsirs if t.get("author") == "Ibn Kathir"), None)
        if ibn_kathir:
            tafsir_content = ibn_kathir.get("content", "Tafsir not available")
            # Truncate tafsir to avoid message length limit (Discord has 2000 char limit)
            if len(tafsir_content) > 500:
                tafsir_text = tafsir_content[:500] + "...\n\n[Full tafsir available on Quran.com]"
            else:
                tafsir_text = tafsir_content
        else:
            # Fallback to first available tafsir
            tafsir_text = tafsirs[0].get("content", "Tafsir not available")[:500]
    
    message = (
        f"{divider}\n"
        f"<@&{QURAN_ROLE_ID}>\n\n"
        f"**Arabic:** {ayah['arabic_text']}\n\n"
        f"**Translation:** {ayah['english_translation']}\n\n"
        f"**Surah:** {ayah['surah_name']} ({ayah['verse_key']})\n"
        f"**Verse:** {ayah['ayah_no']}\n\n"
        f"**Tafsir (Ibn Kathir):**\n{tafsir_text}\n\n"
        f"_Source: QuranAPI_\n"
        f"{divider}"
    )
    
    res = requests.post(WEBHOOK_URL, json={"content": message})
    if res.status_code not in (200, 204):
        print("Failed to send message:", res.text)
    else:
        print(f"Random Ayah with Tafsir sent to Discord: {ayah['verse_key']}")

if __name__ == "__main__":
    try:
        ayah = get_random_ayah()
        tafsir_data = get_tafsir(ayah["surah_no"], ayah["ayah_no"])
        send_to_discord(ayah, tafsir_data)
    except Exception as e:
        print("Error:", e)
