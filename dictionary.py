# Placeholder for Lexin lookup & formatting (plug into main when ready).

import requests

LEXIN_URL = "https://editorportal.oslomet.no/api/v1/findwords"

def lookup_and_format(word: str) -> str:
    """
    Later: call Lexin API, parse top 3 results, and return a short multiline string.
    For now, just echo the word to keep the flow working.
    """
    word = (word or "").strip()
    if not word:
        return ""
    # Example shape (ready to fill in):
    # params = {
    #     "searchWord": word,
    #     "lang": "bokmål-english",
    #     "page": 1,
    #     "selectLang": "bokmål-english",
    #     "includeEngLang": 0,
    # }
    # r = requests.get(LEXIN_URL, params=params, headers={
    #     "Accept": "application/json, text/plain, */*",
    #     "Origin": "https://lexin.oslomet.no",
    #     "Referer": "https://lexin.oslomet.no/",
    #     "User-Agent": "norsk-lookup/0.1",
    # }, timeout=6)
    # r.raise_for_status()
    # data = r.json()
    # ...extract top3...
    return word
