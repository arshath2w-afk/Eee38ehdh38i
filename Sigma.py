import requests
import os

WEBHOOK_URL = os.getenv("WEEBHOOK_URL")

message = """
**🌙 JUMMAH MUBARAK 🌙**

**Qur'an 62:9:**  
> *“O you who believe! When the call is made for the prayer on Friday, hasten to the remembrance of Allah…”*

**Sahih Muslim:**  
> *“The best day on which the sun has risen is Friday.”*

**Sunan Abu Dawud (Sahih):**  
> *“Send abundant salawat upon me on Fridays.”*

---

## 🌿 **Sunnahs of Jummah**
- Recite **Surah al-Kahf**  
- Take **ghusl**  
- Wear **clean clothes**  
- Apply **perfume** (for men)  
- Go early to the masjid  
- Send plenty of **salawat**  
- Make **dua**, especially before Maghrib  
- Read Surah **As-Sajdah** & **Al-Insan** in Fajr (Sunnah of the Prophet ﷺ)

---

## 🤲 **Dua Reminder**
Use today to seek forgiveness, increase dhikr, and make heartfelt dua.  
May Allah accept your deeds and grant you barakah.

**Jummah Mubarak!**
"""

requests.post(WEBHOOK_URL, json={"content": message})
