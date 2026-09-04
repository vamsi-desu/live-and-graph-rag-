import os
import requests
from dotenv import load_dotenv

from generator import generate_answer


# --------------------------------------------------
# LOAD ENVIRONMENT VARIABLES
# --------------------------------------------------

load_dotenv()

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")


# --------------------------------------------------
# GET LOCATION COORDINATES
# --------------------------------------------------

def get_coordinates(city):

    url = "https://api.openweathermap.org/geo/1.0/direct"

    params = {
        "q": f"{city},IN",
        "limit": 1,
        "appid": WEATHER_API_KEY
    }

    response = requests.get(
        url,
        params=params,
        timeout=10
    )

    response.raise_for_status()

    locations = response.json()

    if not locations:
        raise ValueError(
            f"Location '{city}' was not found."
        )

    location = locations[0]

    return {
        "name": location.get("name"),
        "state": location.get("state"),
        "country": location.get("country"),
        "lat": location.get("lat"),
        "lon": location.get("lon")
    }


# --------------------------------------------------
# GET LIVE WEATHER
# --------------------------------------------------

def get_live_weather(city):

    if not WEATHER_API_KEY:
        raise ValueError(
            "WEATHER_API_KEY is not configured in the .env file."
        )

    # --------------------------------------------------
    # STEP 1: CONVERT CITY -> LATITUDE/LONGITUDE
    # --------------------------------------------------

    location = get_coordinates(city)

    latitude = location["lat"]
    longitude = location["lon"]

    # --------------------------------------------------
    # STEP 2: GET WEATHER USING COORDINATES
    # --------------------------------------------------

    url = "https://api.openweathermap.org/data/2.5/weather"

    params = {
        "lat": latitude,
        "lon": longitude,
        "appid": WEATHER_API_KEY,
        "units": "metric"
    }

    response = requests.get(
        url,
        params=params,
        timeout=10
    )

    response.raise_for_status()

    data = response.json()

    # --------------------------------------------------
    # STEP 3: EXTRACT WEATHER INFORMATION
    # --------------------------------------------------

    weather_context = {
        "city": data.get("name"),
        "state": location.get("state"),
        "country": data.get("sys", {}).get("country"),
        "latitude": latitude,
        "longitude": longitude,
        "temperature": data.get("main", {}).get("temp"),
        "feels_like": data.get("main", {}).get("feels_like"),
        "humidity": data.get("main", {}).get("humidity"),
        "weather": data.get("weather", [{}])[0].get("description"),
        "wind_speed": data.get("wind", {}).get("speed")
    }

    return weather_context


# --------------------------------------------------
# LIVE RAG QUERY
# --------------------------------------------------

def live_rag_query(question, city):

    print("\nLIVE RAG")
    print("-------------------------")

    print(f"Question: {question}")
    print(f"City: {city}")

    # --------------------------------------------------
    # STEP 1: GET LIVE WEATHER
    # --------------------------------------------------

    weather_data = get_live_weather(city)

    # --------------------------------------------------
    # STEP 2: FORMAT LIVE DATA
    # --------------------------------------------------

    context = f"""
Live Weather Information

City: {weather_data["city"]}
State: {weather_data["state"]}
Country: {weather_data["country"]}

Latitude: {weather_data["latitude"]}
Longitude: {weather_data["longitude"]}

Temperature: {weather_data["temperature"]} °C
Feels Like: {weather_data["feels_like"]} °C
Humidity: {weather_data["humidity"]}%
Weather: {weather_data["weather"]}
Wind Speed: {weather_data["wind_speed"]} m/s
"""

    # --------------------------------------------------
    # DEBUG
    # --------------------------------------------------

    print("\nLIVE CONTEXT")
    print("-------------------------")
    print(context)

    # --------------------------------------------------
    # STEP 3: GENERATE ANSWER
    # --------------------------------------------------

    answer = generate_answer(
        question,
        context
    )

    print("\nFINAL ANSWER")
    print("-------------------------")

    return answer


# --------------------------------------------------
# TEST
# --------------------------------------------------

if __name__ == "__main__":

    answer = live_rag_query(
        question="What is the weather in Chilakaluripet?",
        city="Chilakaluripet"
    )

    print(answer)



