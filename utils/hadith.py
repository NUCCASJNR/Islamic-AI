import requests
import random
from time import sleep
from os import getenv
from dotenv import load_dotenv
load_dotenv()
api_url = 'https://hadithapi.com/api/hadiths/'

narrators = {
    'Sahih Bukhari': 'sahih-bukhari',
    'Sahih Muslim': 'sahih-muslim',
    "Jami' Al-Tirmidhi": "al-tirmidhi",
    "Sunan Abu Dawood": "abu-dawood",
    "Sunan Ibn-e-Majah": "ibn-e-majah",
    "Sunan An-Nasa`i": "sunan-nasai",
    "Mishkat Al-Masabih": "mishkat"
}

hadith_status = ["Sahih", "Hasan"]


def get_random_hadith():
    random_narrator = random.choice(list(narrators.keys()))
    random_status = random.choice(hadith_status)

    print(f"Selected Narrator: {random_narrator}, Status: {random_status}")
    params = {
        'apiKey': getenv("API_KEY"),
        'book': narrators[random_narrator],
        # 'status': random_status,
        'paginate': 500
    }

    response = requests.get(api_url, params)
    data = response.json()
    if data:
        if data['status'] == 200 and 'hadiths' in data and 'data' in data['hadiths']:
            hadiths = data['hadiths']['data']
            if hadiths:
                for hadith in hadiths:
                    return {
                        'arabic': hadith['hadithArabic'],
                        'english': hadith['hadithEnglish'],
                        "narrator": hadith['englishNarrator']
                    }
            else:
                print("No Hadiths found.")
        else:
            print("No Hadiths found.")
    else:
        print("Failed to retrieve Hadiths after multiple attempts.")


print(get_random_hadith())
