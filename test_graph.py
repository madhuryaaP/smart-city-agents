from graph.workflow import graph

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

print(result["final_context"])