from typing import TypedDict, List, Dict


class SmartCityState(TypedDict, total=False):

    # User input
    user_input: str

    # Route information
    source: str
    destination: str
    arrival_time: str
    route_destinations: List[str]

    # Agents selected by router
    selected_agents: List[str]

    # Agent outputs
    destinations: List[Dict]
    planner: Dict
    traffic: Dict
    water: Dict
    pollution: Dict
    infrastructure: Dict

    # History and normalized input
    history: List[Dict]
    normalized_query: str

    # Final response
    final_context: str
    final_response: str