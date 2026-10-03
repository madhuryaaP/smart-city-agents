import os
import json
import re

from groq import Groq
from dotenv import load_dotenv


load_dotenv()


# ================================================================
# GROQ CLIENT
# ================================================================

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


# ================================================================
# QUERY PARSER
# ================================================================

def parse_user_query(
    question: str,
    history: list = None
) -> dict:

    history_context = ""

    if history and len(history) > 0:

        history_lines = []

        for msg in history[-4:]:

            role = msg.get(
                "role",
                "user"
            )

            text = msg.get(
                "text",
                ""
            )

            history_lines.append(
                f"{role.capitalize()}: {text}"
            )

        history_context = (
            "Recent conversation context:\n"
            + "\n".join(history_lines)
            + "\n\n"
        )

    system_prompt = """
You are an NLP understanding assistant for
Hyderabad Smart City AI.

Your job is to understand the user's question,
correct spelling mistakes and typos, identify
the relevant smart-city domains, and extract
locations and arrival times.

SUPPORTED DOMAINS:

1. planner
2. traffic
3. water
4. pollution
5. infrastructure
6. general

DOMAIN MEANINGS:

planner:
Route planning, reaching somewhere,
departure time, arrival time.

traffic:
Traffic, congestion, road traffic,
commute conditions.

water:
Weather, rain, rainfall, temperature,
humidity, waterlogging, flooding.

pollution:
AQI, air pollution, air quality,
smog, emissions.

infrastructure:
Potholes, damaged roads, broken streetlights,
civic problems.

general:
Greetings and general questions.

IMPORTANT:

A question can contain multiple domains.

Example:

"How is traffic and weather from LB Nagar
to Hitech City?"

Return:

{
    "domains": ["traffic", "water"]
}

Another example:

"Check pollution and traffic in Madhapur"

Return:

{
    "domains": ["pollution", "traffic"]
}

Another:

"Plan my trip from LB Nagar to Gachibowli
and tell me about the weather"

Return:

{
    "domains": ["planner", "traffic", "water"]
}

Understand natural language even if sentence
structure is different.

Correct common spelling mistakes.

Examples:

Hitech City
HITEC City
Hi Tech City

Gachibowli
Kukatpally
KPHB
Madhapur
Kothapet
LB Nagar
Dilsukhnagar
Secunderabad
Banjara Hills
Jubilee Hills
Charminar
Begumpet
Mehdipatnam
KMIT

Return ONLY valid JSON.

Format:

{
    "corrected_query": "...",
    "domains": ["traffic"],
    "source": null,
    "destination": null,
    "arrival_time": null
}
"""

    user_content = (
        history_context
        + "User Query: "
        + question
    )

    try:

        response = client.chat.completions.create(

            model="openai/gpt-oss-20b",

            messages=[

                {
                    "role": "system",
                    "content": system_prompt
                },

                {
                    "role": "user",
                    "content": user_content
                }

            ],

            temperature=0.0
        )

        content = (
            response.choices[0]
            .message
            .content
            .strip()
        )

        # Remove markdown code fences
        if content.startswith("```"):

            content = re.sub(
                r"^```(?:json)?\s*",
                "",
                content
            )

            content = re.sub(
                r"\s*```$",
                "",
                content
            )

        parsed = json.loads(
            content
        )

        return parsed

    except Exception as e:

        print(
            "[Groq Parser Error]:",
            str(e)
        )

        # Safe fallback
        return {

            "corrected_query":
                question,

            "domains":
                ["general"],

            "source":
                None,

            "destination":
                None,

            "arrival_time":
                None
        }


# ================================================================
# RESPONSE GENERATOR
# ================================================================

