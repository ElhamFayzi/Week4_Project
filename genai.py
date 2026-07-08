import os
import json

from google import genai

client = genai.Client(api_key=os.getenv("GENAI_KEY"))

RESPONSE_STRUCTURE = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "id": {"type": "integer"},
            "reason": {"type": "string"},
        },
        "required": ["id", "reason"],
    },
}


def build_prompt(events, interest):
    lines = [
        f"- id={event['id']}: {event['name']} on {event['date']} at {event['venue']}, {event['city']}"
        for event in events
    ]
    event_block = "\n".join(lines)

    return f"""You are an event recommendation assistant. The user is interested in: {interest}.
                1. Rank the events below from most to least relevant to that interest. 
                2. For each event, give a short one-sentence reason for its placement. 
                3. Include every event exactly once.
                4. Return a JSON array, most relevant first, where each item is:
                {{"id": <the event id>, "reason": "<one sentence>"}}

                Events:
                {event_block}
            """


def rank_events(events, interest):
    if not events:
        return []

    prompt = build_prompt(events, interest)

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_schema": RESPONSE_STRUCTURE,
            },
        )
        return json.loads(response.text)
    except Exception:
        return [{"id": e["id"], "reason": ""} for e in events]
