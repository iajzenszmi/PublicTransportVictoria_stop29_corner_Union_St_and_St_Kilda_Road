import requests
from datetime import datetime, timezone
import hmac
import hashlib
import urllib.parse

# Constants
USER_ID = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
API_KEY = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
STOP_ID = 19565  # Stop ID for St Kilda Rd & Union St
ROUTE_TYPE = 1  # Route type for trams
BASE_URL = "https://timetableapi.ptv.vic.gov.au/v3"

def generate_signature(endpoint, user_id, api_key):
    raw = f"/v3/{endpoint}?devid={user_id}"
    signature = hmac.new(
        api_key.encode('utf-8'),
        raw.encode('utf-8'),
        hashlib.sha1
    ).hexdigest().upper()
    return signature

def fetch_tram_departures(stop_id, route_type, user_id, api_key):
    endpoint = f"departures/route_type/{route_type}/stop/{stop_id}"
    signature = generate_signature(endpoint, user_id, api_key)
    url = f"{BASE_URL}/{endpoint}?devid={user_id}&signature={signature}"
    
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching data: {response.status_code}")
        return None

def calculate_eta(departure_time_utc):
    now_utc = datetime.now(timezone.utc)
    departure_time = datetime.fromisoformat(departure_time_utc.replace('Z', '+00:00'))
    time_until_departure = departure_time - now_utc
    minutes, seconds = divmod(time_until_departure.total_seconds(), 60)
    return int(minutes), int(seconds)

def main():
    data = fetch_tram_departures(STOP_ID, ROUTE_TYPE, USER_ID, API_KEY)
    if data and 'departures' in data and data['departures']:
        for departure in data['departures']:
            route_id = departure.get('route_id')
            route_name = departure.get('route_name')
            if 'estimated_departure_utc' in departure:
                departure_time_utc = departure['estimated_departure_utc']
            else:
                departure_time_utc = departure['scheduled_departure_utc']
            minutes, seconds = calculate_eta(departure_time_utc)
            print(f"Route {route_id} ({route_name}): Next tram will arrive in {minutes} minutes and {seconds} seconds.")
    else:
        print("No upcoming tram departures found.")

if __name__ == "__main__":
    main()

