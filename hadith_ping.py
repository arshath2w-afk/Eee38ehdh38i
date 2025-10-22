import requests
import random
import os

WEBHOOK_URL = os.getenv("WEBHOOK_URL")
HADITH_ROLE_ID = os.getenv("HADITH_ROLE_ID")

EDITIONS = [
    "eng-bukhari",
    "eng-muslim",
    "eng-tirmidhi",
    "eng-abudawud",
    "eng-nasai",
    "eng-ibnmajah",
    "eng-malik",
    "eng-ahmad",
    "eng-darimi",
    "eng-riyad",
    "eng-shamail",
    "eng-bulugh",
    "eng-adab",
    "eng-mishkat",
    "eng-nawawi",
    "eng-qudsi"
]

def fetch_random_hadith():
    edition = random.choice(EDITIONS)
    url = f"https://cdn.jsdelivr.net/gh/fawazahmed0/hadith-api@1/editions/{edition}.json"

    r = requests.get(url)
    if r.status_code != 200:
        raise Exception("Failed to fetch hadith")

    data = r.json()
    hadiths = data.get("hadiths", [])
    if not hadiths:
        raise Exception("Hadith list empty")

    hadith = random.choice(hadiths)
    # Extract details safely
    hadith_text = hadith.get("text", "No text available")
    hadith_number = hadith.get("hadith_number") or hadith.get("number") or "N/A"
    book = hadith.get("book") or "N/A"
    narrator = hadith.get("arabic_name") or hadith.get("narrator") or "N/A"
    book_name = data.get("metadata", {}).get("name", edition).replace("English:", "").strip()

    return hadith_text, hadith_number, book, narrator, book_name

def send_to_discord(hadith_text, hadith_number, book, narrator, source_name):
    message = (
        f"<@&{HADITH_ROLE_ID}>\n"
        f"\"{hadith_text}\"\n\n"
        f"Hadith #: {hadith_number}\n"
        f"Book: {book}\n"
        f"Narrator: {narrator}\n"
        f"_Source: {source_name}_"
    )

    payload = {"content": message}
    response = requests.post(WEBHOOK_URL, json=payload)

    if response.status_code != 204:
        print("Failed to send:", response.text)
    else:
        print(f"Hadith sent from {source_name}")

if __name__ == "__main__":
    try:
        text, hadith_number, book, narrator, source = fetch_random_hadith()
        send_to_discord(text, hadith_number, book, narrator, source)
    except Exception as e:
        print("Error:", e)
        
