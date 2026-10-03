from dotenv import load_dotenv

load_dotenv()

from typing import List, Optional
from fastapi import FastAPI
from pydantic import BaseModel

from graph.workflow import graph


app = FastAPI(title="Smart City AI API")


class UserRequest(BaseModel):
    question: str
    startLocation: Optional[str] = None
    destinations: Optional[List[str]] = None
    arrival_time: Optional[str] = None
    history: Optional[List[dict]] = None


@app.get("/")
def home():
    return {
        "message": "Smart City AI API is running"
    }


@app.post("/ask")
def ask(request: UserRequest):

    graph_input = {
        "user_input": request.question
    }

    # Starting location
    if request.startLocation:
        graph_input["source"] = request.startLocation

    # Destination(s)
    if request.destinations:
        graph_input["route_destinations"] = request.destinations
        graph_input["destination"] = request.destinations[-1]

    # Arrival time
    if request.arrival_time:
        graph_input["arrival_time"] = request.arrival_time

    # Conversation history
    if request.history:
        graph_input["history"] = request.history

    # Run LangGraph
    result = graph.invoke(graph_input)

    return {
        "question": request.question,
        "corrected_question": result.get("normalized_query", request.question),

        "response": result.get(
            "final_response",
            ""
        ),

        "planner": result.get(
            "planner",
            {}
        ),

        "traffic": result.get(
            "traffic",
            {}
        ),

        "water": result.get(
            "water",
            {}
        ),

        "pollution": result.get(
            "pollution",
            {}
        ),

        "infrastructure": result.get(
            "infrastructure",
            {}
        )
    }