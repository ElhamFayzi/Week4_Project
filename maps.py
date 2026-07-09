import os
import requests

# Right now, "driving-car" is the routing profile; 
# swap for "foot-walking", "cycling-regular", etc. for other modes.
URL = 'https://api.openrouteservice.org/v2/matrix/driving-car'
API_KEY = os.environ.get("ORS_API_KEY")

def get_distance_and_time(user_lat, user_lon, venue_lat, venue_lon):
    if not API_KEY:
        return {'error': 'ORS_API_KEY is not set'}
    
    headers = {
        'Authorization': API_KEY,
        'Content-Type': 'application/json'
    }

    contents = {
        'locations': [[user_lon, user_lat],
                      [venue_lon, venue_lat]],
        'sources': [0],
        'destinations': [1],
        'metrics': ['distance', 'duration'],
        'units': 'mi'
    }

    try:
        response = requests.post(URL, json=contents, headers=headers, timeout=10)
    except requests.RequestException:
        return {'error': 'Routing service unreachable'}

    if not response.ok:
        return {'error': f'Routing request failed ({response.status_code})'}

    data = response.json()

    distance_mi = data['distances'][0][0]
    duration_s = data['durations'][0][0]

    if distance_mi is None or duration_s is None:
        return {'error': 'No route found between the given points'}

    return {
        'distance_mi': round(distance_mi, 2),
        'duration_min': round(duration_s / 60, 1),
        'distance_m': round(distance_mi * 1609.34),
        'duration_s': round(duration_s)
    }