def generate_response(
    context: str,
    question: str,
    history: list = None
) -> str:

    history_text = ""

    if history and len(history) > 0:

        history_lines = []

        for msg in history[-4:]:

            if msg.get("role") == "user":

                role = "Citizen"

            else:

                role = "Assistant"

            text = msg.get(
                "text",
                ""
            )

            history_lines.append(
                f"{role}: {text}"
            )

        history_text = (
            "PREVIOUS CONVERSATION:\n"
            + "\n".join(history_lines)
            + "\n\n"
        )

    # ============================================================
    # IMPORTANT RESPONSE RULES
    # ============================================================

    system_prompt = """
You are the Smart City Assistant for Hyderabad.

Answer the citizen's question using ONLY the
information available in the Context.

Do NOT invent information.

================================================
DATA AVAILABILITY RULES
================================================

These rules are extremely important.

1. Empty dictionaries are NOT data.

2. None is NOT data.

3. null is NOT data.

4. "Unknown" is NOT data.

5. "Unavailable" is NOT data.

6. Error messages are NOT usable data.

7. If an agent did not provide useful information,
   completely OMIT that section.

8. NEVER write:

   AQI: Unknown

9. NEVER write:

   Weather: Unknown

10. NEVER write:

   Traffic: Unknown

11. NEVER write:

   Infrastructure: Unknown

12. Do not create fake values to fill missing
    fields.

13. Do not assume a value when it is missing.

================================================
AVAILABLE SECTIONS
================================================

Only use these sections when actual useful
data exists.

🚦 Traffic & Route

🌦️ Weather & Flooding

🍃 Air Quality (AQI)

🛠️ Civic & Road Status

💡 Smart Recommendations

================================================
TRAFFIC
================================================

If actual traffic information exists, show:

• Location OR route
• Current speed if available
• Free-flow speed if available
• Traffic level
• Travel time if available
• Traffic delay if available

For routes, show source and destination.

================================================
WEATHER
================================================

If actual weather information exists, show:

• Location
• Temperature
• Humidity
• Weather condition
• Rainfall
• Flood risk

================================================
POLLUTION
================================================

If actual pollution information exists, show:

• AQI
• PM2.5 if available
• PM10 if available
• Other available pollutants

If pollution information does NOT exist,
do NOT mention AQI at all.

================================================
INFRASTRUCTURE
================================================

If actual infrastructure information exists,
show only the available information.

================================================
RECOMMENDATIONS
================================================

Only provide recommendations when they are
supported by the available data.

Do not create generic recommendations just
because a section is missing.

================================================
FORMAT
================================================

Start with:

📌 Summary

Then include ONLY the relevant sections.

Use short bullet points.

Keep the response easy to read on a mobile app.

Do not mention:

• Groq
• LangGraph
• APIs
• backend
• agents
• implementation
• internal processing

Do not expose technical implementation details.

================================================
FACTUAL ACCURACY
================================================

Use ONLY information explicitly available
in the Context.

Keep numbers exactly consistent with the Context.

Do not change weather descriptions.

Do not create information that is not present.
"""

    user_content = (
        history_text
        + "CITIZEN QUESTION:\n"
        + question
        + "\n\n"
        + "SMART CITY CONTEXT:\n"
        + (
            context
            if context and context.strip()
            else "No specific data is available."
        )
    )

    try:

        response = client.chat.completions.create(

            model="openai/gpt-oss-20b",

            messages=[

                {
                    "role": "system",
                    "content": system_prompt
                },

                {
                    "role": "user",
                    "content": user_content
                }

            ],

            temperature=0.2
        )

        answer = (
            response.choices[0]
            .message
            .content
            .strip()
        )

        return answer

    except Exception as e:

        print(
            "[Groq Response Error]:",
            str(e)
        )

        return (
            "📌 **Smart City Assistant**\n\n"
            "I could not retrieve the latest "
            "information right now. Please try again."
        )


# ================================================================
# GENERAL GROQ HELPER
# ================================================================

def get_groq_response(
    prompt: str
) -> str:

    try:

        response = client.chat.completions.create(

            model="openai/gpt-oss-20b",

            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],

            temperature=0.3
        )

        return (
            response.choices[0]
            .message
            .content
            .strip()
        )

    except Exception as e:

        print(
            "[Groq Helper Error]:",
            str(e)
        )

        return (
            "I am currently unable "
            "to process your request."
        )