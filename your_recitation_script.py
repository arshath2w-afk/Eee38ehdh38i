import requests
import os
import random

# Configuration - use new environment variables for webhook and role
WEBHOOK_URL = os.getenv("WEBHOOK_URL_RECITATION") or "YOUR_NEW_DISCORD_WEBHOOK_URL"
QURAN_ROLE_ID = os.getenv("QURAN_ROLE_ID_RECITATION") or "YOUR_NEW_ROLE_ID"

BASE_API = "https://quranapi.pages.dev/api"

def get_chapters():
    """Fetch all chapters from Quran API"""
    url = f"{BASE_API}/surah.json"
    r = requests.get(url)
    r.raise_for_status()
    return r.json()

def get_random_recitation():
    """Get a random ayah with audio recitation"""
    chapters = get_chapters()
    chapter = random.choice(chapters)
    
    surah_no = chapters.index(chapter) + 1
    surah_name = chapter.get("surahName", "Unknown Surah")
    total_ayah = chapter.get("totalAyah", 0)

    ayah_no = random.randint(1, total_ayah)

    # Fetch the specific ayah with audio
    url = f"{BASE_API}/{surah_no}/{ayah_no}.json"
    r = requests.get(url)
    r.raise_for_status()
    ayah = r.json()

    # Extract Arabic and English text
    arabic_text = ayah.get("arabic1", ayah.get("arabic2", "Arabic text not available"))
    english_translation = ayah.get("english", "Translation not available")

    # Extract audio recitations
    audio_data = ayah.get("audio", {})
    
    reciter_name = "No Recitation Available"
    audio_url = None
    
    if audio_data:
        reciter_ids = list(audio_data.keys())
        random_reciter_id = random.choice(reciter_ids)
        recitation = audio_data[random_reciter_id]
        reciter_name = recitation.get("reciter", "Unknown Reciter")
        audio_url = recitation.get("originalUrl") or recitation.get("url")

    return {
        "surah_name": surah_name,
        "surah_no": surah_no,
        "ayah_no": ayah_no,
        "verse_key": f"{surah_no}:{ayah_no}",
        "arabic_text": arabic_text,
        "english_translation": english_translation,
        "reciter_name": reciter_name,
        "audio_url": audio_url
    }

def send_to_discord(recitation_data):
    """Send audio recitation to Discord with playable audio"""
    divider = "───────────────────────────────"
    
    if not recitation_data["audio_url"]:
        message = (
            f"{divider}\n"
            f"<@&{QURAN_ROLE_ID}>\n\n"
            f"**Arabic:** {recitation_data['arabic_text']}\n\n"
            f"**Translation:** {recitation_data['english_translation']}\n\n"
            f"**Surah:** {recitation_data['surah_name']} ({recitation_data['verse_key']})\n"
            f"**Verse:** {recitation_data['ayah_no']}\n\n"
            f"Audio not available for this verse.\n"
            f"{divider}"
        )
    else:
        message = (
            f"{divider}\n"
            f"<@&{QURAN_ROLE_ID}>\n\n"
            f"**Arabic:** {recitation_data['arabic_text']}\n\n"
            f"**Translation:** {recitation_data['english_translation']}\n\n"
            f"**Surah:** {recitation_data['surah_name']} ({recitation_data['verse_key']})\n"
            f"**Verse:** {recitation_data['ayah_no']}\n\n"
            f"**Reciter:** {recitation_data['reciter_name']}\n"
            f"**Audio:** {recitation_data['audio_url']}\n\n"
            f"_Click the link or paste into Discord to play the recitation directly._\n"
            f"{divider}"
        )

    res = requests.post(WEBHOOK_URL, json={"content": message})
    if res.status_code not in (200, 204):
        print("Failed to send message:", res.text)
    else:
        print(f"Quran recitation sent to Discord: {recitation_data['verse_key']} - {recitation_data['reciter_name']}")

if __name__ == "__main__":
    try:
        recitation = get_random_recitation()
        send_to_discord(recitation)
    except Exception as e:
        print("Error:", e)
