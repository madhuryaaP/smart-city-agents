import re
from typing import List

from langgraph.graph import StateGraph, END

# IMPORTANT: SmartCityState must be imported
from graph.state import SmartCityState

from agents.planner_agent import PlannerAgent
from agents.traffic_agent import TrafficAgent
from agents.water_agent import WaterAgent

from agents.pollution_agent import pollution_agent
from agents.infrastructure_agent import infrastructure_agent

from utils.groq_client import generate_response, parse_user_query


# ============================================================
# AGENT OBJECTS
# ============================================================

planner_agent = PlannerAgent()
traffic_agent = TrafficAgent()
water_agent = WaterAgent()


# ============================================================
# EXTRACT SOURCE, DESTINATION AND TIME
# ============================================================

def extract_location_from_question(
    question: str
):

    q = question.strip()

    # --------------------------------------------------------
    # FORMAT 1:
    #
    # reach DESTINATION from SOURCE by TIME
    #
    # Example:
    # reach Hitech City from LB Nagar by 9 AM
    # --------------------------------------------------------

    pattern1 = re.search(
        r"reach\s+(.+?)\s+from\s+(.+?)\s+by\s+"
        r"(\d{1,2}(?::\d{2})?\s*(?:am|pm))",
        q,
        re.IGNORECASE
    )

    if pattern1:

        destination = pattern1.group(1).strip()

        source = pattern1.group(2).strip()

        arrival_time = pattern1.group(3).strip()

        return (
            destination,
            source,
            arrival_time
        )

    # --------------------------------------------------------
    # FORMAT 2:
    #
    # reach DESTINATION by TIME from SOURCE
    #
    # Example:
    # reach KMIT by 9 AM from LB Nagar
    # --------------------------------------------------------

    pattern2 = re.search(
        r"reach\s+(.+?)\s+by\s+"
        r"(\d{1,2}(?::\d{2})?\s*(?:am|pm))"
        r"\s+from\s+(.+?)(?=\s+(?:tell|show|give|what|how)\b|$)",
        q,
        re.IGNORECASE
    )

    if pattern2:

        destination = pattern2.group(1).strip()

        arrival_time = pattern2.group(2).strip()

        source = pattern2.group(3).strip()

        return (
            destination,
            source,
            arrival_time
        )

    return (
        None,
        None,
        None
    )


# ============================================================
# TIME NORMALIZATION
# ============================================================

def normalize_time(
    arrival_time: str
):

    if not arrival_time:

        return None

    time_match = re.match(
        r"^\s*(\d{1,2})(?::(\d{2}))?\s*(am|pm)?\s*$",
        arrival_time,
        re.IGNORECASE
    )

    if not time_match:

        return None

    hour = int(
        time_match.group(1)
    )

    minute = int(
        time_match.group(2) or 0
    )

    ampm = time_match.group(3)

    # --------------------------------------------------------
    # Validate minutes
    # --------------------------------------------------------

    if minute < 0 or minute > 59:

        return None

    # --------------------------------------------------------
    # AM / PM
    # --------------------------------------------------------

    if ampm:

        ampm = ampm.lower()

        if hour < 1 or hour > 12:

            return None

        if ampm == "pm" and hour != 12:

            hour += 12

        elif ampm == "am" and hour == 12:

            hour = 0

    else:

        # 24-hour format

        if hour < 0 or hour > 23:

            return None

    return f"{hour:02d}:{minute:02d}"


# ============================================================
# ROUTER
# ============================================================

