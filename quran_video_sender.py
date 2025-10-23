import os
import random
import requests
from moviepy.editor import *
from discord_webhook import DiscordWebhook

WEBHOOK_URL = os.getenv("WEBHOOK_URL_VIDEO")
QURAN_ROLE_ID = os.getenv("QURAN_ROLE_ID_VIDEO")

BASE_API = "https://quranapi.pages.dev/api"

def get_random_ayah():
    chapters = requests.get(f"{BASE_API}/surah.json").json()
    chapter = random.choice(chapters)
    surah_no = chapters.index(chapter) + 1
    total_ayah = chapter['totalAyah']
    ayah_no = random.randint(1, total_ayah)
    ayah_url = f"{BASE_API}/{surah_no}/{ayah_no}.json"
    ayah = requests.get(ayah_url).json()
    arabic = ayah.get('arabic1') or ayah.get('arabic2') or "Arabic not found"
    audio = None
    audios = ayah.get("audio", {})
    if audios:
        reciter_id = list(audios.keys())[0]
        audio = audios[reciter_id].get("originalUrl") or audios[reciter_id].get("url")
    return arabic, audio, surah_no, ayah_no

def download_audio(audio_url):
    r = requests.get(audio_url, stream=True)
    r.raise_for_status()
    filename = "temp_audio.mp3"
    with open(filename, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)
    return filename

def create_video_with_text(text, audio_file, output_file):
    duration = AudioFileClip(audio_file).duration
    w, h = 720, 480

    bg = ColorClip(size=(w, h), color=(20, 20, 30), duration=duration)

    txt_clip = TextClip(
        text,
        fontsize=48,
        font="Amiri",
        color='white',
        size=(w-40, None),
        method='caption',
        align='center'
    ).set_pos('center').set_duration(duration)

    audio_clip = AudioFileClip(audio_file)

    video = CompositeVideoClip([bg, txt_clip]).set_audio(audio_clip)

    video.write_videofile(output_file, fps=24, codec='libx264', audio_codec='aac')

def send_video_to_discord(video_path):
    message = f"<@&{QURAN_ROLE_ID}> Here is a random Quran ayah recitation video."
    webhook = DiscordWebhook(url=WEBHOOK_URL, content=message)
    with open(video_path, "rb") as f:
        webhook.add_file(file=f.read(), filename=os.path.basename(video_path))
    webhook.execute()

def main():
    arabic_text, audio_url, surah_no, ayah_no = get_random_ayah()
    if not audio_url:
        print("No audio available for random ayah.")
        return

    print(f"Generating video for Surah {surah_no}, Ayah {ayah_no}")
    audio_file = download_audio(audio_url)
    video_file = f"quran_video_surah{surah_no}_ayah{ayah_no}.mp4"

    create_video_with_text(arabic_text, audio_file, video_file)
    send_video_to_discord(video_file)

    os.remove(audio_file)
    os.remove(video_file)

if __name__ == "__main__":
    main()
    
