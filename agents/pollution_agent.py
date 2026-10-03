import os
import re
import requests
import chromadb

from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer


# ============================================================
# ENVIRONMENT
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

ENV_FILE = os.path.join(
    BASE_DIR,
    ".env"
)

load_dotenv(ENV_FILE)

OPENWEATHER_API_KEY = os.getenv(
    "OPENWEATHER_API_KEY"
)


# ============================================================
# CHROMADB
# ============================================================

CHROMA_DIR = os.path.join(
    BASE_DIR,
    "chroma_db"
)

COLLECTION_NAME = "smart_city_knowledge"

RAG_DISTANCE_THRESHOLD = 1.20

RAG_RESULTS = 10

REQUEST_TIMEOUT = 10


# ============================================================
# LOAD EMBEDDING MODEL
# ============================================================

print(
    "Loading Pollution Agent embedding model..."
)

model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

print(
    "Pollution Agent embedding model loaded."
)


# ============================================================
# CONNECT TO CHROMADB
# ============================================================

try:

    print(
        "\nChromaDB path:",
        CHROMA_DIR
    )

    chroma_client = chromadb.PersistentClient(
        path=CHROMA_DIR
    )

    collection = chroma_client.get_collection(
        name=COLLECTION_NAME
    )

    print(
        "Pollution Agent connected to ChromaDB."
    )

    print(
        "Knowledge chunks available:",
        collection.count()
    )

except Exception as e:

    print(
        "Pollution Agent ChromaDB Error:",
        str(e)
    )

    chroma_client = None
    collection = None


# ============================================================
# AQI CATEGORY
# ============================================================

def get_aqi_category(aqi):

    categories = {
        1: "Good",
        2: "Fair",
        3: "Moderate",
        4: "Poor",
        5: "Very Poor",
    }

    try:

        return categories.get(
            int(aqi),
            "Unknown"
        )

    except Exception:

        return "Unknown"


# ============================================================
# LOCATION EXTRACTION
# ============================================================

def extract_location(question):

    if not question:

        return "Hyderabad"

    text = question.strip()

    # --------------------------------------------------------
    # Remove common time expressions
    # --------------------------------------------------------

    text = re.sub(
        r"\b(?:today|tonight|now|currently|right now)\b",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    ).strip()

    # --------------------------------------------------------
    # around LOCATION
    # --------------------------------------------------------

    match = re.search(
        r"\baround\s+(.+?)(?=\s+(?:is|are|safe|good|bad|today|now|currently|right|and|but|to|for)\b|[?.!,]|$)",
        text,
        re.IGNORECASE
    )

    if match:

        location = match.group(1).strip()

        if location:
            return location

    # --------------------------------------------------------
    # in LOCATION
    # --------------------------------------------------------

    match = re.search(
        r"\bin\s+(.+?)(?=\s+(?:is|are|safe|good|bad|today|now|currently|right|and|but|to|for)\b|[?.!,]|$)",
        text,
        re.IGNORECASE
    )

    if match:

        location = match.group(1).strip()

        if location:
            return location

    # --------------------------------------------------------
    # near LOCATION
    # --------------------------------------------------------

    match = re.search(
        r"\bnear\s+(.+?)(?=\s+(?:is|are|safe|good|bad|today|now|currently|right|and|but|to|for)\b|[?.!,]|$)",
        text,
        re.IGNORECASE
    )

    if match:

        location = match.group(1).strip()

        if location:
            return location

    # --------------------------------------------------------
    # at LOCATION
    # --------------------------------------------------------

    match = re.search(
        r"\bat\s+(.+?)(?=\s+(?:is|are|safe|good|bad|today|now|currently|right|and|but|to|for)\b|[?.!,]|$)",
        text,
        re.IGNORECASE
    )

    if match:

        location = match.group(1).strip()

        if location:
            return location

    # --------------------------------------------------------
    # for LOCATION
    # --------------------------------------------------------

    match = re.search(
        r"\bfor\s+(.+?)(?=\s+(?:is|are|safe|good|bad|today|now|currently|right|and|but|to|for)\b|[?.!,]|$)",
        text,
        re.IGNORECASE
    )

    if match:

        location = match.group(1).strip()

        if location:
            return location

    # --------------------------------------------------------
    # Known Hyderabad locations
    # --------------------------------------------------------

    known_locations = [
        "Hitech City",
        "Hitec City",
        "Gachibowli",
        "Kukatpally",
        "Miyapur",
        "LB Nagar",
        "Dilsukhnagar",
        "Banjara Hills",
        "Jubilee Hills",
        "Secunderabad",
        "Begumpet",
        "Mehdipatnam",
        "Charminar",
        "Ameerpet",
        "Madhapur",
        "Kondapur",
        "Uppal",
        "Manikonda",
    ]

    for known_location in known_locations:

        if known_location.lower() in text.lower():

            return known_location

    return "Hyderabad"