def router_node(
    state: SmartCityState
):

    question = state.get(
        "user_input",
        ""
    ).strip()

    history = state.get(
        "history",
        []
    )

    print(
        "\n===================================="
    )

    print(
        "ROUTER (NLP-Powered & Typo-Resilient)"
    )

    print(
        "===================================="
    )

    print(
        "Question:",
        question
    )

    # 1. NLP Query Parsing (handles spelling mistakes, typos, city localities, and arbitrary sentence syntax)
    nlp_result = parse_user_query(
        question,
        history
    )

    corrected_query = nlp_result.get(
        "corrected_query"
    ) or question

    domains = [
        str(d).lower()
        for d in nlp_result.get("domains", [])
    ]

    extracted_source = nlp_result.get("source")
    extracted_dest = nlp_result.get("destination")
    extracted_time = nlp_result.get("arrival_time")

    print("Corrected Query:", corrected_query)
    print("Detected Domains:", domains)
    print("Extracted Source:", extracted_source)
    print("Extracted Destination:", extracted_dest)
    print("Extracted Arrival Time:", extracted_time)

    # 2. Use Groq's detected domains directly.
    #    No hard-coded English phrases or keyword lists are used here.
    allowed_domains = {
        "planner",
        "traffic",
        "water",
        "pollution",
        "infrastructure",
        "general"
    }

    domains = [
        domain
        for domain in domains
        if domain in allowed_domains
    ]

    planning = "planner" in domains
    traffic = "traffic" in domains
    water = "water" in domains
    pollution = "pollution" in domains
    infrastructure = "infrastructure" in domains

    # --------------------------------------------------------
    # Force planning mode when Flutter sends structured fields
    # (source, destination, arrival_time) even if Groq did not
    # classify the query as "planner".
    # --------------------------------------------------------

    has_structured_fields = (
        (
            state.get("source")
            or extracted_source
        )
        and (
            state.get("destination")
            or extracted_dest
        )
        and (
            state.get("arrival_time")
            or extracted_time
        )
    )

    if has_structured_fields and not planning:

        print(
            "Structured fields detected — "
            "forcing planning mode."
        )

        planning = True

    selected_agents = []

    if planning:
        selected_agents.extend([
            "planner_parser",
            "traffic",
            "water",
            "planner"
        ])
    else:
        if traffic:
            selected_agents.append("traffic")
        if water:
            selected_agents.append("water")

    if pollution:
        selected_agents.append("pollution")

    if infrastructure:
        selected_agents.append("infrastructure")

    # Remove duplicates
    selected_agents = list(
        dict.fromkeys(
            selected_agents
        )
    )

    print(
        "Selected agents:",
        selected_agents
    )

    print(
        "====================================\n"
    )

    updates = {
        "selected_agents": selected_agents,
        "normalized_query": corrected_query
    }

    if extracted_source and not state.get("source"):
        updates["source"] = extracted_source

    if extracted_dest and not state.get("destination"):
        updates["destination"] = extracted_dest

    if extracted_time and not state.get("arrival_time"):
        updates["arrival_time"] = extracted_time

    return updates


# ============================================================
# PLANNER PARSER
# ============================================================

