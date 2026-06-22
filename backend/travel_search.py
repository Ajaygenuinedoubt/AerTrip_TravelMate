import requests
from backend.config import SERPER_API_KEY

def travel_search(query):

    url = "https://google.serper.dev/search"

    headers = {
        "X-API-KEY": SERPER_API_KEY,
        "Content-Type": "application/json"
    }

    payload = {
        "q": query
    }

    response = requests.post(
        url,
        headers=headers,
        json=payload
    )

    return response.json()
