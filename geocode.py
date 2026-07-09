import os
import requests

URL = 'https://api.openrouteservice.org/geocode/search'
REVERSE_URL = 'https://api.openrouteservice.org/geocode/reverse'
API_KEY = os.environ.get("ORS_API_KEY")


def geocode(place):
    if not API_KEY:
        return {'error': 'ORS_API_KEY is not set'}

    params = {
        'api_key': API_KEY,
        'text': place,
        'size': 1,  # only need the top match
    }

    try:
        response = requests.get(URL, params=params, timeout=10)
    except requests.RequestException:
        return {'error': 'Geocoding service unreachable'}

    if not response.ok:
        return {'error': f'Geocoding request failed ({response.status_code})'}

    data = response.json()

    features = data.get('features')
    if not features:
        return {'error': f'No location found for "{place}"'}

    lon, lat = features[0]['geometry']['coordinates']
    return {'lat': lat, 'lon': lon}


def reverse_geocode(lat, lon):
    if not API_KEY:
        return None

    params = {
        'api_key': API_KEY,
        'point.lat': lat,
        'point.lon': lon,
        'size': 1,
    }

    try:
        response = requests.get(REVERSE_URL, params=params, timeout=10)
    except requests.RequestException:
        return None

    if not response.ok:
        return None

    features = response.json().get('features')
    if not features:
        return None

    props = features[0].get('properties', {})
    return props.get('locality') or props.get('region') or props.get('label')
