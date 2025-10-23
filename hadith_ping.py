import requests
import random
import os

WEBHOOK_URL = os.getenv("WEBHOOK_URL") or "YOUR_DISCORD_WEBHOOK_URL"
HADITH_ROLE_ID = os.getenv("HADITH_ROLE_ID") or "YOUR_ROLE_ID"
HADITH_API_KEY = os.getenv("HADITH_API_KEY") or "YOUR_API_KEY"

BOOKS_API = f"https://hadithapi.com/api/books?apiKey={HADITH_API_KEY}"
HADITHS_API = "https://hadithapi.com/api/hadiths"

def fetch_valid_books():
    resp = requests.get(BOOKS_API)
    resp.raise_for_status()
    books = resp.json().get("books", [])
    valid_books = []
    for book in books:
        # Check if book has hadiths by fetching count or test fetch (optional)
        slug = book.get("bookSlug")
        # Add only if slug exists and book name exists
        if slug and book.get("bookNameEnglish"):
            valid_books.append(slug)
    return valid_books

def get_random_hadith(book_slug):
    url = f"{HADITHS_API}/{book_slug}?apiKey={HADITH_API_KEY}&paginate=50"
    resp = requests.get(url)
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
    text = hadith.get("hadithEnglish", "No text")
    no = hadith.get("hadithNumber", "N/A")
    narrator = hadith.get("narrated", "Unknown")
    book = hadith.get("book", {}).get("bookNameEnglish", "Unknown Book")
    ref = hadith.get("reference", "No reference")

    message = (
        f"<@&{HADITH_ROLE_ID}>\n"
        f"\"{text}\"\n\n"
        f"Hadith #: {no}\n"
        f"Book: {book}\n"
        f"Narrator: {narrator}\n"
        f"Reference: {ref}\n"
        f"_Source: HadithAPI.com_"
    )
    res = requests.post(WEBHOOK_URL, json={"content": message})
    if res.status_code not in (200, 204):
        print("Failed to send message:", res.text)
    else:
        print(f"Hadith sent from {book}")

if __name__ == "__main__":
    try:
        valid_books = fetch_valid_books()
        hadith = None
        attempts = 0
        while not hadith and attempts < 10:
            book = random.choice(valid_books)
            hadith = get_random_hadith(book)
            attempts += 1
        if hadith:
            send_to_discord(hadith)
        else:
            print("Failed to fetch hadith after multiple attempts.")
    except Exception as e:
        print("Error:", e)
