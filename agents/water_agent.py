import re
import os
import requests
from dotenv import load_dotenv

load_dotenv()


class WaterAgent:

    def __init__(self):

        self.openweather_api_key = os.getenv(
            "OPENWEATHER_API_KEY"
        )

        # ========================================================
        # HYDERABAD LOCATION ALIASES
        # ========================================================

        self.location_aliases = {

            "kmit":
                "Hyderabad",

            "keshav memorial institute of technology":
                "Hyderabad",

            "keshav memorial institute of technology hyderabad":
                "Hyderabad",

            "lb nagar":
                "LB Nagar",

            "l.b. nagar":
                "LB Nagar",

            "l b nagar":
                "LB Nagar",

            "lbnagar":
                "LB Nagar",

            "kothapet":
                "Kothapet",

            "dilsukhnagar":
                "Dilsukhnagar",

            "malakpet":
                "Malakpet",

            "saroornagar":
                "Saroornagar",

            "nagole":
                "Nagole",

            "uppal":
                "Uppal",

            "habsiguda":
                "Habsiguda",

            "tarnaka":
                "Tarnaka",

            "malkajgiri":
                "Malkajgiri",

            "ecil":
                "ECIL",

            "as rao nagar":
                "AS Rao Nagar",

            "hitech city":
                "HITEC City",

            "hi tech city":
                "HITEC City",

            "hitec city":
                "HITEC City",

            "hitec":
                "HITEC City",

            "madhapur":
                "Madhapur",

            "kondapur":
                "Kondapur",

            "gachibowli":
                "Gachibowli",

            "financial district":
                "Financial District",

            "nanakramguda":
                "Nanakramguda",

            "kokapet":
                "Kokapet",

            "narsingi":
                "Narsingi",

            "manikonda":
                "Manikonda",

            "raidurg":
                "Raidurg",

            "durgam cheruvu":
                "Durgam Cheruvu",

            "kukatpally":
                "Kukatpally",

            "kphb":
                "KPHB",

            "kphb colony":
                "KPHB",

            "miyapur":
                "Miyapur",

            "bachupally":
                "Bachupally",

            "nizampet":
                "Nizampet",

            "pragathi nagar":
                "Pragathi Nagar",

            "moosapet":
                "Moosapet",

            "balanagar":
                "Balanagar",

            "jeedimetla":
                "Jeedimetla",

            "chintal":
                "Chintal",

            "hafeezpet":
                "Hafeezpet",

            "chandanagar":
                "Chandanagar",

            "serilingampally":
                "Serilingampally",

            "bhel":
                "BHEL",

            "patancheru":
                "Patancheru",

            "ameerpet":
                "Ameerpet",

            "begumpet":
                "Begumpet",

            "panjagutta":
                "Panjagutta",

            "somajiguda":
                "Somajiguda",

            "khairatabad":
                "Khairatabad",

            "abids":
                "Abids",

            "koti":
                "Koti",

            "nampally":
                "Nampally",

            "basheerbagh":
                "Basheerbagh",

            "lakdikapul":
                "Lakdikapul",

            "masab tank":
                "Masab Tank",

            "mehdipatnam":
                "Mehdipatnam",

            "tolichowki":
                "Tolichowki",

            "shaikpet":
                "Shaikpet",

            "jubilee hills":
                "Jubilee Hills",

            "banjara hills":
                "Banjara Hills",

            "film nagar":
                "Film Nagar",

            "yousufguda":
                "Yousufguda",

            "srinagar colony":
                "Srinagar Colony",

            "secunderabad":
                "Secunderabad",

            "paradise":
                "Paradise",

            "musheerabad":
                "Musheerabad",

            "bowenpally":
                "Bowenpally",

            "tadbund":
                "Tadbund",

            "mettuguda":
                "Mettuguda",

            "charminar":
                "Charminar",

            "chandrayangutta":
                "Chandrayangutta",

            "falaknuma":
                "Falaknuma",

            "saidabad":
                "Saidabad",

            "santoshnagar":
                "Santoshnagar",

            "shamshabad":
                "Shamshabad",

            "rajiv gandhi airport":
                "Rajiv Gandhi International Airport",

            "airport":
                "Rajiv Gandhi International Airport",

            "tukkuguda":
                "Tukkuguda",

            "adibatla":
                "Adibatla",

            "barkatpura":
                "Barkatpura"

        }

    # ========================================================
    # EXTRACT LOCATION
    # ========================================================

    def extract_location(self, user_input):

        text = user_input.strip()

        patterns = [

            r"(?:weather|temperature|rain|rainfall)"
            r"\s+(?:in|at|near|around)\s+"
            r"(.+?)(?:\?|$)",

            r"flood\s+risk\s+"
            r"(?:in|at|near|around)\s+"
            r"(.+?)(?:\?|$)",

            r"waterlogging\s+"
            r"(?:in|at|near|around)\s+"
            r"(.+?)(?:\?|$)",

            r"(?:raining|rain)"
            r".*?"
            r"(?:in|at|near|around)\s+"
            r"(.+?)(?:\?|$)"
        ]

        for pattern in patterns:

            match = re.search(
                pattern,
                text,
                re.IGNORECASE
            )

            if match:

                location = match.group(1).strip()

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

                return location.strip(" ,.")

        return text.strip(" ,.")

    # ========================================================
    # NORMALIZE LOCATION
    # ========================================================

    def normalize_location(self, location):

        clean = location.strip().lower()

        return self.location_aliases.get(
            clean,
            location.strip()
        )

    # ========================================================
    # GEOCODE LOCATION
    # ========================================================

    def geocode_location(self, location):

        url = (
            "https://api.openweathermap.org/"
            "geo/1.0/direct"
        )

        # IMPORTANT:
        # Do not append Hyderabad to an already
        # normalized Hyderabad location.

        candidates = [
            f"{location}, Hyderabad, India",
            f"{location}, Telangana, India",
            location
        ]

        # Remove duplicates
        candidates = list(
            dict.fromkeys(candidates)
        )

        for candidate in candidates:

            try:

                print(
                    f"[Weather Geocoding] Trying: "
                    f"{candidate}"
                )

                response = requests.get(
                    url,
                    params={
                        "q": candidate,
                        "limit": 1,
                        "appid":
                            self.openweather_api_key
                    },
                    timeout=20
                )

                # Don't immediately crash on a failed candidate
                if response.status_code != 200:

                    print(
                        f"[Weather Geocoding] "
                        f"{candidate} -> "
                        f"{response.status_code}"
                    )

                    continue

                results = response.json()

                if results:

                    return results[0]

            except requests.RequestException as e:

                print(
                    f"[Weather Geocoding Error] "
                    f"{candidate}: {e}"
                )

        return None

    # ========================================================
    # GET WEATHER
    # ========================================================

    def get_weather(self, area):

        if not self.openweather_api_key:

            return {
                "error":
                    "OPENWEATHER_API_KEY is not configured."
            }

        # ----------------------------------------------------
        # Extract location
        # ----------------------------------------------------

        original_location = self.extract_location(
            area
        )

        # ----------------------------------------------------
        # Normalize common names
        # ----------------------------------------------------

        location = self.normalize_location(
            original_location
        )

        print(
            f"[Weather Agent] "
            f"Detected location: {location}"
        )

        # ----------------------------------------------------
        # Special case:
        # KMIT should simply use Hyderabad
        # ----------------------------------------------------

        if location.lower() == "hyderabad":

            location_to_search = "Hyderabad"

        else:

            location_to_search = location

        # ----------------------------------------------------
        # Geocode
        # ----------------------------------------------------

        location_data = self.geocode_location(
            location_to_search
        )

        if location_data is None:

            return {
                "area":
                    original_location,

                "error":
                    f"Could not find weather location: "
                    f"{original_location}"
            }

        latitude = location_data["lat"]
        longitude = location_data["lon"]

        resolved_name = location_data.get(
            "name",
            original_location
        )

        print(
            f"[Weather Agent] "
            f"Resolved: {resolved_name} "
            f"({latitude}, {longitude})"
        )

        # ====================================================
        # CURRENT WEATHER
        # ====================================================

        weather_url = (
            "https://api.openweathermap.org/"
            "data/2.5/weather"
        )

        try:

            response = requests.get(
                weather_url,
                params={
                    "lat":
                        latitude,

                    "lon":
                        longitude,

                    "appid":
                        self.openweather_api_key,

                    "units":
                        "metric"
                },
                timeout=20
            )

            response.raise_for_status()

            data = response.json()

        except requests.RequestException as e:

            print(
                f"[Weather API Error]: {e}"
            )

            return {
                "area":
                    original_location,

                "error":
                    "Weather data is unavailable "
                    "at the moment."
            }

        # ====================================================
        # EXTRACT DATA
        # ====================================================

        main_data = data.get(
            "main",
            {}
        )

        temperature = main_data.get(
            "temp"
        )

        humidity = main_data.get(
            "humidity"
        )

        weather_list = data.get(
            "weather",
            []
        )

        if weather_list:

            weather_description = (
                weather_list[0]
                .get(
                    "description",
                    "unavailable"
                )
            )

        else:

            weather_description = "unavailable"

        rainfall_mm = (
            data.get(
                "rain",
                {}
            )
            .get(
                "1h",
                0
            )
        )

        # ====================================================
        # FLOOD RISK
        # ====================================================

        if rainfall_mm > 10:

            flood_risk = "high"

        elif rainfall_mm >= 2:

            flood_risk = "moderate"

        else:

            flood_risk = "low"

        # ====================================================
        # RESULT
        # ====================================================

        return {

            "area":
                original_location,

            "resolved_location":
                resolved_name,

            "temperature_c":
                temperature,

            "humidity":
                humidity,

            "weather":
                weather_description,

            "rainfall_mm_last_1h":
                rainfall_mm,

            "flood_risk":
                flood_risk
        }


# ================================================================
# DIRECT TEST
# ================================================================

if __name__ == "__main__":

    agent = WaterAgent()

    tests = [

        "How is the weather in Kothapet?",

        "What's the weather in KMIT?",

        "How is the weather in Hitech City?",

        "Is it raining in Kukatpally?",

        "What's the weather in Gachibowli?",

        "What is the weather in Madhapur?",

        "What's the flood risk in LB Nagar?"
    ]

    for question in tests:

        print("\n========================================")
        print("QUESTION:", question)
        print("========================================")

        result = agent.get_weather(
            question
        )

        print(result)