import random
from os import getenv

import requests
from dotenv import load_dotenv

load_dotenv()
api_url = "https://hadithapi.com/api/hadiths/"

narrators = {
    "Sahih Bukhari": "sahih-bukhari",
    "Sahih Muslim": "sahih-muslim",
    "Jami' Al-Tirmidhi": "al-tirmidhi",
    "Sunan Abu Dawood": "abu-dawood",
    "Sunan Ibn-e-Majah": "ibn-e-majah",
    "Sunan An-Nasa`i": "sunan-nasai",
    "Mishkat Al-Masabih": "mishkat",
}


def get_random_hadith():
    """ """
    random_narrator = random.choice(list(narrators.keys()))
    # random_status = random.choice(hadith_status)
    random_page = random.randint(1, 1000)
    params = {
        "apiKey": getenv("API_KEY"),
        "book": narrators[random_narrator],
        # 'status': random_status,
        "paginate": random_page,
    }

    response = requests.get(api_url, params)
    data = response.json()
    if data:
        if data["status"] == 200 and "hadiths" in data and "data" in data["hadiths"]:
            hadiths = data["hadiths"]["data"]
            if hadiths:
                for hadith in hadiths:
                    return {
                        "arabic": hadith["hadithArabic"],
                        "english": hadith["hadithEnglish"],
                        "narrator": hadith["englishNarrator"],
                    }
            else:
                print("No Hadiths found.")
        else:
            print("No Hadiths found.")
    else:
        print("Failed to retrieve Hadiths after multiple attempts.")


# print(get_random_hadith().get('arabic'))