# ============================================================
# OPENWEATHER GEOCODING
# ============================================================

def geocode_location(location):

    if not OPENWEATHER_API_KEY:

        return {
            "success": False,
            "error": (
                "OPENWEATHER_API_KEY is not configured."
            )
        }

    # --------------------------------------------------------
    # Try exact location first
    # --------------------------------------------------------

    search_queries = [
        location,
        f"{location}, Hyderabad, India",
        f"{location}, Telangana, India",
        "Hyderabad, Telangana, India",
    ]

    # Remove duplicate queries
    search_queries = list(
        dict.fromkeys(search_queries)
    )

    last_error = None

    for query in search_queries:

        print(
            "\nTrying geocoding:",
            query
        )

        try:

            response = requests.get(
                "https://api.openweathermap.org/geo/1.0/direct",
                params={
                    "q": query,
                    "limit": 1,
                    "appid": OPENWEATHER_API_KEY,
                },
                timeout=REQUEST_TIMEOUT,
            )

            if response.status_code != 200:

                last_error = (
                    f"OpenWeather geocoding returned "
                    f"status {response.status_code}"
                )

                continue

            data = response.json()

            if not data:

                print(
                    "No location found for:",
                    query
                )

                continue

            place = data[0]

            result = {

                "success": True,

                "name": place.get(
                    "name",
                    location
                ),

                "state": place.get(
                    "state"
                ),

                "country": place.get(
                    "country"
                ),

                "latitude": place.get(
                    "lat"
                ),

                "longitude": place.get(
                    "lon"
                ),

                "requested_location": location,

                "geocoding_query": query,
            }

            print(
                "Location resolved:"
            )

            print(
                result
            )

            return result

        except Exception as e:

            last_error = str(e)

            print(
                "Geocoding attempt failed:",
                str(e)
            )

    return {
        "success": False,
        "error": (
            f"Could not resolve '{location}' "
            "using OpenWeather geocoding."
        ),
        "details": last_error,
    }


# ============================================================
# LIVE OPENWEATHER AIR POLLUTION
# ============================================================

def get_live_pollution(location):

    print(
        "\n[OPENWEATHER LIVE AIR POLLUTION]"
    )

    print(
        "Requested location:",
        location
    )

    if not OPENWEATHER_API_KEY:

        print(
            "OpenWeather API key not configured."
        )

        return {
            "available": False,
            "error": (
                "OPENWEATHER_API_KEY is not configured."
            )
        }

    # --------------------------------------------------------
    # Resolve location
    # --------------------------------------------------------

    geo = geocode_location(
        location
    )

    if not geo.get("success"):

        print(
            "Geocoding error:",
            geo.get("error")
        )

        return {
            "available": False,
            "error": geo.get(
                "error",
                "Location could not be resolved."
            )
        }

    latitude = geo.get(
        "latitude"
    )

    longitude = geo.get(
        "longitude"
    )

    print(
        "\nResolved location:",
        geo.get("name")
    )

    print(
        "Latitude:",
        latitude
    )

    print(
        "Longitude:",
        longitude
    )

    # --------------------------------------------------------
    # Air pollution API
    # --------------------------------------------------------

    try:

        response = requests.get(
            "https://api.openweathermap.org/data/2.5/air_pollution",
            params={
                "lat": latitude,
                "lon": longitude,
                "appid": OPENWEATHER_API_KEY,
            },
            timeout=REQUEST_TIMEOUT,
        )

        if response.status_code != 200:

            return {
                "available": False,
                "error": (
                    "OpenWeather air pollution request "
                    f"failed with status "
                    f"{response.status_code}."
                )
            }

        data = response.json()

        pollution_list = data.get(
            "list",
            []
        )

        if not pollution_list:

            return {
                "available": False,
                "error": (
                    "OpenWeather returned no "
                    "air pollution data."
                )
            }

        current = pollution_list[0]

        main = current.get(
            "main",
            {}
        )

        components = current.get(
            "components",
            {}
        )

        aqi = main.get(
            "aqi"
        )

        result = {

            "available": True,

            "source": "OpenWeather",

            "location": geo.get(
                "name",
                location
            ),

            "state": geo.get(
                "state"
            ),

            "country": geo.get(
                "country"
            ),

            "latitude": latitude,

            "longitude": longitude,

            "aqi": aqi,

            "aqi_category": (
                get_aqi_category(aqi)
                if aqi is not None
                else "Unknown"
            ),

            "pm2_5": components.get(
                "pm2_5"
            ),

            "pm10": components.get(
                "pm10"
            ),

            "co": components.get(
                "co"
            ),

            "no": components.get(
                "no"
            ),

            "no2": components.get(
                "no2"
            ),

            "o3": components.get(
                "o3"
            ),

            "so2": components.get(
                "so2"
            ),

            "nh3": components.get(
                "nh3"
            ),

            "timestamp": current.get(
                "dt"
            ),
        }

        print(
            "\nLIVE POLLUTION RESULT:"
        )

        print(
            result
        )

        return result

    except Exception as e:

        print(
            "OpenWeather API error:",
            str(e)
        )

        return {
            "available": False,
            "error": str(e)
        }


