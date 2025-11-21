# Sigma.py
import os
import sys
import requests
from datetime import datetime
import pytz

WEBHOOK_URL = os.getenv("JUMMAH_HOOK")

def abort(msg, code=1):
    print("ERROR:", msg)
    sys.exit(code)

# Validate webhook
if not WEBHOOK_URL:
    abort("JUMMAH_HOOK secret not found. Add it in Repo Settings → Secrets → Actions.")
if not (WEBHOOK_URL.startswith("http://") or WEBHOOK_URL.startswith("https://")):
    abort(f"JUMMAH_HOOK looks invalid: {WEBHOOK_URL}")

content = "@here **🌙 JUMMAH MUBARAK 🌙**\n\nMake abundant salawat and dhikr. Recite Surah al-Kahf today."

embed = {
    "title": "Jummah Reminder",
    "description": (
        "**Qur'an 62:9**\n"
        "\"O you who believe! When the call is made for the prayer on Friday, hasten to the remembrance of Allah...\"\n\n"
        "**Hadith (Sahih Muslim):**\n"
        "\"The best day on which the sun has risen is Friday.\"\n\n"
        "**Sunnahs Today:**\n"
        "- Recite **Surah al-Kahf**.\n"
        "- Take **ghusl** and wear clean clothes.\n"
        "- Apply **perfume** (men).\n"
        "- Come early to Jumu'ah.\n"
        "- Make **dua** and send abundant **salawat**.\n"
    ),
    "color": 0x2ECC71,
    "timestamp": datetime.now(pytz.timezone("Asia/Kolkata")).isoformat()
}

payload = {
    "content": content,
    "embeds": [embed]
}

try:
    resp = requests.post(WEBHOOK_URL, json=payload, timeout=15)
    if resp.status_code in (200, 204):
        print("Jummah reminder sent successfully.")
    else:
        print(f"Failed — HTTP {resp.status_code}: {resp.text}")
        sys.exit(2)
except Exception as e:
    print("Request failed:", str(e))
    sys.exit(3)
