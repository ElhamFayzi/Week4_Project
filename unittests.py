
import unittest
from app import app
import maps
import geocode
import weather
import ticketmaster

class BasicTests(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_index(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Event Finder', response.data)

    def test_results(self):
        response = self.app.post('/results', data=dict(interest='music', location='New York'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'music', response.data)
        self.assertIn(b'New York', response.data)
class WeatherTests(unittest.TestCase):
    def test_get_weather_forecast(self):
        lat, lon = 33.7554, -84.4019   
        date = '2026-07-15'
        forecast = weather.get_weather_forecast(lat, lon, date)
        self.assertIn('date', forecast)
        self.assertIn('temp_max_f', forecast)
        self.assertIn('temp_min_f', forecast)
        self.assertIn('precipitation_probability', forecast)
        self.assertIn('weather_code', forecast)
class TestGeocode(unittest.TestCase):
    def test_geocode(self):
        location = "Atlanta, GA"
        result = geocode.geocode(location)
        result["lat"] = round(result["lat"], 4)
        result["lon"] = round(result["lon"], 4)
        self.assertEqual(round(result['lat'], 1), 33.8)
        self.assertEqual(round(result['lon'], 1), -84.4)
class TestDistanceAndTime(unittest.TestCase):
    def test_get_distance_and_time(self):
        user_lat, user_lon = 33.7554, -84.4019  
        venue_lat, venue_lon = 33.7490, -84.3880  
        result = maps.get_distance_and_time(user_lat, user_lon, venue_lat, venue_lon)
        self.assertIn('distance_mi', result)
        self.assertIn('duration_min', result)
class TestFindEvents(unittest.TestCase):
    def test_find_events(self):
        city = "Atlanta"
        interest = "music"
        events = ticketmaster.find_events(city, interest)
        self.assertIsInstance(events, list)
        for event in events:
            self.assertIn('name', event)
            self.assertIn('date', event)
            self.assertIn('venue', event)
            self.assertIn('city', event)
            self.assertIn('latitude', event)
            self.assertIn('longitude', event)
        
        