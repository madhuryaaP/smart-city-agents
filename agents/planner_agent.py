import re
from datetime import datetime, timedelta


class PlannerAgent:

    def parse_request(self, user_input):

        match = re.search(
            r"reach\s+(.+?)\s+from\s+(.+?)\s+by\s+(\d{1,2})(?::(\d{2}))?\s*(AM|PM)",
            user_input,
            re.IGNORECASE
        )

        if not match:
            return {
                "error": "Please provide destination, source, and arrival time."
            }

        destination = match.group(1).strip()
        source = match.group(2).strip()

        hour = int(match.group(3))
        minute = int(match.group(4) or 0)
        period = match.group(5).upper()

        if period == "PM" and hour != 12:
            hour += 12

        elif period == "AM" and hour == 12:
            hour = 0

        arrival_time = f"{hour:02d}:{minute:02d}"

        return {
            "source": source,
            "destination": destination,
            "arrival_time": arrival_time
        }


    def calculate_departure(
        self,
        destinations,
        arrival_time,
        traffic_delay=0,
        weather="no_rain"
    ):

        total_minutes = 0

        for place in destinations:
            total_minutes += place["travel_time"]

        total_minutes += round(traffic_delay)

        if weather == "rain":
            total_minutes += 20

        arrival = datetime.strptime(
            arrival_time,
            "%H:%M"
        )

        departure = arrival - timedelta(
            minutes=total_minutes
        )

        return {
            "destinations": destinations,
            "weather": weather,
            "traffic_delay_minutes": round(
                traffic_delay
            ),
            "total_travel_minutes": total_minutes,
            "recommended_departure": departure.strftime(
                "%H:%M"
            ),
            "arrival_time": arrival.strftime(
                "%H:%M"
            )
        }

# TEST CODE MUST BE AT THE LEFT EDGE
if __name__ == "__main__":
    agent = PlannerAgent()

    result = agent.search_location(
        "Keshav Memorial Institute of Technology"
    )

    print(result)