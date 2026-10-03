from agents.planner_agent import PlannerAgent

planner = PlannerAgent()

trip = [
    {
        "name": "College",
        "travel_time": 20,
        "arrival_time": "09:00"
    },
    {
        "name": "Hospital",
        "travel_time": 15,
        "arrival_time": "09:30"
    },
    {
        "name": "Shopping Mall",
        "travel_time": 25,
        "arrival_time": "10:00"
    }
]

result = planner.calculate_departure(
    destinations=trip,
    traffic="heavy",
    weather="rain"
)

print(result)