# ============================================================
# RAG RETRIEVAL
# ============================================================

def retrieve_pollution_knowledge(question):

    print(
        "\n[POLLUTION RAG]"
    )

    print(
        "Question:",
        question
    )

    if collection is None:

        return {
            "found": False,
            "context": [],
            "error": (
                "ChromaDB collection is unavailable."
            )
        }

    try:

        query_embedding = model.encode(
            question
        ).tolist()

        results = collection.query(
            query_embeddings=[
                query_embedding
            ],
            n_results=RAG_RESULTS,
        )

        documents = (
            results.get(
                "documents",
                [[]]
            )[0]
        )

        metadatas = (
            results.get(
                "metadatas",
                [[]]
            )[0]
        )

        distances = (
            results.get(
                "distances",
                [[]]
            )[0]
        )

        print(
            "\nRetrieved results:",
            len(documents)
        )

        context = []

        for index, document in enumerate(
            documents
        ):

            metadata = {}

            if index < len(metadatas):

                metadata = (
                    metadatas[index]
                    or {}
                )

            distance = None

            if index < len(distances):

                distance = distances[index]

            source = metadata.get(
                "source",
                "unknown"
            )

            category = str(
                metadata.get(
                    "category",
                    ""
                )
            ).strip().lower()

            print(
                f"\nCandidate distance: "
                f"{distance}"
            )

            print(
                "Source:",
                source
            )

            print(
                "Category:",
                category
            )

            # ------------------------------------------------
            # Pollution category filter
            # ------------------------------------------------

            if (
                category
                and category != "pollution"
            ):

                continue

            # ------------------------------------------------
            # Distance filter
            # ------------------------------------------------

            if (
                distance is not None
                and distance > RAG_DISTANCE_THRESHOLD
            ):

                continue

            context.append({

                "source": source,

                "distance": distance,

                "content": document,

                "category": (
                    category
                    or "pollution"
                ),
            })

        if not context:

            print(
                "\nNo relevant pollution "
                "information found."
            )

            return {
                "found": False,
                "context": [],
            }

        context = context[:5]

        print(
            "\nRelevant pollution results:",
            len(context)
        )

        for item in context:

            print(
                "\nSource:",
                item["source"]
            )

            print(
                "Distance:",
                item["distance"]
            )

        return {
            "found": True,
            "context": context,
        }

    except Exception as e:

        print(
            "\nPollution RAG Error:",
            str(e)
        )

        return {
            "found": False,
            "context": [],
            "error": str(e),
        }


# ============================================================
# HYBRID POLLUTION AGENT
# ============================================================

def pollution_agent(question):

    print(
        "\n===================================="
    )

    print(
        "POLLUTION AGENT"
    )

    print(
        "===================================="
    )

    print(
        "Question:",
        question
    )

    # --------------------------------------------------------
    # 1. Extract location
    # --------------------------------------------------------

    location = extract_location(
        question
    )

    print(
        "\nDetected location:",
        location
    )

    # --------------------------------------------------------
    # 2. Live pollution data
    # --------------------------------------------------------

    live_data = get_live_pollution(
        location
    )

    # --------------------------------------------------------
    # 3. RAG knowledge
    # --------------------------------------------------------

    rag_data = retrieve_pollution_knowledge(
        question
    )

    # --------------------------------------------------------
    # 4. Combine
    # --------------------------------------------------------

    result = {

        "agent": "pollution",

        "location": location,

        "live_data": live_data,

        "rag": rag_data,

        "found": (
            rag_data.get(
                "found",
                False
            )
            or live_data.get(
                "available",
                False
            )
        ),

        "context": rag_data.get(
            "context",
            []
        ),
    }

    print(
        "\n===================================="
    )

    print(
        "COMBINED POLLUTION RESULT"
    )

    print(
        "===================================="
    )

    print(
        result
    )

    return result


# ============================================================
# DIRECT TEST
# ============================================================

if __name__ == "__main__":

    print(
        "\n===================================="
    )

    print(
        "POLLUTION AGENT TEST"
    )

    print(
        "===================================="
    )

    question = input(
        "Ask a pollution question: "
    ).strip()

    result = pollution_agent(
        question
    )

    print(
        "\n===================================="
    )

    print(
        "FINAL RESULT"
    )

    print(
        "===================================="
    )

    print(result)