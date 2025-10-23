import requests
import random
import os
import json

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
    # Debug: Print the full JSON structure to understand the response
    print("=== DEBUG: Full Hadith JSON Structure ===")
    print(json.dumps(hadith, indent=2, ensure_ascii=False))
    print("=== END DEBUG ===")
    
    # Extract text - try multiple possible field names
    text = (hadith.get("hadithEnglish") or 
            hadith.get("hadith") or 
            hadith.get("text") or 
            hadith.get("english") or 
            "No text available")
    
    # Extract hadith number - try multiple possible field names  
    no = (hadith.get("hadithNumber") or 
          hadith.get("hadith_number") or
          hadith.get("number") or
          hadith.get("id") or
          "N/A")
    
    # Extract narrator - try multiple approaches
    narrator = "Unknown Narrator"
    narrator_candidates = [
        hadith.get("narrated"),
        hadith.get("narrator"), 
        hadith.get("rawi"),
        hadith.get("chain")
    ]
    for candidate in narrator_candidates:
        if candidate:
            if isinstance(candidate, dict):
                narrator = candidate.get("name") or candidate.get("arabicName") or candidate.get("english") or "Unknown Narrator"
            elif isinstance(candidate, str):
                narrator = candidate
            break
    
    # Extract book name - try multiple approaches
    book = "Unknown Book"
    book_info = hadith.get("book")
    if isinstance(book_info, dict):
        book = (book_info.get("bookNameEnglish") or 
                book_info.get("name") or 
                book_info.get("bookName") or
                book_info.get("title") or
                "Unknown Book")
    elif isinstance(book_info, str):
        book = book_info
    
    # Extract reference - try multiple possible field names
    reference = (hadith.get("reference") or 
                hadith.get("hadithReference") or
                hadith.get("ref") or
                hadith.get("source") or
                "No reference")

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
