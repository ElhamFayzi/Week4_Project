import os
import sqlalchemy as db
from google import genai

my_api_key = os.getenv("GENAI_KEY")
client = genai.Client(api_key=my_api_key)
engine = db.create_engine("sqlite:///eventcache.db")


def get_events_from_db():
    with engine.connect() as connection:
        rows = connection.execute(
            db.text("SELECT id, name, url, date, venue, city FROM event")
        ).fetchall()
    return rows


def build_prompt(events, user_interests):
    texts = ""
    for i, event in enumerate(events, 1):
        event_id, name, url, date, venue, city = event
        texts += f"""
                Event {i}:
                - Name: {name}
                - date: {date}
                - venue: {venue}
                - city: {city}
                - URL: {url}
                """

    prompt =  f"""You are an event recommendation assistant. The user is interested in: {user_interests}. Below is a list of upcoming events. Please:
                1. rank the events from most to least relevant based on the user's interests.
                2. for each event give a short 1 sentence explanation of why you recommended it
                3. Please format your response cleanly using a numbered list.
                4. Start your answer with 'Here are the events ranked from most to least relevant based on your interest in (rephrase the user's interest)':

                Events: {texts}
               """
    return prompt


def get_recommendation(user_interests):
    events = get_events_from_db()
    prompt = build_prompt(events, user_interests)

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
        )
    except Exception:
        return "Sorry, the recommendation service is currently unavailable. Please try again in a moment."

    return response.text
