import requests
import os
import random

WEBHOOK_URL = os.getenv("WEBHOOK_URL_RECITATION") or "YOUR_DISCORD_WEBHOOK_URL"
QURAN_ROLE_ID = os.getenv("QURAN_ROLE_ID_RECITATION") or "YOUR_ROLE_ID"

BASE_API = "https://quranapi.pages.dev/api"

def get_reciters():
    url = f"{BASE_API}/recitations.json"
    r = requests.get(url)
    r.raise_for_status()
    return r.json()

def get_chapters():
    url = f"{BASE_API}/surah.json"
    r = requests.get(url)
    r.raise_for_status()
    return r.json()

def send_full_surah_recitation():
    reciters = get_reciters()
    chapters = get_chapters()

    reciter = random.choice(reciters)
    chapter = random.choice(chapters)

    reciter_id = reciter.get("recitationId") or reciter.get("id")
    reciter_name = reciter.get("recitationName") or reciter.get("reciterName") or "Unknown Reciter"

    surah_no = chapters.index(chapter) + 1
    surah_name = chapter.get("surahName", "Unknown Surah")

    # Construct direct full Surah audio URL (example pattern, confirm actual API spec)
    audio_url = f"{BASE_API}/recitations/{reciter_id}/{surah_no}.mp3"

    divider = "───────────────────────────────"
    message = (
        f"{divider}\n"
        f"<@&{QURAN_ROLE_ID}>\n\n"
        f"Listen to full recitation of Surah **{surah_name}** by **{reciter_name}**:\n"
        f"{audio_url}\n\n"
        f"_Click the link or paste into Discord to play the full Surah recitation._\n"
        f"{divider}"
    )

    res = requests.post(WEBHOOK_URL, json={"content": message})
    if res.status_code not in (200, 204):
        print("Failed to send message:", res.text)
    else:
        print(f"Full Surah recitation sent: {surah_name} by {reciter_name}")

if __name__ == "__main__":
    try:
        send_full_surah_recitation()
    except Exception as e:
        print("Error:", e)
