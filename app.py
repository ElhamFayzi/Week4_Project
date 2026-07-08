from flask import Flask
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///eventdata.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
class Weather(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    temperature = db.Column(db.Float, nullable=False)
    humidity = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200), nullable=False)

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(200), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    venue = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    forecast = db.relationship('Weather', backref='event', lazy=True)
    weather_id = db.Column(db.Integer, db.ForeignKey('weather.id'), nullable=True)
def init_database():
    db.create_all()

@app.route('/')
def index():
    return "Test"

if __name__ == "__main__":
    with app.app_context():
        init_database()
    app.run(debug=True)
from flask import Flask, render_template, request

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/results", methods=["POST"])
def results():
    # For now this just passes the form input through so the page renders.
    # Will wire the pipeline (geocode -> ticketmaster -> maps + weather -> ranking)
    # in here next

    interest = request.form.get("interest", "")
    location = request.form.get("location", "")

    return render_template("results.html", interest=interest, location=location)


if __name__ == "__main__":
    app.run(debug=True)
