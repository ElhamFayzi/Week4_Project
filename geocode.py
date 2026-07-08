# This adds geocoding functionality using OpenRouteService API to 
# convert a location strings into coordinates we could use for other
# modules

import os
import requests

URL = 'https://api.openrouteservice.org/geocode/search'
API_KEY = os.environ.get("ORS_API_KEY")


def geocode(place):
    """Convert a location string (e.g. 'Atlanta, GA') into lat/lon."""
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
