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


# def get_hadiths(api_url, params, retries=3, backoff_factor=0.3):
#     for attempt in range(retries):
#         try:
#             full_url = f"{api_url}?{requests.compat.urlencode(params)}"
#             print(f"Attempting URL: {full_url}")  # Debugging output
#             response = requests.get(full_url)
#             response.raise_for_status()
#             return response.json()
#         except requests.exceptions.RequestException as error:
#             print(f"Attempt {attempt + 1} failed: {error}")
#             sleep(backoff_factor * (2 ** attempt))
#     return None



def get_random_hadith():
    random_narrator = random.choice(list(narrators.keys()))
    random_status = random.choice(hadith_status)

    print(f"Selected Narrator: {random_narrator}, Status: {random_status}")
    print(getenv("API_KEY"))
    params = {
        'apiKey': getenv("API_KEY"),
        'book': narrators[random_narrator],
        # 'status': random_status,
        'paginate': 1
    }

    response = requests.get(api_url, params)
    data = response.json()
    if data:
        if data['status'] == 200 and 'hadiths' in data and 'data' in data['hadiths']:
            hadiths = data['hadiths']['data']
            if hadiths:
                for hadith in hadiths:
                    print(hadith)
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
