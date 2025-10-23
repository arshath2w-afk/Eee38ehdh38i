import requests
import random
import os

# Configuration - set via environment variables or replace with actual values
WEBHOOK_URL = os.getenv("WEBHOOK_URL") or "YOUR_DISCORD_WEBHOOK_URL"
HADITH_ROLE_ID = os.getenv("HADITH_ROLE_ID") or "YOUR_ROLE_ID"
HADITH_API_KEY = os.getenv("HADITH_API_KEY") or "$2y$10$sGwoTXe3EvRvSCdIuy9sDeLhOjomG6OKkT453f0iFsLYUyxDf5i2"

print(f"Loaded API Key: {HADITH_API_KEY[:4]}{'*' * (len(HADITH_API_KEY) - 8)}{HADITH_API_KEY[-4:]}")
print(f"Webhook URL set: {'Yes' if WEBHOOK_URL != 'YOUR_DISCORD_WEBHOOK_URL' else 'No'}")
print(f"Hadith Role ID set: {'Yes' if HADITH_ROLE_ID != 'YOUR_ROLE_ID' else 'No'}")

HADITHS_API = "https://hadithapi.com/api/hadiths"

BOOK_SLUGS = [
    "sahih-bukhari",
    "sahih-muslim",
    "al-tirmidhi",
    "abu-dawood",
    "ibn-e-majah",
    "sunan-nasai",
    "mishkat"
]

def get_random_hadith(book_slug):
    params = {
        "apiKey": HADITH_API_KEY,
        "book": book_slug,
        "paginate": 50
    }
    print(f"Fetching hadiths from book '{book_slug}'...")
    resp = requests.get(HADITHS_API, params=params)
    if resp.status_code != 200:
        print(f"Warning: Could not fetch hadiths for '{book_slug}': {resp.status_code}")
        return None

    data = resp.json()
    hadiths = data.get("hadiths", {}).get("data", [])
    if not hadiths:
        print(f"Warning: No hadiths found for '{book_slug}'")
        return None

    return random.choice(hadiths)

def send_to_discord(hadith):
    text = hadith.get("hadithEnglish", "No text available")
    no = hadith.get("hadithNumber", "N/A")

    narrator = hadith.get("narrated") or hadith.get("narrator") or "Unknown Narrator"
    if isinstance(narrator, dict):
        narrator = narrator.get("name") or narrator.get("arabicName") or "Unknown Narrator"

    book_info = hadith.get("book")
    if isinstance(book_info, dict):
        book = book_info.get("bookNameEnglish") or book_info.get("name") or "Unknown Book"
    elif isinstance(book_info, str):
        book = book_info
    else:
        book = "Unknown Book"

    reference = hadith.get("reference") or hadith.get("hadithReference") or "No reference"

    message = (
        f"<@&{HADITH_ROLE_ID}>\n"
        f"\"{text}\"\n\n"
        f"Hadith #: {no}\n"
        f"Book: {book}\n"
        f"Narrator: {narrator}\n"
        f"Reference: {reference}\n"
        f"_Source: HadithAPI.com_"
    )

    res = requests.post(WEBHOOK_URL, json={"content": message})
    if res.status_code not in (200, 204):
        print("Failed to send message:", res.text)
    else:
        print(f"Hadith sent from {book}")

if __name__ == "__main__":
    try:
        hadith = None
        attempts = 0
        while not hadith and attempts < 10:
            book = random.choice(BOOK_SLUGS)
            hadith = get_random_hadith(book)
            attempts += 1
        if hadith:
            send_to_discord(hadith)
        else:
            print("Failed to fetch hadith after multiple attempts.")
    except Exception as e:
        print("Error:", e)
