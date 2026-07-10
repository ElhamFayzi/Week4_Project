# Event Whisperer

Event Whisperer is a Flask web application that finds upcoming events near you, enriches each one with a weather forecast and travel time, and uses Google's Gemini AI to rank and recommend those events based on your personal interests.

You tell it where you are and what you like; it shows you which events are worth your time, how far away they are, what the weather will be like, and why each one made the list.

---

## ✨ Features

- **Event search** : pulls up to 20 upcoming events for any city from [Ticketmaster](https://developer.ticketmaster.com/), filtered by the kind of event you want.
- **AI recommendations** : sends the events to Google Gemini, which ranks them from most to least relevant to your stated interests and explains *why* each one was recommended.
- **Weather forecast** : shows the daily forecast for each venue on the event date via [Open-Meteo](https://open-meteo.com/) (no API key needed).
- **Travel distance & time** : calculates driving distance and duration from you to each venue via [OpenRouteService](https://openrouteservice.org/).
- **Flexible location** : type a city (e.g. `Atlanta, GA`) or click **Use my location** to let the browser share your GPS position.
- **Local caching** : stores each search's results in a local SQLite database (`instance/eventdata.db`) via SQLAlchemy, cleared and refreshed on every new search.

---

## 🧱 How It Works

```
                ┌───────────────┐     ┌──────────────┐     ┌────────────────┐
  user input →  │ ticketmaster  │ →   │   database   │ →   │     genai      │ → ranked results
  (event type,  │  + weather    │     │  (SQLite via │     │   (Gemini AI)  │   (web page)
   location,    │  + maps       │     │  SQLAlchemy) │     └────────────────┘
   interest)    └───────────────┘     └──────────────┘
```

1. **`app.py`** receives the search form, and `resolve_origin` turns your location into coordinates — either by geocoding the text you typed or reverse-geocoding your GPS position.
2. **`ticketmaster.py`** queries the Ticketmaster Discovery API for events in the given city and event type.
3. For each event, **`weather.py`** fetches a forecast for the venue and **`maps.py`** calculates travel distance/time from you — all stored in `eventdata.db`.
4. **`genai.py`** reads the stored events, builds a prompt with your interests, and asks Gemini to rank them and explain each recommendation.
5. **`app.py`** renders the ranked events, forecasts, and travel details on the results page.

---

## 📂 Project Structure

| File | Description |
|------|-------------|
| `app.py` | Entry point : Flask app, database models, routes, and the search → enrich → rank pipeline. |
| `ticketmaster.py` | Fetches events from the Ticketmaster Discovery API. |
| `geocode.py` | Forward and reverse geocoding via OpenRouteService. |
| `maps.py` | Driving distance and travel time via OpenRouteService. |
| `weather.py` | Daily weather forecast for each venue via Open-Meteo. |
| `genai.py` | Builds the prompt and calls the Google Gemini API for ranking and reasons. |
| `templates/` | `index.html` (search form) and `results.html` (ranked results). |
| `static/style.css` | Page styling. |
| `unittests.py` | Unit tests for the app and each service module. |
| `requirements.txt` | Python dependencies. |
| `instance/eventdata.db` | SQLite database file (created/populated at runtime). |

---

## 🛠️ Prerequisites

- **Python 3.10+**
- A **Ticketmaster API key** : get one from the [Ticketmaster Developer Portal](https://developer.ticketmaster.com/).
- A **Google Gemini API key** : get one from [Google AI Studio](https://aistudio.google.com/apikey).
- An **OpenRouteService API key** : get one from the [OpenRouteService dashboard](https://openrouteservice.org/dev/#/signup) (used for geocoding and travel time).

> Open-Meteo (weather) requires no API key.

--- 

## 🚀 Setup & Installation

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd Week4_Project
   ```

2. **(Optional) Create and activate a virtual environment (to avoid installing packages on global Python environment)**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set your API keys as environment variables**

   ```bash
   export TICKETMASTER_API_KEY="your_ticketmaster_key_here"
   export GENAI_KEY="your_gemini_key_here"
   export ORS_API_KEY="your_openrouteservice_key_here"
   ```

   > Tip: To avoid re-exporting these every session, add them to your shell profile
   > (`~/.zshrc` / `~/.bashrc`) and `source` it, or place them in a `.env` file (already
   > git-ignored) — it's loaded automatically at startup via `python-dotenv`:
   >
   > ```env
   > TICKETMASTER_API_KEY=your_ticketmaster_key_here
   > GENAI_KEY=your_gemini_key_here
   > ORS_API_KEY=your_openrouteservice_key_here
   > ```

---

## ▶️ Usage

Run the application from the project root:

```bash
python app.py
```

Then open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser. The SQLite
database is created automatically on first run.

You'll be asked for:

- **What kind of events?** : e.g. `concerts`, `comedy`, `sports`
- **Your location** : type a city (e.g. `Atlanta, GA`) or click **Use my location** for GPS
- **What are you into?** : used to rank events, e.g. `90s hip-hop, female vocalists, indie`

Event Whisperer lists the events it found, each with its date, venue, forecast, and travel time, ranked from most to least relevant, with a one-sentence reason for each placement.

---

## 🌐 Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `TICKETMASTER_API_KEY` | ✅ | API key for the Ticketmaster Discovery API. |
| `GENAI_KEY` | ✅ | API key for the Google Gemini API. |
| `ORS_API_KEY` | ✅ | API key for OpenRouteService (geocoding + travel time). |

---

## 🧪 Running Tests

```bash
python -m unittest unittests.py
```

This covers:

- `test_index` / `test_results` : verify the Flask routes render the expected pages.
- `get_weather_forecast` : verifies the Open-Meteo forecast is parsed correctly.
- `geocode` : verifies a city name resolves to the expected coordinates.
- `get_distance_and_time` : verifies travel distance and duration are returned.
- `find_events` : verifies the Ticketmaster response is parsed into the expected structure.

> Note: These make **live calls** to the external APIs, so valid API keys and network access are required to run them.

---

## 🧰 Tech Stack

**Language & runtime**

- **Python 3.13** : core language
- **[Flask]** : web framework serving the search form and results pages

**External APIs / Services**

- **[Ticketmaster API]** : source of upcoming event data (search by city and event type)
- **[Google Gemini API]** (`gemini-2.5-flash`) : ranks events and generates personalized recommendations
- **[OpenRouteService API]** : geocoding, reverse geocoding, and driving distance/time
- **[Open-Meteo API]** : daily weather forecast per venue (no key required)

**Libraries**

- **[requests]** : HTTP calls to the external APIs
- **[Flask-SQLAlchemy]** / **[SQLAlchemy]** : database toolkit and ORM
- **[SQLite]** : lightweight local database for caching each search (`eventdata.db`)
- **[google-genai]** : official Python client for the Google Gemini API
- **[python-dotenv]** : loads API keys from a `.env` file

**Tooling**

- **[unittest]** : testing
- **[venv]** : virtual environment / dependency isolation

---

## 👥 Authors

Built by **Elham Fayzi**, **Jacob Sotunde**, and **Ricardo Bezi**.
