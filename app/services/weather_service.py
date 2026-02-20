import httpx
import os
from dotenv import load_dotenv

load_dotenv()

WEATHER_API_URL = "https://api.weatherapi.com/v1/current.json"
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")


async def get_weather(lat: float, lon: float):

    if not WEATHER_API_KEY:
        raise RuntimeError("WEATHER_API_KEY no está definida")

    params = {
        "key": WEATHER_API_KEY,
        "q": f"{lat},{lon}",
        "aqi": "no"
    }

    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(WEATHER_API_URL, params=params)

    print("WEATHER STATUS:", response.status_code)

    response.raise_for_status()

    data = response.json()
    current = data["current"]

    return {
        "temperature": current["temp_c"],
        "humidity": current["humidity"],
        "windspeed": current["wind_kph"],
        "winddirection": current["wind_degree"],
        "is_day": current["is_day"],
        "condition": current["condition"]["text"],
        "feelslike": current["feelslike_c"],
        "time": data["location"]["localtime"]
    }