def planner_parser_node(
    state: SmartCityState
):

    selected = state.get(
        "selected_agents",
        []
    )

    if "planner_parser" not in selected:

        return {}

    question = state.get(
        "user_input",
        ""
    )

    print(
        "\n[PLANNER PARSER AGENT]"
    )

    # --------------------------------------------------------
    # Use structured API fields first
    # --------------------------------------------------------

    source = state.get(
        "source"
    )

    destination = state.get(
        "destination"
    )

    arrival_time = state.get(
        "arrival_time"
    )

    # --------------------------------------------------------
    # If fields are missing, extract from question
    # --------------------------------------------------------

    if (
        not source
        or not destination
        or not arrival_time
    ):

        (
            parsed_destination,
            parsed_source,
            parsed_time
        ) = extract_location_from_question(
            question
        )

        if not destination:

            destination = parsed_destination

        if not source:

            source = parsed_source

        if not arrival_time:

            arrival_time = parsed_time

    # --------------------------------------------------------
    # Validate
    # --------------------------------------------------------

    if (
        not destination
        or not source
        or not arrival_time
    ):

        # --------------------------------------------------------
        # If source and destination are known, pass them through
        # so traffic and weather agents can use them even
        # without arrival_time.
        # --------------------------------------------------------

        if source and destination:

            print(
                "Missing arrival_time — "
                "passing source and destination only."
            )

            return {

                "source": source,

                "destination": destination,

                "planner": {

                    "source": source,

                    "destination": destination,

                    "note": (
                        "Arrival time not provided. "
                        "Route and weather data will "
                        "still be available."
                    )

                }

            }

        error = {

            "error": (
                "Please provide destination, "
                "source, and arrival time."
            )

        }

        print(
            error
        )

        return {
            "planner": error
        }

    # --------------------------------------------------------
    # Normalize time
    # --------------------------------------------------------

    normalized_time = normalize_time(
        arrival_time
    )

    if normalized_time is None:

        error = {

            "error": (
                "Invalid arrival time. "
                "Please use a time such as "
                "9 AM or 09:00."
            )

        }

        print(
            error
        )

        return {
            "planner": error
        }

    print(
        "Source:",
        source
    )

    print(
        "Destination:",
        destination
    )

    print(
        "Arrival time:",
        normalized_time
    )

    return {

        "source": source,

        "destination": destination,

        "arrival_time": normalized_time,

        "planner": {

            "source": source,

            "destination": destination,

            "arrival_time": normalized_time

        }

    }


# ============================================================
# TRAFFIC AGENT
# ============================================================

def traffic_node(
    state: SmartCityState
):

    selected = state.get(
        "selected_agents",
        []
    )

    if "traffic" not in selected:
        return {}

    print("\n[TRAFFIC AGENT]")

    question = state.get(
        "normalized_query"
    ) or state.get(
        "user_input",
        ""
    )

    # --------------------------------------------------------
    # For planning requests, source/destination are already
    # available in state.
    #
    # For normal traffic questions, send the original question
    # directly to TrafficAgent.
    # --------------------------------------------------------

    source = state.get(
        "source"
    )

    destination = state.get(
        "destination"
    )

    try:

        # ----------------------------------------------------
        # Multiple destination planning
        # ----------------------------------------------------

        route_destinations = state.get(
            "route_destinations"
        )

        if source and route_destinations:

            print(
                "Source:",
                source
            )

            print(
                "Destinations:",
                route_destinations
            )

            result = (
                traffic_agent
                .get_multi_destination_traffic(
                    source,
                    route_destinations
                )
            )

        # ----------------------------------------------------
        # Single destination planning
        # ----------------------------------------------------

        elif source and destination:

            print(
                "Source:",
                source
            )

            print(
                "Destination:",
                destination
            )

            result = (
                traffic_agent
                .get_traffic(
                    f"from {source} to {destination}"
                )
            )

        # ----------------------------------------------------
        # Normal traffic question
        #
        # Two sub-cases:
        #   a) "from X to Y" → route traffic
        #   b) "traffic in X" → area traffic (single location)
        # ----------------------------------------------------

        else:

            print(
                "Sending original question to Traffic Agent:"
            )

            print(
                question
            )

            result = (
                traffic_agent
                .get_traffic(
                    question
                )
            )

        print(
            "\nTraffic Result:"
        )

        print(
            result
        )

        return {
            "traffic": result
        }

    except Exception as e:

        print(
            "\nTraffic Agent Error:",
            str(e)
        )

        return {

            "traffic": {

                "error": str(e)

            }

        }

        # ----------------------------------------------------
        # Multiple destinations
        # ----------------------------------------------------

        if route_destinations:

            result = (
                traffic_agent
                .get_multi_destination_traffic(
                    source,
                    route_destinations
                )
            )

        # ----------------------------------------------------
        # Single destination
        # ----------------------------------------------------

        else:

            result = (
                traffic_agent
                .get_traffic(
                    f"from {source} to {destination}"
                )
            )

        return {
            "traffic": result
        }

    except Exception as e:

        print(
            "Traffic Agent Error:",
            str(e)
        )

        return {

            "traffic": {

                "error": str(e)

            }

        }


