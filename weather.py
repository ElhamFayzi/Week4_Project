import requests

URL = 'https://api.open-meteo.com/v1/forecast'

WEATHER_CODES = {
    0: 'Clear sky',
    1: 'Mainly clear',
    2: 'Partly cloudy',
    3: 'Overcast',
    45: 'Fog',
    48: 'Depositing rime fog',
    51: 'Light drizzle',
    53: 'Moderate drizzle',
    55: 'Dense drizzle',
    56: 'Light freezing drizzle',
    57: 'Dense freezing drizzle',
    61: 'Slight rain',
    63: 'Moderate rain',
    65: 'Heavy rain',
    66: 'Light freezing rain',
    67: 'Heavy freezing rain',
    71: 'Slight snowfall',
    73: 'Moderate snowfall',
    75: 'Heavy snowfall',
    77: 'Snow grains',
    80: 'Slight rain showers',
    81: 'Moderate rain showers',
    82: 'Violent rain showers',
    85: 'Slight snow showers',
    86: 'Heavy snow showers',
    95: 'Thunderstorm',
    96: 'Thunderstorm with slight hail',
    99: 'Thunderstorm with heavy hail',
}

def get_weather_forecast(lat, lon, date):
    params = {
        'latitude': lat,
        'longitude': lon,
        'daily': [
            'weather_code',
            'temperature_2m_max',
            'temperature_2m_min',
            'precipitation_probability_max',
        ],
        'start_date': date,
        'end_date': date,
        'timezone': 'auto',
        'temperature_unit': 'fahrenheit',
    }

    try:
        response = requests.get(URL, params=params, timeout=10)
    except requests.RequestException:
        return {'error': 'Weather service unreachable'}

    if not response.ok:
        if response.status_code == 400 and 'out of allowed range' in response.text:
            return {'error': 'Forecast not available this far in advance'}
        return {'error': f'Weather request failed ({response.status_code})'}

    data = response.json()

    daily = data.get('daily')
    if not daily or not daily.get('time'):
        return {'error': f'No forecast available for {date} at this location'}

    code = daily['weather_code'][0]
    return {
        'date': daily['time'][0],
        'temp_max_f': daily['temperature_2m_max'][0],
        'temp_min_f': daily['temperature_2m_min'][0],
        'precipitation_probability': daily['precipitation_probability_max'][0],
        'weather_code': code,
        'description': WEATHER_CODES.get(code, 'Unknown'),
    }