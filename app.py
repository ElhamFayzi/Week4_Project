from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

from ticketmaster import find_events
from geocode import geocode
from maps import get_distance_and_time
from weather import get_weather_forecast
from genai import rank_events

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///eventdata.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class Weather(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    temp_max_f = db.Column(db.Float)
    temp_min_f = db.Column(db.Float)
    precipitation_probability = db.Column(db.Integer)
    weather_code = db.Column(db.Integer)
    description = db.Column(db.String(200))


class Event(db.Model):
    """A Ticketmaster event, enriched with distance + a weather forecast."""

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    url = db.Column(db.String(300))
    date = db.Column(db.String(20))
    venue = db.Column(db.String(200))
    city = db.Column(db.String(100))
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)

    distance_mi = db.Column(db.Float, nullable=True)
    duration_min = db.Column(db.Float, nullable=True)

    rank = db.Column(db.Integer, nullable=True)
    reason = db.Column(db.String(500), nullable=True)

    weather_id = db.Column(db.Integer, db.ForeignKey("weather.id"), nullable=True)
    forecast = db.relationship("Weather", backref="events", lazy=True)


def run_pipeline(interest, location):
    # Because DB is a cache of the latest search, so clear the previous one first so they don't interfere with new searches.
    Event.query.delete()
    Weather.query.delete()
    db.session.commit()

    user = geocode(location)
    user_lat = user.get("lat")
    user_lon = user.get("lon")

    city = location.split(",")[0].strip()
    events = find_events(city, interest)

    for event in events:
        has_coords = event["latitude"] is not None and event["longitude"] is not None

        # Forecast for the venue on the event date
        forecast = None
        if has_coords:
            weather = get_weather_forecast(event["latitude"], event["longitude"], event["date"])
            if "error" not in weather:
                forecast = Weather(
                    temp_max_f=weather["temp_max_f"],
                    temp_min_f=weather["temp_min_f"],
                    precipitation_probability=weather["precipitation_probability"],
                    weather_code=weather["weather_code"],
                    description=weather["description"],
                )
                db.session.add(forecast)

        # distance/time from the user to the venue
        distance_mi = duration_min = None
        if has_coords and user_lat is not None and user_lon is not None:
            d = get_distance_and_time(user_lat, user_lon, event["latitude"], event["longitude"])
            if "error" not in d:
                distance_mi = d["distance_mi"]
                duration_min = d["duration_min"]

        db.session.add(
            Event(
                name=event["name"],
                url=event["url"],
                date=event["date"],
                venue=event["venue"],
                city=event["city"],
                latitude=event["latitude"],
                longitude=event["longitude"],
                distance_mi=distance_mi,
                duration_min=duration_min,
                forecast=forecast,
            )
        )

    db.session.commit()

    rank_stored_events(interest)


def rank_stored_events(interest):
    stored = Event.query.all()
    event_dicts = [
        {
            "id": event.id,
            "name": event.name,
            "date": event.date,
            "venue": event.venue,
            "city": event.city,
        }
        for event in stored
    ]

    ranking = rank_events(event_dicts, interest)
    by_id = {event.id: event for event in stored}

    position = 0
    ranked_ids = set()
    for item in ranking:
        event = by_id.get(item.get("id"))
        if event is not None and event.id not in ranked_ids:
            position += 1
            event.rank = position
            event.reason = item.get("reason", "")
            ranked_ids.add(event.id)

    for event in stored:
        if event.id not in ranked_ids:
            position += 1
            event.rank = position

    db.session.commit()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/results", methods=["POST"])
def results():
    interest = request.form.get("interest", "")
    location = request.form.get("location", "")

    run_pipeline(interest, location)
    events = Event.query.order_by(Event.rank).all()

    return render_template(
        "results.html", interest=interest, location=location, events=events
    )


with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True)