# ============================================================
# WATER / WEATHER AGENT
# ============================================================

def water_node(
    state: SmartCityState
):

    selected = state.get(
        "selected_agents",
        []
    )

    if "water" not in selected:

        return {}

    print(
        "\n[WATER / WEATHER AGENT]"
    )

    # --------------------------------------------------------
    # For planning requests, destination is already available.
    # For normal weather questions, destination may not exist.
    # In that case, send the original question to WaterAgent.
    # WaterAgent will extract the location itself.
    # --------------------------------------------------------

    destination = state.get(
        "destination"
    )

    question = state.get(
        "normalized_query"
    ) or state.get(
        "user_input",
        ""
    )

    source = state.get(
        "source"
    )

    if destination:

        weather_input = destination

    elif source:

        # Source is set but no destination — use source
        weather_input = source

    else:

        # Try to extract destination from "from X to Y"
        travel_match = re.search(
            r"from\s+(.+?)\s+to\s+(.+?)"
            r"(?:\s+(?:tell|and|show|give|what|how|is|are"
            r"|the|traffic|weather|check|will|please|can"
            r"|could|by|at|before|after)\b|\?|$)",
            question,
            re.IGNORECASE
        )

        if travel_match:

            weather_input = travel_match.group(2).strip()

            print(
                "Extracted destination from question:",
                weather_input
            )

        else:

            weather_input = question

    print(
        "Sending to Water Agent:",
        weather_input
    )

    try:

        result = (
            water_agent
            .get_weather(
                weather_input
            )
        )

        return {
            "water": result
        }

    except Exception as e:

        print(
            "Water Agent Error:",
            str(e)
        )

        return {

            "water": {

                "area": None,

                "temperature_c": None,

                "humidity": None,

                "weather": None,

                "rainfall_mm_last_1h": 0,

                "flood_risk": "unknown",

                "error": str(e)

            }

        }

# ============================================================
# PLANNER AGENT
# ============================================================

def planner_node(
    state: SmartCityState
):

    selected = state.get(
        "selected_agents",
        []
    )

    if "planner" not in selected:

        return {}

    planner_data = state.get(
        "planner",
        {}
    )

    if "error" in planner_data:

        return {}

    source = state.get(
        "source"
    )

    destination = state.get(
        "destination"
    )

    arrival_time = state.get(
        "arrival_time"
    )

    if not source or not destination:

        return {}

    print(
        "\n[PLANNER AGENT]"
    )

    # --------------------------------------------------------
    # Traffic delay
    # --------------------------------------------------------

    traffic_data = state.get(
        "traffic",
        {}
    )

    traffic_delay = 0

    if isinstance(
        traffic_data,
        dict
    ):

        traffic_delay = traffic_data.get(
            "traffic_delay_minutes",
            traffic_data.get(
                "total_traffic_delay_minutes",
                0
            )
        )

        if traffic_delay is None:

            traffic_delay = 0

    # --------------------------------------------------------
    # Weather
    # --------------------------------------------------------

    water_data = state.get(
        "water",
        {}
    )

    weather = "no_rain"

    if isinstance(
        water_data,
        dict
    ):

        rainfall = water_data.get(
            "rainfall_mm_last_1h",
            0
        )

        if rainfall and rainfall > 0:

            weather = "rain"

    # --------------------------------------------------------
    # Destinations
    # --------------------------------------------------------

    route_destinations = state.get(
        "route_destinations"
    )

    if route_destinations:

        destinations = [

            {
                "place": place
            }

            for place in route_destinations

        ]

    else:

        destinations = [

            {
                "place": destination
            }

        ]

    # --------------------------------------------------------
    # Use traffic travel time
    # --------------------------------------------------------

    if isinstance(
        traffic_data,
        dict
    ):

        legs = traffic_data.get(
            "legs",
            []
        )

        if legs:

            destinations = []

            for leg in legs:

                destinations.append({

                    "place": leg.get(
                        "destination",
                        ""
                    ),

                    "travel_time": round(
                        leg.get(
                            "travel_time_minutes",
                            0
                        )
                    )

                })

        else:

            travel_time = (
                traffic_data.get(
                    "travel_time_minutes"
                )
            )

            if travel_time is not None:

                destinations = [

                    {

                        "place": destination,

                        "travel_time": round(
                            travel_time
                        )

                    }

                ]

    # --------------------------------------------------------
    # Ensure travel_time exists
    # --------------------------------------------------------

    for place in destinations:

        if "travel_time" not in place:

            place["travel_time"] = 0

    # --------------------------------------------------------
    # Calculate departure
    # --------------------------------------------------------

    if not arrival_time:

        # No arrival_time — return route and weather
        # info without departure calculation.

        result = {

            "destinations": destinations,

            "weather": weather,

            "traffic_delay_minutes": round(
                traffic_delay
            ),

            "note": (
                "No arrival time specified. "
                "Showing route and weather info."
            )

        }

        # Add total travel time from traffic data
        total_travel = 0

        for place in destinations:

            total_travel += place.get(
                "travel_time",
                0
            )

        result["total_travel_minutes"] = (
            total_travel
        )

        return {
            "planner": result
        }

    try:

        result = (
            planner_agent
            .calculate_departure(
                destinations=destinations,
                arrival_time=arrival_time,
                traffic_delay=traffic_delay,
                weather=weather
            )
        )

        return {
            "planner": result
        }

    except Exception as e:

        print(
            "Planner Agent Error:",
            str(e)
        )

        return {

            "planner": {

                "error": str(e)

            }

        }


