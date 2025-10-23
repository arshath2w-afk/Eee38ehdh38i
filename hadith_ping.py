import requests
import random
import os

# ------------------------------------------------
# Configuration (use GitHub Secrets or local .env)
# ------------------------------------------------
WEBHOOK_URL = os.getenv("WEBHOOK_URL") or "YOUR_DISCORD_WEBHOOK_URL"
HADITH_ROLE_ID = os.getenv("HADITH_ROLE_ID") or "YOUR_ROLE_ID"
HADITH_API_KEY = os.getenv("HADITH_API_KEY") or "$2y$10$sGwoTXe3EvRvSCdIuy9sDeLhOjomG6OKkT453f0iFsLYUyxDf5i2"

# ------------------------------------------------
# Hadith API Reference
# https://hadithapi.com/docs/hadiths
# ------------------------------------------------
API_URL = "https://hadithapi.com/api/hadiths"

BOOK_SLUGS = [
    "sahih-bukhari",
    "sahih-muslim",
    "al-tirmidhi",
    "abu-dawood",
    "ibn-e-majah",
    "sunan-nasai",
    "mishkat",
    "musnad-ahmad",
    "al-silsila-sahiha"
]

def get_random_hadith():
    """Fetch one random hadith from a random book."""
    book = random.choice(BOOK_SLUGS)
    params = {
        "apiKey": HADITH_API_KEY,
        "book": book,
        "paginate": 50  # get more results per request
    }

    print(f"Fetching hadiths from: {book}")
    res = requests.get(API_URL, params=params)
    if res.status_code != 200:
        raise Exception(f"API error {res.status_code}: {res.text}")

    data = res.json()
    hadiths = data.get("hadiths", {}).get("data", [])
    if not hadiths:
        raise Exception("No hadiths returned from API.")

    return random.choice(hadiths)

def send_to_discord(h):
    """Send nicely formatted hadith to Discord."""
    text = h.get("hadithEnglish", "No text available")
    number = h.get("hadithNumber", "N/A")
    narrator = h.get("narrated", "Unknown Narrator")
    reference = h.get("reference", "No reference")
    book_name = h.get("book", {}).get("bookNameEnglish", "Unknown Book")

    message = (
        f"<@&{HADITH_ROLE_ID}>\n"
        f"\"{text}\"\n\n"
        f"Hadith #: {number}\n"
        f"Book: {book_name}\n"
        f"Narrator: {narrator}\n"
        f"Reference: {reference}\n"
        f"_Source: HadithAPI.com_"
    )

    res = requests.post(WEBHOOK_URL, json={"content": message})
    if res.status_code not in (200, 204):
        print("Failed to send:", res.text)
    else:
        print(f"Hadith sent successfully ({book_name})")

if __name__ == "__main__":
    try:
        hadith = get_random_hadith()
        send_to_discord(hadith)
    except Exception as e:
        print("Error:", e)
        
