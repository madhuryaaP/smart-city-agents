import re
import os
import requests
from dotenv import load_dotenv

load_dotenv()


class TrafficAgent:

    def __init__(self):
        self.tomtom_api_key = os.getenv("TOMTOM_API_KEY")

        # ========================================================
        # HYDERABAD KNOWN LOCATIONS (hardcoded coordinates)
        # ========================================================

        self.known_locations = {

            # ---- KMIT / EAST HYDERABAD ----
            "kmit": (17.5449, 78.5718, "KMIT, Hyderabad"),
            "keshav memorial institute of technology": (17.5449, 78.5718, "KMIT, Hyderabad"),
            "lb nagar": (17.3457, 78.5522, "LB Nagar, Hyderabad"),
            "l.b. nagar": (17.3457, 78.5522, "LB Nagar, Hyderabad"),
            "l b nagar": (17.3457, 78.5522, "LB Nagar, Hyderabad"),
            "lbnagar": (17.3457, 78.5522, "LB Nagar, Hyderabad"),
            "lb nagar junction": (17.3457, 78.5522, "LB Nagar, Hyderabad"),
            "kothapet": (17.3641, 78.5331, "Kothapet, Hyderabad"),
            "dilsukhnagar": (17.3688, 78.5247, "Dilsukhnagar, Hyderabad"),
            "dilshuknagar": (17.3688, 78.5247, "Dilsukhnagar, Hyderabad"),
            "malakpet": (17.3783, 78.5068, "Malakpet, Hyderabad"),
            "saroornagar": (17.3550, 78.5380, "Saroornagar, Hyderabad"),
            "saroor nagar": (17.3550, 78.5380, "Saroornagar, Hyderabad"),
            "nagole": (17.3858, 78.5580, "Nagole, Hyderabad"),
            "uppal": (17.3954, 78.5593, "Uppal, Hyderabad"),
            "uppal junction": (17.3954, 78.5593, "Uppal, Hyderabad"),
            "habsiguda": (17.4019, 78.5338, "Habsiguda, Hyderabad"),
            "nacharam": (17.4047, 78.5505, "Nacharam, Hyderabad"),
            "tarnaka": (17.4283, 78.5290, "Tarnaka, Hyderabad"),
            "malkajgiri": (17.4470, 78.5270, "Malkajgiri, Hyderabad"),
            "ecil": (17.4544, 78.5601, "ECIL, Hyderabad"),
            "as rao nagar": (17.4540, 78.5404, "AS Rao Nagar, Hyderabad"),
            "ramanthapur": (17.3970, 78.5400, "Ramanthapur, Hyderabad"),
            "meerpet": (17.3200, 78.5270, "Meerpet, Hyderabad"),
            "karmanghat": (17.3350, 78.5350, "Karmanghat, Hyderabad"),
            "saidabad": (17.3560, 78.5050, "Saidabad, Hyderabad"),
            "almasguda": (17.3100, 78.5500, "Almasguda, Hyderabad"),
            "narayanaguda": (17.3950, 78.4850, "Narayanaguda, Hyderabad"),

            # ---- WEST HYDERABAD ----
            "hitech city": (17.4435, 78.3772, "HITEC City, Hyderabad"),
            "hi tech city": (17.4435, 78.3772, "HITEC City, Hyderabad"),
            "hitec city": (17.4435, 78.3772, "HITEC City, Hyderabad"),
            "hitec": (17.4435, 78.3772, "HITEC City, Hyderabad"),
            "madhapur": (17.4400, 78.3909, "Madhapur, Hyderabad"),
            "kondapur": (17.4571, 78.3649, "Kondapur, Hyderabad"),
            "gachibowli": (17.4401, 78.3489, "Gachibowli, Hyderabad"),
            "financial district": (17.4218, 78.3400, "Financial District, Hyderabad"),
            "nanakramguda": (17.4150, 78.3600, "Nanakramguda, Hyderabad"),
            "kokapet": (17.3950, 78.3400, "Kokapet, Hyderabad"),
            "narsingi": (17.3830, 78.3550, "Narsingi, Hyderabad"),
            "manikonda": (17.4020, 78.3780, "Manikonda, Hyderabad"),
            "gowlidoddi": (17.4180, 78.3800, "Gowlidoddi, Hyderabad"),
            "raidurg": (17.4310, 78.3870, "Raidurg, Hyderabad"),
            "raidurgam": (17.4310, 78.3870, "Raidurg, Hyderabad"),
            "durgam cheruvu": (17.4340, 78.3810, "Durgam Cheruvu, Hyderabad"),
            "mindspace": (17.4370, 78.3830, "Mindspace, Hyderabad"),
            "cyber towers": (17.4480, 78.3780, "Cyber Towers, Hyderabad"),
            "biodiversity junction": (17.4260, 78.3770, "Biodiversity Junction, Hyderabad"),

            # ---- NORTH-WEST HYDERABAD ----
            "kukatpally": (17.4849, 78.4138, "Kukatpally, Hyderabad"),
            "kphb": (17.4890, 78.3940, "KPHB, Hyderabad"),
            "kphb colony": (17.4890, 78.3940, "KPHB, Hyderabad"),
            "miyapur": (17.4970, 78.3520, "Miyapur, Hyderabad"),
            "bachupally": (17.5320, 78.3700, "Bachupally, Hyderabad"),
            "nizampet": (17.5180, 78.3830, "Nizampet, Hyderabad"),
            "pragathi nagar": (17.5100, 78.3700, "Pragathi Nagar, Hyderabad"),
            "moosapet": (17.4660, 78.4260, "Moosapet, Hyderabad"),
            "balanagar": (17.4710, 78.4430, "Balanagar, Hyderabad"),
            "balanagar junction": (17.4710, 78.4430, "Balanagar, Hyderabad"),
            "jeedimetla": (17.5010, 78.4460, "Jeedimetla, Hyderabad"),
            "chintal": (17.4950, 78.4200, "Chintal, Hyderabad"),
            "suraram": (17.5360, 78.4400, "Suraram, Hyderabad"),
            "alwal": (17.5010, 78.5100, "Alwal, Hyderabad"),
            "quthbullapur": (17.5200, 78.4600, "Quthbullapur, Hyderabad"),
            "qutbullapur": (17.5200, 78.4600, "Quthbullapur, Hyderabad"),
            "hafeezpet": (17.4800, 78.3700, "Hafeezpet, Hyderabad"),
            "chandanagar": (17.4860, 78.3270, "Chandanagar, Hyderabad"),
            "chanda nagar": (17.4860, 78.3270, "Chandanagar, Hyderabad"),
            "serilingampally": (17.4630, 78.3350, "Serilingampally, Hyderabad"),
            "allwyn colony": (17.4790, 78.3950, "Allwyn Colony, Hyderabad"),
            "bhel": (17.4720, 78.3100, "BHEL, Hyderabad"),
            "patancheru": (17.5320, 78.2700, "Patancheru, Hyderabad"),
            "jntu junction": (17.4930, 78.3860, "JNTU Junction, Hyderabad"),
            "suchitra junction": (17.4880, 78.5000, "Suchitra Junction, Hyderabad"),

            # ---- CENTRAL HYDERABAD ----
            "ameerpet": (17.4375, 78.4482, "Ameerpet, Hyderabad"),
            "begumpet": (17.4440, 78.4750, "Begumpet, Hyderabad"),
            "panjagutta": (17.4290, 78.4520, "Panjagutta, Hyderabad"),
            "somajiguda": (17.4370, 78.4660, "Somajiguda, Hyderabad"),
            "khairatabad": (17.4170, 78.4570, "Khairatabad, Hyderabad"),
            "khairtabad": (17.4170, 78.4570, "Khairatabad, Hyderabad"),
            "abids": (17.3950, 78.4750, "Abids, Hyderabad"),
            "koti": (17.3880, 78.4830, "Koti, Hyderabad"),
            "nampally": (17.3920, 78.4680, "Nampally, Hyderabad"),
            "nampally junction": (17.3920, 78.4680, "Nampally, Hyderabad"),
            "basheerbagh": (17.4020, 78.4700, "Basheerbagh, Hyderabad"),
            "lakdikapul": (17.4080, 78.4600, "Lakdikapul, Hyderabad"),
            "masab tank": (17.4130, 78.4520, "Masab Tank, Hyderabad"),
            "mehdipatnam": (17.3950, 78.4400, "Mehdipatnam, Hyderabad"),
            "tolichowki": (17.4050, 78.4200, "Tolichowki, Hyderabad"),
            "shaikpet": (17.4120, 78.4080, "Shaikpet, Hyderabad"),

            # ---- JUBILEE HILLS / BANJARA HILLS ----
            "jubilee hills": (17.4320, 78.4120, "Jubilee Hills, Hyderabad"),
            "banjara hills": (17.4230, 78.4430, "Banjara Hills, Hyderabad"),
            "film nagar": (17.4180, 78.4270, "Film Nagar, Hyderabad"),
            "yousufguda": (17.4350, 78.4350, "Yousufguda, Hyderabad"),
            "srinagar colony": (17.4270, 78.4370, "Srinagar Colony, Hyderabad"),

            # ---- SECUNDERABAD ----
            "secunderabad": (17.4399, 78.4983, "Secunderabad, Hyderabad"),
            "paradise": (17.4416, 78.4831, "Paradise, Hyderabad"),
            "paradise circle": (17.4416, 78.4831, "Paradise, Hyderabad"),
            "tirmulgherry": (17.4710, 78.5060, "Tirmulgherry, Hyderabad"),
            "marredpally": (17.4540, 78.4970, "Marredpally, Hyderabad"),
            "musheerabad": (17.4170, 78.4940, "Musheerabad, Hyderabad"),
            "bowenpally": (17.4620, 78.4790, "Bowenpally, Hyderabad"),
            "old bowenpally": (17.4670, 78.4770, "Old Bowenpally, Hyderabad"),
            "tadbund": (17.4580, 78.4720, "Tadbund, Hyderabad"),
            "mettuguda": (17.4370, 78.5080, "Mettuguda, Hyderabad"),
            "sangeet": (17.4580, 78.4940, "Sangeet, Hyderabad"),

            # ---- OLD CITY ----
            "old city": (17.3616, 78.4747, "Charminar, Hyderabad"),
            "old city hyderabad": (17.3616, 78.4747, "Charminar, Hyderabad"),
            "charminar": (17.3616, 78.4747, "Charminar, Hyderabad"),
            "chandrayangutta": (17.3310, 78.4860, "Chandrayangutta, Hyderabad"),
            "falaknuma": (17.3410, 78.4670, "Falaknuma, Hyderabad"),
            "santoshnagar": (17.3550, 78.5200, "Santoshnagar, Hyderabad"),

            # ---- AIRPORT / SOUTH HYDERABAD ----
            "shamshabad": (17.2403, 78.4294, "Shamshabad, Hyderabad"),
            "rajiv gandhi airport": (17.2403, 78.4294, "RGIA, Hyderabad"),
            "rajiv gandhi international airport": (17.2403, 78.4294, "RGIA, Hyderabad"),
            "airport": (17.2403, 78.4294, "RGIA, Hyderabad"),
            "tukkuguda": (17.2700, 78.4700, "Tukkuguda, Hyderabad"),

            "adibatla": (17.2800, 78.5100, "Adibatla, Hyderabad"),

            # ---- OUTER RING ROAD ----
            "orr": (17.4200, 78.3600, "Outer Ring Road, Hyderabad"),
            "outer ring road": (17.4200, 78.3600, "Outer Ring Road, Hyderabad"),
        }

    # ============================================================
    # SEARCH LOCATION USING TOMTOM
    # ============================================================

    def search_location(self, location):

        original_location = location.strip()
        clean_location = original_location.lower()

        # Return instantly for known locations
        if clean_location in self.known_locations:
            lat, lon, name = self.known_locations[
                clean_location
            ]
            return {
                "latitude": lat,
                "longitude": lon,
                "display_name": name
            }

        # Fallback to TomTom API for unknown locations
        if not self.tomtom_api_key:
            return None

        candidates = [
            f"{original_location}, Hyderabad, India",
            f"{original_location}, Telangana, India"
        ]

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
                    timeout=8
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
                timeout=8
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
                timeout=8
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

        if clean_question in self.known_locations:

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