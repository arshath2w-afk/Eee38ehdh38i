import requests
import os
import random

WEBHOOK_URL = os.getenv("WEBHOOK_URL_RECITATION") or "YOUR_DISCORD_WEBHOOK_URL"
QURAN_ROLE_ID = os.getenv("QURAN_ROLE_ID_RECITATION") or "YOUR_ROLE_ID"

# Quranicaudio reciters folder IDs (same as before)
RECITERS = [
    {"name": "Mishary Rashid Alafasy", "folder": "7"},
    {"name": "Saad Al-Ghamdi", "folder": "2"},
    {"name": "Abdul Basit Abdul Samad", "folder": "3"},
    {"name": "Maher Al-Muaiqly", "folder": "17"},
    {"name": "Ahmed Al Ajmi", "folder": "4"},
]

TOTAL_SURAHS = 114

def download_audio(url):
    """Download audio file content"""
    r = requests.get(url, stream=True)
    r.raise_for_status()

    # Read content but limit size to 8MB to avoid large uploads
    content = b""
    max_size = 8 * 1024 * 1024  # 8MB

    for chunk in r.iter_content(chunk_size=8192):
        content += chunk
        if len(content) > max_size:
            print("Audio exceeds 8MB, stopping download.")
            return None

    return content

def send_audio_file(filename, file_bytes, reciter, surah_no):
    """Send audio file attachment to Discord webhook"""
    divider = "───────────────────────────────"
    content = f"{divider}\n<@&{QURAN_ROLE_ID}>\nRecitation by **{reciter}**, Surah #{surah_no}\n{divider}"

    files = {
        "file": (filename, file_bytes, "audio/mpeg"),
    }
    data = {
        "content": content,
    }

    res = requests.post(WEBHOOK_URL, data=data, files=files)
    if res.status_code not in (200, 204):
        print("Failed to send audio file:", res.text)
    else:
        print(f"Audio recitation sent: Surah {surah_no} by {reciter}")

def main():
    reciter = random.choice(RECITERS)
    surah_no = random.randint(1, TOTAL_SURAHS)
    surah_str = f"{surah_no:03d}"

    audio_url = f"https://cdn.islamic.network/quran/audio/128/{reciter['folder']}/{surah_str}.mp3"
    print(f"Downloading from {audio_url}")

    audio_data = download_audio(audio_url)

    if audio_data:
        filename = f"{reciter['name'].replace(' ', '_')}_Surah_{surah_str}.mp3"
        send_audio_file(filename, audio_data, reciter["name"], surah_no)
    else:
        print("Audio file too large or failed to download.")

if __name__ == "__main__":
    main()
