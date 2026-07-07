import os
import requests

API_KEY = os.environ.get("TICKETMASTER_API_KEY")
URL = "https://app.ticketmaster.com/discovery/v2/events.json"



def find_events(city, keyword):
    params = {
        "apikey": API_KEY,
        "city": city,
        "keyword": keyword,
        "sort": "date,asc",
        "size": 20,
    }

    response = requests.get(URL, params=params)
    data = response.json()

    if "_embedded" not in data:
        return []

    events = []
    for event in data["_embedded"]["events"]:
        venue = event["_embedded"]["venues"][0]
        events.append(
            {
                "id": event["id"],
                "name": event["name"],
                "url": event["url"],
                "date": event["dates"]["start"]["localDate"],
                "venue": venue["name"],
                "city": venue["city"]["name"],
            }
        )
    return events
