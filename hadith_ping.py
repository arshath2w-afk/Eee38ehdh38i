import requests
import random
import os

# ------------------------
# Configuration
# ------------------------
WEBHOOK_URL = os.getenv("WEBHOOK_URL") or "YOUR_DISCORD_WEBHOOK_URL"
HADITH_ROLE_ID = os.getenv("HADITH_ROLE_ID") or "YOUR_ROLE_ID"
HADITH_API_KEY = os.getenv("HADITH_API_KEY") or "$2y$10$sGwoTXe3EvRvSCdIuy9sDeLhOjomG6OKkT453f0iFsLYUyxDf5i2"

# Hadith API base URL
BASE_URL = "https://hadithapi.com/api/hadiths"

# List of authentic book slugs (from docs)
BOOKS = [
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
    """Fetch a random hadith from a random authentic book."""
    book_slug = random.choice(BOOKS)
    url = f"{BASE_URL}?apiKey={HADITH_API_KEY}&book={book_slug}&paginate=50"

    res = requests.get(url)
    if res.status_code != 200:
        raise Exception(f"API error: {res.status_code} - {res.text}")

    data = res.json()
    hadiths = data.get("hadiths", {}).get("data", [])
    if not hadiths:
        raise Exception("No hadith data returned")

    hadith = random.choice(hadiths)

    # Extract important fields safely
    text = hadith.get("hadithEnglish", "No text available")
    number = hadith.get("hadithNumber", "N/A")
    narrator = hadith.get("narrated", "Unknown Narrator")
    book = hadith.get("book", {}).get("bookNameEnglish", "Unknown Book")
    reference = hadith.get("reference", "No reference")

    return text, number, narrator, book, reference

def send_to_discord(text, number, narrator, book, reference):
    """Send the hadith nicely formatted to Discord webhook."""
    message = (
        f"<@&{HADITH_ROLE_ID}>\n"
        f"\"{text}\"\n\n"
        f"Hadith #: {number}\n"
        f"Book: {book}\n"
        f"Narrator: {narrator}\n"
        f"Reference: {reference}\n"
        f"_Source: HadithAPI.com_"
    )

    payload = {"content": message}
    res = requests.post(WEBHOOK_URL, json=payload)

    if res.status_code != 204:
        print("Failed to send:", res.text)
    else:
        print(f"Hadith sent successfully from {book}")

if __name__ == "__main__":
    try:
        text, number, narrator, book, reference = get_random_hadith()
        send_to_discord(text, number, narrator, book, reference)
    except Exception as err:
        print("Error:", err)
