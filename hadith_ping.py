import requests
import random
import os

# Environment variables (for GitHub Actions or local use)
WEBHOOK_URL = os.getenv("WEBHOOK_URL") or "YOUR_DISCORD_WEBHOOK_URL"
HADITH_ROLE_ID = os.getenv("HADITH_ROLE_ID") or "YOUR_ROLE_ID"
HADITH_API_KEY = os.getenv("HADITH_API_KEY") or "$2y$10$sGwoTXe3EvRvSCdIuy9sDeLhOjomG6OKkT453f0iFsLYUyxDf5i2"

# Base API URL
BOOKS_URL = f"https://hadithapi.com/api/books?apiKey={HADITH_API_KEY}"
HADITHS_URL = "https://hadithapi.com/api/hadiths"

def get_books():
    """Fetch list of valid book slugs"""
    res = requests.get(BOOKS_URL)
    if res.status_code != 200:
        raise Exception(f"Failed to load books: {res.text}")
    books = res.json().get("books", [])
    if not books:
        raise Exception("No books found.")
    return books

def get_random_hadith(book_slug):
    """Get random hadith from given book slug"""
    url = f"{HADITHS_URL}/{book_slug}?apiKey={HADITH_API_KEY}"
    res = requests.get(url)
    if res.status_code != 200:
        raise Exception(f"Hadith fetch failed: {res.text}")
    data = res.json()
    hadiths = data.get("hadiths", {}).get("data", [])
    if not hadiths:
        raise Exception("No hadiths found in this book.")
    return random.choice(hadiths)

def send_to_discord(hadith):
    """Send properly formatted hadith message to Discord"""
    text = hadith.get("hadithEnglish", "No text available")
    hadith_no = hadith.get("hadithNumber", "N/A")
    narrator = hadith.get("narrated", "Unknown Narrator")
    book_name = hadith.get("book", {}).get("bookNameEnglish", "Unknown Book")
    reference = hadith.get("reference", "No reference")

    message = (
        f"<@&{HADITH_ROLE_ID}>"
        f"\n\"{text}\"\n\n"
        f"Hadith #: {hadith_no}\n"
        f"Book: {book_name}\n"
        f"Narrator: {narrator}\n"
        f"Reference: {reference}\n"
        f"_Source: HadithAPI.com_"
    )

    res = requests.post(WEBHOOK_URL, json={"content": message})
    if res.status_code != 204:
        print("Failed to send:", res.text)
    else:
        print(f"Hadith sent successfully from {book_name}")

if __name__ == "__main__":
    try:
        books = get_books()
        random_book = random.choice(books)
        book_slug = random_book.get("bookSlug")

        print(f"Fetching hadith from: {book_slug}")
        hadith = get_random_hadith(book_slug)
        send_to_discord(hadith)
    except Exception as e:
        print("Error:", e)
