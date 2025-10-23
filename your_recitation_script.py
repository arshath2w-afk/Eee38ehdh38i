import requests
import os
import random

# Configuration - use environment variables or replace with actual values
WEBHOOK_URL = os.getenv("WEBHOOK_URL_RECITATION") or "YOUR_DISCORD_WEBHOOK_URL"
QURAN_ROLE_ID = os.getenv("QURAN_ROLE_ID_RECITATION") or "YOUR_ROLE_ID"

# List of Quranicaudio.com reciters (names and folder names for constructing URLs)
RECITERS = [
    {"name": "Mishary Rashid Alafasy", "folder": "7"},
    {"name": "Saad Al-Ghamdi", "folder": "2"},
    {"name": "Abdul Basit Abdul Samad", "folder": "3"},
    {"name": "Maher Al-Muaiqly", "folder": "17"},
    {"name": "Ahmed Al Ajmi", "folder": "4"},
    # Add more reciters with their folder number on Quranicaudio.com if desired
]

# Number of Surahs in the Quran
TOTAL_SURAHS = 114

def get_random_recitation():
    reciter = random.choice(RECITERS)
    surah_no = random.randint(1, TOTAL_SURAHS)

    # Surah number zero-padded to three digits (e.g., 001, 002, ..., 114)
    surah_str = f"{surah_no:03d}"

    # Construct the MP3 URL based on Quranicaudio.com pattern
    # Example: https://cdn.islamic.network/quran/audio/128/7/001.mp3
    audio_url = f"https://cdn.islamic.network/quran/audio/128/{reciter['folder']}/{surah_str}.mp3"
    
    return {
        "reciter_name": reciter["name"],
        "surah_no": surah_no,
        "surah_str": surah_str,
        "audio_url": audio_url
    }

def send_to_discord(recitation):
    divider = "───────────────────────────────"
    message = (
        f"{divider}\n"
        f"<@&{QURAN_ROLE_ID}>\n\n"
        f"Listen to full Surah recitation:\n"
        f"Surah Number: {recitation['surah_no']}\n"
        f"Reciter: {recitation['reciter_name']}\n"
        f"Audio: {recitation['audio_url']}\n\n"
        f"_Click the link above or paste into Discord to play within the app_\n"
        f"{divider}"
    )

    res = requests.post(WEBHOOK_URL, json={"content": message})
    if res.status_code not in (200, 204):
        print("Failed to send message:", res.text)
    else:
        print(f"Full Surah recitation sent to Discord: Surah {recitation['surah_no']} by {recitation['reciter_name']}")

if __name__ == "__main__":
    try:
        recitation = get_random_recitation()
        send_to_discord(recitation)
    except Exception as e:
        print("Error:", e)