# ============================================================
# POLLUTION RAG
# ============================================================

def pollution_node(
    state: SmartCityState
):

    selected = state.get(
        "selected_agents",
        []
    )

    if "pollution" not in selected:

        return {}

    print(
        "\n[POLLUTION AGENT]"
    )

    # IMPORTANT:
    # Send the ORIGINAL user question directly
    # to the Pollution RAG agent.

    question = state.get(
        "normalized_query"
    ) or state.get(
        "user_input",
        ""
    )

    print(
        "Sending question to Pollution RAG:",
        question
    )

    try:

        result = pollution_agent(
            question
        )

        return {
            "pollution": result
        }

    except Exception as e:

        print(
            "Pollution Agent Error:",
            str(e)
        )

        return {

            "pollution": {

                "agent": "pollution",

                "found": False,

                "context": [],

                "error": str(e)

            }

        }


# ============================================================
# INFRASTRUCTURE RAG
# ============================================================

def infrastructure_node(
    state: SmartCityState
):

    selected = state.get(
        "selected_agents",
        []
    )

    if "infrastructure" not in selected:

        return {}

    print(
        "\n[INFRASTRUCTURE AGENT]"
    )

    # IMPORTANT:
    # Send the ORIGINAL user question directly
    # to the Infrastructure RAG agent.

    question = state.get(
        "normalized_query"
    ) or state.get(
        "user_input",
        ""
    )

    print(
        "Sending question to Infrastructure RAG:",
        question
    )

    try:

        result = infrastructure_agent(
            question
        )

        return {
            "infrastructure": result
        }

    except Exception as e:

        print(
            "Infrastructure Agent Error:",
            str(e)
        )

        return {

            "infrastructure": {

                "agent": "infrastructure",

                "found": False,

                "context": [],

                "error": str(e)

            }

        }


# ============================================================
# COMBINE AGENT RESULTS
# ============================================================

