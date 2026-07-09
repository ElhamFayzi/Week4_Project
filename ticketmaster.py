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

    try:
        response = requests.get(URL, params=params, timeout=10)
        data = response.json()
    except requests.RequestException:
        return []

    if "_embedded" not in data:
        return []

    events = []
    for event in data["_embedded"]["events"]:
        venues = event.get("_embedded", {}).get("venues", [])
        venue = venues[0] if venues else {}

        location = venue.get("location", {})
        latitude = location.get("latitude")
        longitude = location.get("longitude")

        events.append(
            {
                "id": event["id"],
                "name": event["name"],
                "url": event.get("url"),
                "date": event.get("dates", {}).get("start", {}).get("localDate"),
                "venue": venue.get("name"),
                "city": venue.get("city", {}).get("name"),
                "latitude": float(latitude) if latitude is not None else None,
                "longitude": float(longitude) if longitude is not None else None,
            }
        )
    return events
