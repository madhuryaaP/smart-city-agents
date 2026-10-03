from graph.workflow import graph
from utils.groq_client import generate_response

state = {
    "question": "I need to reach college by 10 AM",

    "destinations": [
        {
            "name": "College",
            "travel_time": 20,
            "arrival_time": "10:00"
        }
    ],

    "traffic": {},
    "water": {},
    "planner": {},
    "infrastructure": {},
    "pollution": {},
    "final_context": ""
}

result = graph.invoke(state)

answer = generate_response(
    result["final_context"],
    state["question"]
)

print(answer)