def combine_node(
    state: SmartCityState
):

    print(
        "\n===================================="
    )

    print(
        "COMBINED AGENT CONTEXT"
    )

    print(
        "===================================="
    )

    planner_data = state.get(
        "planner",
        {}
    )

    traffic_data = state.get(
        "traffic",
        {}
    )

    water_data = state.get(
        "water",
        {}
    )

    pollution_data = state.get(
        "pollution",
        {}
    )

    infrastructure_data = state.get(
        "infrastructure",
        {}
    )

    print(
        "\nPLANNER INFORMATION:"
    )

    print(
        planner_data
    )

    print(
        "\nTRAFFIC INFORMATION:"
    )

    print(
        traffic_data
    )

    print(
        "\nWEATHER / WATER INFORMATION:"
    )

    print(
        water_data
    )

    print(
        "\nPOLLUTION INFORMATION:"
    )

    print(
        pollution_data
    )

    print(
        "\nINFRASTRUCTURE INFORMATION:"
    )

    print(
        infrastructure_data
    )

    context = f"""

PLANNER INFORMATION:
{planner_data}

TRAFFIC INFORMATION:
{traffic_data}

WEATHER / WATER INFORMATION:
{water_data}

POLLUTION INFORMATION:
{pollution_data}

INFRASTRUCTURE INFORMATION:
{infrastructure_data}
"""

    return {
        "final_context": context
    }


# ============================================================
# GROQ RESPONSE
# ============================================================

def response_node(
    state: SmartCityState
):

    print(
        "\n[GROQ RESPONSE AGENT]"
    )

    context = state.get(
        "final_context",
        ""
    )

    question = state.get(
        "normalized_query"
    ) or state.get(
        "user_input",
        ""
    )

    history = state.get(
        "history",
        []
    )

    try:

        response = generate_response(
            context,
            question,
            history
        )

        return {
            "final_response": response
        }

    except Exception as e:

        print(
            "Groq Error:",
            str(e)
        )

        return {

            "final_response": (
                "Sorry, I was unable to "
                "generate a response."
            )

        }


# ============================================================
# LANGGRAPH
# ============================================================

workflow = StateGraph(
    SmartCityState
)


# ============================================================
# ADD NODES
# ============================================================

workflow.add_node(
    "router",
    router_node
)

workflow.add_node(
    "planner_parser",
    planner_parser_node
)

workflow.add_node(
    "traffic",
    traffic_node
)

workflow.add_node(
    "water",
    water_node
)

workflow.add_node(
    "planner",
    planner_node
)

workflow.add_node(
    "pollution",
    pollution_node
)

workflow.add_node(
    "infrastructure",
    infrastructure_node
)

workflow.add_node(
    "combine",
    combine_node
)

workflow.add_node(
    "response",
    response_node
)


# ============================================================
# SEQUENTIAL GRAPH
#
# Router
#   ↓
# Planner Parser
#   ↓
# Traffic
#   ↓
# Weather
#   ↓
# Planner
#   ↓
# Pollution
#   ↓
# Infrastructure
#   ↓
# Combine
#   ↓
# Groq
#   ↓
# END
# ============================================================

workflow.set_entry_point(
    "router"
)

workflow.add_edge(
    "router",
    "planner_parser"
)

workflow.add_edge(
    "planner_parser",
    "traffic"
)

workflow.add_edge(
    "traffic",
    "water"
)

workflow.add_edge(
    "water",
    "planner"
)

workflow.add_edge(
    "planner",
    "pollution"
)

workflow.add_edge(
    "pollution",
    "infrastructure"
)

workflow.add_edge(
    "infrastructure",
    "combine"
)

workflow.add_edge(
    "combine",
    "response"
)

workflow.add_edge(
    "response",
    END
)


# ============================================================
# COMPILE
# ============================================================

graph = workflow.compile()


# ============================================================
# TERMINAL TEST
# ============================================================

if __name__ == "__main__":

    print(
        "\n===================================="
    )

    print(
        "SMART CITY AI"
    )

    print(
        "===================================="
    )

    question = input(
        "Enter your request: "
    ).strip()

    result = graph.invoke({

        "user_input": question

    })

    print(
        "\n===================================="
    )

    print(
        "FINAL AI RESPONSE"
    )

    print(
        "===================================="
    )

    print(
        result.get(
            "final_response",
            ""
        )
    )