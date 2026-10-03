from utils.groq_client import get_groq_response


class ResponseAgent:

    def generate_response(self, user_input, final_context):

        prompt = f"""
You are a Smart City assistant for Hyderabad.

The user asked:
{user_input}

Here is the information collected by the Smart City system:

{final_context}

Give the user a clear and useful answer.

Rules:
- Use only the information provided above.
- Do not invent information.
- Do not mention internal agents, LangGraph, APIs, or implementation details.
- Keep the answer concise.
- If this is a travel planning request, clearly state the recommended departure time.
- If traffic information is available, mention traffic level and travel time.
- If weather information is available, mention the relevant weather and flood risk.
"""

        return get_groq_response(prompt)