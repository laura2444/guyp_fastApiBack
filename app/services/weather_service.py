import httpx
import asyncio

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

async def get_weather(lat: float, lon: float):

    params = {
        "latitude": lat,
        "longitude": lon,
        "current_weather": True
    }

    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(OPEN_METEO_URL, params=params)

    print("WEATHER STATUS:", response.status_code)
    print("WEATHER RESPONSE:", response.text)

    response.raise_for_status()

    data = response.json()

    return data.get("current_weather")

