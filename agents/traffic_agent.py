import re
import os
import requests
from dotenv import load_dotenv

load_dotenv()


class TrafficAgent:

    def __init__(self):
        self.tomtom_api_key = os.getenv("TOMTOM_API_KEY")

        # ========================================================
        # HYDERABAD LOCATION ALIASES
        # ========================================================

        self.location_aliases = {

            # ----------------------------------------------------
            # KMIT / EAST HYDERABAD
            # ----------------------------------------------------

            "kmit": "KMIT Hyderabad",

            "keshav memorial institute of technology":
                "KMIT Hyderabad",

            "keshav memorial institute of technology hyderabad":
                "KMIT Hyderabad",

            "keshav memorial institute of technology, hyderabad":
                "KMIT Hyderabad",

            "lb nagar": "LB Nagar Hyderabad",
            "l.b. nagar": "LB Nagar Hyderabad",
            "l b nagar": "LB Nagar Hyderabad",
            "lbnagar": "LB Nagar Hyderabad",

            "lb nagar junction":
                "LB Nagar Junction Hyderabad",

            "kothapet": "Kothapet Hyderabad",

            "dilsukhnagar":
                "Dilsukhnagar Hyderabad",

            "dilshuknagar":
                "Dilsukhnagar Hyderabad",

            "malakpet":
                "Malakpet Hyderabad",

            "saroornagar":
                "Saroornagar Hyderabad",

            "saroor nagar":
                "Saroornagar Hyderabad",

            "nagole":
                "Nagole Hyderabad",

            "uppal":
                "Uppal Hyderabad",

            "uppal junction":
                "Uppal Junction Hyderabad",

            "habsiguda":
                "Habsiguda Hyderabad",

            "nacharam":
                "Nacharam Hyderabad",

            "tarnaka":
                "Tarnaka Hyderabad",

            "malkajgiri":
                "Malkajgiri Hyderabad",

            "ecil":
                "ECIL Hyderabad",

            "as rao nagar":
                "AS Rao Nagar Hyderabad",

            # ----------------------------------------------------
            # WEST HYDERABAD
            # ----------------------------------------------------

            "hitech city":
                "HITEC City Hyderabad",

            "hi tech city":
                "HITEC City Hyderabad",

            "hitec city":
                "HITEC City Hyderabad",

            "hitec":
                "HITEC City Hyderabad",

            "madhapur":
                "Madhapur Hyderabad",

            "kondapur":
                "Kondapur Hyderabad",

            "gachibowli":
                "Gachibowli Hyderabad",

            "financial district":
                "Financial District Hyderabad",

            "nanakramguda":
                "Nanakramguda Hyderabad",

            "kokapet":
                "Kokapet Hyderabad",

            "narsingi":
                "Narsingi Hyderabad",

            "manikonda":
                "Manikonda Hyderabad",

            "gowlidoddi":
                "Gowlidoddi Hyderabad",

            "raidurg":
                "Raidurg Hyderabad",

            "raidurgam":
                "Raidurg Hyderabad",

            "durgam cheruvu":
                "Durgam Cheruvu Hyderabad",

            "mindspace":
                "Mindspace Hyderabad",

            "cyber towers":
                "Cyber Towers Hyderabad",

            "biodiversity junction":
                "Biodiversity Junction Hyderabad",

            # ----------------------------------------------------
            # NORTH-WEST HYDERABAD
            # ----------------------------------------------------

            "kukatpally":
                "Kukatpally Hyderabad",

            "kphb":
                "KPHB Hyderabad",

            "kphb colony":
                "KPHB Hyderabad",

            "miyapur":
                "Miyapur Hyderabad",

            "bachupally":
                "Bachupally Hyderabad",

            "nizampet":
                "Nizampet Hyderabad",

            "pragathi nagar":
                "Pragathi Nagar Hyderabad",

            "moosapet":
                "Moosapet Hyderabad",

            "balanagar":
                "Balanagar Hyderabad",

            "balanagar junction":
                "Balanagar Junction Hyderabad",

            "jeedimetla":
                "Jeedimetla Hyderabad",

            "chintal":
                "Chintal Hyderabad",

            "suraram":
                "Suraram Hyderabad",

            "alwal":
                "Alwal Hyderabad",

            "quthbullapur":
                "Quthbullapur Hyderabad",

            "qutbullapur":
                "Qutbullapur Hyderabad",

            "hafeezpet":
                "Hafeezpet Hyderabad",

            "chandanagar":
                "Chandanagar Hyderabad",

            "chanda nagar":
                "Chanda Nagar Hyderabad",

            "serilingampally":
                "Serilingampally Hyderabad",

            "allwyn colony":
                "Allwyn Colony Hyderabad",

            "bhel":
                "BHEL Hyderabad",

            "patancheru":
                "Patancheru Hyderabad",

            "jntu junction":
                "JNTU Junction Hyderabad",

            "suchitra junction":
                "Suchitra Junction Hyderabad",

            # ----------------------------------------------------
            # CENTRAL HYDERABAD
            # ----------------------------------------------------

            "ameerpet":
                "Ameerpet Hyderabad",

            "begumpet":
                "Begumpet Hyderabad",

            "panjagutta":
                "Panjagutta Hyderabad",

            "somajiguda":
                "Somajiguda Hyderabad",

            "khairatabad":
                "Khairatabad Hyderabad",

            "khairtabad":
                "Khairatabad Hyderabad",

            "abids":
                "Abids Hyderabad",

            "koti":
                "Koti Hyderabad",

            "nampally":
                "Nampally Hyderabad",

            "nampally junction":
                "Nampally Hyderabad",

            "basheerbagh":
                "Basheerbagh Hyderabad",

            "lakdikapul":
                "Lakdikapul Hyderabad",

            "masab tank":
                "Masab Tank Hyderabad",

            "mehdipatnam":
                "Mehdipatnam Hyderabad",

            "tolichowki":
                "Tolichowki Hyderabad",

            "shaikpet":
                "Shaikpet Hyderabad",

            # ----------------------------------------------------
            # JUBILEE HILLS / BANJARA HILLS
            # ----------------------------------------------------

            "jubilee hills":
                "Jubilee Hills Hyderabad",

            "banjara hills":
                "Banjara Hills Hyderabad",

            "film nagar":
                "Film Nagar Hyderabad",

            "yousufguda":
                "Yousufguda Hyderabad",

            "srinagar colony":
                "Srinagar Colony Hyderabad",

            # ----------------------------------------------------
            # SECUNDERABAD
            # ----------------------------------------------------

            "secunderabad":
                "Secunderabad Hyderabad",

            "paradise":
                "Paradise Hyderabad",

            "paradise circle":
                "Paradise Circle Hyderabad",

            "musheerabad":
                "Musheerabad Hyderabad",

            "bowenpally":
                "Bowenpally Hyderabad",

            "old bowenpally":
                "Old Bowenpally Hyderabad",

            "tadbund":
                "Tadbund Hyderabad",

            "mettuguda":
                "Mettuguda Hyderabad",

            "sangeet":
                "Sangeet Hyderabad",

            # ----------------------------------------------------
            # OLD CITY
            # ----------------------------------------------------

            "old city":
                "Charminar Hyderabad",

            "old city hyderabad":
                "Charminar Hyderabad",

            "charminar":
                "Charminar Hyderabad",

            "chandrayangutta":
                "Chandrayangutta Hyderabad",

            "falaknuma":
                "Falaknuma Hyderabad",

            "saidabad":
                "Saidabad Hyderabad",

            "santoshnagar":
                "Santoshnagar Hyderabad",

            # ----------------------------------------------------
            # AIRPORT / SOUTH HYDERABAD
            # ----------------------------------------------------

            "shamshabad":
                "Shamshabad Hyderabad",

            "rajiv gandhi airport":
                "Rajiv Gandhi International Airport Hyderabad",

            "rajiv gandhi international airport":
                "Rajiv Gandhi International Airport Hyderabad",

            "airport":
                "Rajiv Gandhi International Airport Hyderabad",

            "tukkuguda":
                "Tukkuguda Hyderabad",

            "adibatla":
                "Adibatla Hyderabad",

            # ----------------------------------------------------
            # OUTER RING ROAD
            # ----------------------------------------------------

            "orr":
                "Hyderabad Outer Ring Road",

            "outer ring road":
                "Hyderabad Outer Ring Road"
        }

    # ============================================================
    # SEARCH LOCATION USING TOMTOM
    # ============================================================

    def search_location(self, location):

        if not self.tomtom_api_key:
            return None

        original_location = location.strip()

        clean_location = original_location.lower()

        # Use alias if available
        if clean_location in self.location_aliases:
            location = self.location_aliases[
                clean_location
            ]

        # Different search variations
        candidates = [
            location,
            f"{location}, Hyderabad, India",
            f"{location}, Telangana, India"
        ]

        # Remove duplicate candidates
        candidates = list(
            dict.fromkeys(candidates)
        )

        # Hyderabad bounding box for validation
        HYD_LAT_MIN = 17.15
        HYD_LAT_MAX = 17.65
        HYD_LON_MIN = 78.20
        HYD_LON_MAX = 78.75

        for candidate in candidates:

            try:

                url = (
                    "https://api.tomtom.com/search/2/search/"
                    f"{candidate}.json"
                )

                response = requests.get(
                    url,
                    params={
                        "key": self.tomtom_api_key,
                        "countrySet": "IN",
                        "limit": 5
                    },
                    timeout=20
                )

                response.raise_for_status()

                data = response.json()

                if not data.get("results"):
                    continue

                # Pick the first result inside
                # Hyderabad bounding box
                for result in data["results"]:

                    position = result.get(
                        "position"
                    )

                    if not position:
                        continue

                    lat = position["lat"]
                    lon = position["lon"]

                    if (
                        HYD_LAT_MIN <= lat <= HYD_LAT_MAX
                        and
                        HYD_LON_MIN <= lon <= HYD_LON_MAX
                    ):
                        return {
                            "latitude": lat,
                            "longitude": lon,
                            "display_name":
                                result.get(
                                    "address",
                                    {}
                                ).get(
                                    "freeformAddress",
                                    candidate
                                )
                        }

                # If no result was inside Hyderabad,
                # skip to next candidate
                print(
                    f"[TomTom] '{candidate}' "
                    f"not in Hyderabad bounds"
                )
                continue

            except requests.RequestException as e:

                print(
                    f"[TomTom Search Error] "
                    f"{candidate}: {e}"
                )

            except Exception as e:

                print(
                    f"[Location Error] "
                    f"{candidate}: {e}"
                )

        return None

    # ============================================================
    # CALCULATE ROUTE
    # ============================================================

    def calculate_route(
        self,
        source,
        destination
    ):

        source_location = self.search_location(
            source
        )

        destination_location = self.search_location(
            destination
        )

        if source_location is None:

            return {
                "error":
                    f"Could not find source: {source}"
            }

        if destination_location is None:

            return {
                "error":
                    f"Could not find destination: "
                    f"{destination}"
            }

        origin = (
            f"{source_location['latitude']},"
            f"{source_location['longitude']}"
        )

        destination_point = (
            f"{destination_location['latitude']},"
            f"{destination_location['longitude']}"
        )

        url = (
            "https://api.tomtom.com/routing/1/"
            "calculateRoute/"
            f"{origin}:{destination_point}/json"
        )

        try:

            response = requests.get(
                url,
                params={
                    "key": self.tomtom_api_key,
                    "traffic": "true",
                    "computeTravelTimeFor": "all"
                },
                timeout=20
            )

            response.raise_for_status()

            data = response.json()

        except requests.RequestException as e:

            return {
                "error":
                    f"Unable to retrieve route traffic: {e}"
            }

        if not data.get("routes"):

            return {
                "error":
                    "No route found between the locations."
            }

        summary = data["routes"][0]["summary"]

        traffic_delay = round(
            summary.get(
                "trafficDelayInSeconds",
                0
            ) / 60,
            2
        )

        if traffic_delay >= 10:

            traffic_level = "heavy"

        elif traffic_delay >= 5:

            traffic_level = "moderate"

        else:

            traffic_level = "light"

        return {

            "source":
                source,

            "destination":
                destination,

            "distance_km":
                round(
                    summary["lengthInMeters"] / 1000,
                    2
                ),

            "travel_time_minutes":
                round(
                    summary["travelTimeInSeconds"] / 60,
                    2
                ),

            "traffic_delay_minutes":
                traffic_delay,

            "traffic_level":
                traffic_level,

            "congestion":
                traffic_level == "heavy"
        }

    # ============================================================
    # STANDALONE LOCATION TRAFFIC
    #
    # Example:
    # "How is traffic in Kukatpally?"
    # ============================================================

    def get_location_traffic(
        self,
        location
    ):

        location_data = self.search_location(
            location
        )

        if location_data is None:

            return {
                "location":
                    location,

                "error":
                    f"Could not find location: {location}"
            }

        latitude = location_data["latitude"]
        longitude = location_data["longitude"]

        url = (
            "https://api.tomtom.com/traffic/services/4/"
            "flowSegmentData/absolute/10/json"
        )

        try:

            response = requests.get(
                url,
                params={
                    "key":
                        self.tomtom_api_key,

                    "point":
                        f"{latitude},{longitude}",

                    "unit":
                        "KMPH"
                },
                timeout=20
            )

            response.raise_for_status()

            data = response.json()

        except requests.RequestException as e:

            return {
                "location":
                    location,

                "error":
                    f"Traffic data unavailable: {e}"
            }

        flow = data.get(
            "flowSegmentData",
            {}
        )

        current_speed = flow.get(
            "currentSpeed"
        )

        free_flow_speed = flow.get(
            "freeFlowSpeed"
        )

        current_travel_time = flow.get(
            "currentTravelTime"
        )

        free_flow_travel_time = flow.get(
            "freeFlowTravelTime"
        )

        if current_speed is None:

            return {
                "location":
                    location,

                "error":
                    "Traffic data unavailable for this location."
            }

        # ========================================================
        # CALCULATE TRAFFIC LEVEL
        # ========================================================

        if (
            free_flow_speed
            and free_flow_speed > 0
        ):

            speed_ratio = (
                current_speed /
                free_flow_speed
            )

            if speed_ratio < 0.40:

                traffic_level = "heavy"

            elif speed_ratio < 0.70:

                traffic_level = "moderate"

            else:

                traffic_level = "light"

        else:

            traffic_level = "unknown"

        # ========================================================
        # TRAVEL TIME DELAY
        # ========================================================

        traffic_delay_minutes = None

        if (
            current_travel_time is not None
            and free_flow_travel_time is not None
        ):

            traffic_delay_minutes = round(
                max(
                    0,
                    current_travel_time
                    - free_flow_travel_time
                ) / 60,
                2
            )

        return {

            "location":
                location,

            "current_speed_kmph":
                round(
                    current_speed,
                    1
                ),

            "free_flow_speed_kmph":
                round(
                    free_flow_speed,
                    1
                )
                if free_flow_speed
                else None,

            "current_travel_time_minutes":
                round(
                    current_travel_time / 60,
                    2
                )
                if current_travel_time
                else None,

            "free_flow_travel_time_minutes":
                round(
                    free_flow_travel_time / 60,
                    2
                )
                if free_flow_travel_time
                else None,

            "traffic_delay_minutes":
                traffic_delay_minutes,

            "traffic_level":
                traffic_level,

            "congestion":
                traffic_level == "heavy"
        }

    # ============================================================
    # EXTRACT ROUTE
    # ============================================================

    def extract_route(
        self,
        question
    ):

        patterns = [

            # from A to B
            r"from\s+(.+?)\s+to\s+(.+?)(?:\?|$)",

            # between A and B
            r"between\s+(.+?)\s+and\s+(.+?)(?:\?|$)",

            # A to B traffic
            r"(.+?)\s+to\s+(.+?)\s+traffic(?:\?|$)"
        ]

        for pattern in patterns:

            match = re.search(
                pattern,
                question,
                re.IGNORECASE
            )

            if match:

                source = (
                    match.group(1)
                    .strip()
                )

                destination = (
                    match.group(2)
                    .strip()
                )

                return (
                    source,
                    destination
                )

        return None, None

    # ============================================================
    # EXTRACT STANDALONE LOCATION
    # ============================================================

    def extract_location_question(
        self,
        question
    ):

        patterns = [

            # traffic in Kukatpally
            r"traffic\s+"
            r"(?:in|at|near|around)\s+"
            r"(.+?)(?:\?|$)",

            # traffic around Hitech City
            r"(?:traffic|congestion)\s+"
            r"(?:in|at|near|around)\s+"
            r"(.+?)(?:\?|$)",

            # How is traffic in X?
            r"(?:how(?:'s| is)?|what(?:'s| is)?)"
            r"\s+(?:the\s+)?traffic\s+"
            r"(?:like\s+)?"
            r"(?:in|at|near|around)\s+"
            r"(.+?)(?:\?|$)",

            # Is traffic heavy in X?
            r"(?:is|are)\s+"
            r"(?:there\s+)?"
            r"(?:heavy|bad|high|good|slow)?\s*"
            r"traffic\s+"
            r"(?:in|at|near|around)\s+"
            r"(.+?)(?:\?|$)",

            # X traffic
            r"(.+?)\s+"
            r"(?:traffic|congestion)"
            r"(?:\s+right\s+now)?"
            r"(?:\?|$)"
        ]

        for pattern in patterns:

            match = re.search(
                pattern,
                question,
                re.IGNORECASE
            )

            if match:

                location = (
                    match.group(1)
                    .strip()
                )

                # Remove common trailing words
                location = re.sub(
                    r"\b("
                    r"right now|"
                    r"currently|"
                    r"today|"
                    r"now|"
                    r"please"
                    r")\b",
                    "",
                    location,
                    flags=re.IGNORECASE
                ).strip()

                # Remove unnecessary punctuation
                location = location.strip(
                    " ,."
                )

                if location:

                    return location

        return None

    # ============================================================
    # MAIN TRAFFIC FUNCTION
    # ============================================================

    def get_traffic(
        self,
        question
    ):

        question = question.strip()

        # ========================================================
        # 1. CHECK ROUTE TRAFFIC
        # ========================================================

        source, destination = (
            self.extract_route(
                question
            )
        )

        if source and destination:

            return self.calculate_route(
                source,
                destination
            )

        # ========================================================
        # 2. CHECK STANDALONE LOCATION TRAFFIC
        # ========================================================

        location = (
            self.extract_location_question(
                question
            )
        )

        if location:

            return self.get_location_traffic(
                location
            )

        # ========================================================
        # 3. IF QUESTION ITSELF IS A LOCATION
        # ========================================================

        clean_question = (
            question
            .lower()
            .strip()
            .rstrip("?")
        )

        if clean_question in self.location_aliases:

            return self.get_location_traffic(
                clean_question
            )

        # ========================================================
        # 4. NO LOCATION
        # ========================================================

        return {

            "error":
                "Please provide a route or location. "
                "For example: "
                "'traffic in Kukatpally' or "
                "'traffic from LB Nagar to Hitech City'."
        }

    # ============================================================
    # MULTI-DESTINATION TRAFFIC
    # ============================================================

    def get_multi_destination_traffic(
        self,
        source,
        destinations
    ):

        locations = [
            source
        ] + destinations

        legs = []

        total_distance = 0
        total_travel_time = 0
        total_delay = 0

        for i in range(
            len(locations) - 1
        ):

            leg_source = locations[i]

            leg_destination = (
                locations[i + 1]
            )

            result = self.get_traffic(
                f"from {leg_source} "
                f"to {leg_destination}"
            )

            if "error" in result:

                return {
                    "error":
                        result["error"]
                }

            legs.append(
                result
            )

            total_distance += result.get(
                "distance_km",
                0
            )

            total_travel_time += result.get(
                "travel_time_minutes",
                0
            )

            total_delay += result.get(
                "traffic_delay_minutes",
                0
            )

        return {

            "source":
                source,

            "destinations":
                destinations,

            "legs":
                legs,

            "total_distance_km":
                round(
                    total_distance,
                    2
                ),

            "total_travel_time_minutes":
                round(
                    total_travel_time,
                    2
                ),

            "total_traffic_delay_minutes":
                round(
                    total_delay,
                    2
                )
        }


# ================================================================
# TESTING
# ================================================================

if __name__ == "__main__":

    agent = TrafficAgent()

    print("\n================================")
    print("ROUTE TRAFFIC TEST")
    print("================================")

    print(
        agent.get_traffic(
            "How is traffic from LB Nagar to Hitech City?"
        )
    )

    print("\n================================")
    print("LOCATION TRAFFIC TEST")
    print("================================")

    locations = [

        "Kukatpally",
        "Gachibowli",
        "Madhapur",
        "Hitech City",
        "Ameerpet",
        "Kondapur",
        "Miyapur",
        "Uppal",
        "Nagole",
        "Tarnaka",
        "Dilsukhnagar",
        "Kothapet",
        "Secunderabad",
        "Mehdipatnam",
        "Banjara Hills",
        "Jubilee Hills",
        "Charminar",
        "Begumpet",
        "Manikonda",
        "Narsingi"
    ]

    for location in locations:

        print(
            f"\nTraffic in {location}:"
        )

        result = agent.get_traffic(
            f"How is traffic in {location}?"
        )

        print(result)