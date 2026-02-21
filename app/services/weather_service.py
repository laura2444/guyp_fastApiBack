"""
Servicio de clima basado en WeatherAPI.com.
Obtiene condiciones actuales y datos de ubicación a partir de coordenadas GPS.
"""
import os
from typing import Optional, TypedDict

import httpx
from dotenv import load_dotenv

load_dotenv()

WEATHER_API_URL = "https://api.weatherapi.com/v1/current.json"
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
REQUEST_TIMEOUT_SEC = 10


class WeatherData(TypedDict):
    """Estructura de datos de clima para consumo interno y prompt."""
    temperature: float
    humidity: int
    windspeed: float
    winddirection: int
    is_day: int
    condition: str
    feelslike: float
    time: str
    location_name: str
    region: str
    country: str


def _are_valid_coordinates(lat: float, lon: float) -> bool:
    """
    Indica si las coordenadas son válidas para consultar clima.
    Evita (0, 0) y rangos fuera de límites.

    Returns:
        True si lat ∈ [-90, 90] y lon ∈ [-180, 180] y no es (0, 0) por defecto.
    """
    if lat == 0 and lon == 0:
        return False
    return -90 <= lat <= 90 and -180 <= lon <= 180


async def get_weather(lat: float, lon: float) -> Optional[WeatherData]:
    """
    Obtiene el clima actual y datos de ubicación para las coordenadas dadas.

    Args:
        lat: Latitud en grados decimales.
        lon: Longitud en grados decimales.

    Returns:
        Diccionario con temperatura, humedad, viento, condición, ubicación (nombre, región, país),
        o None si falta API key, coordenadas inválidas o hay error en la petición.
    """
    if not WEATHER_API_KEY or not WEATHER_API_KEY.strip():
        return None

    if not _are_valid_coordinates(lat, lon):
        return None

    params = {
        "key": WEATHER_API_KEY,
        "q": f"{lat},{lon}",
        "aqi": "no",
    }

    try:
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_SEC) as client:
            response = await client.get(WEATHER_API_URL, params=params)
        response.raise_for_status()
    except (httpx.HTTPError, httpx.TimeoutException) as e:
        # Log opcional; no romper el flujo si el clima falla
        print(f"[weather_service] Error obteniendo clima: {e}")
        return None

    try:
        data = response.json()
        loc = data.get("location", {})
        current = data.get("current", {})
        condition = current.get("condition") or {}

        return {
            "temperature": float(current.get("temp_c", 0)),
            "humidity": int(current.get("humidity", 0)),
            "windspeed": float(current.get("wind_kph", 0)),
            "winddirection": int(current.get("wind_degree", 0)),
            "is_day": 1 if current.get("is_day") else 0,
            "condition": str(condition.get("text", "")),
            "feelslike": float(current.get("feelslike_c", 0)),
            "time": str(loc.get("localtime", "")),
            "location_name": str(loc.get("name", "")),
            "region": str(loc.get("region", "")),
            "country": str(loc.get("country", "")),
        }
    except (KeyError, TypeError, ValueError) as e:
        print(f"[weather_service] Error parseando respuesta: {e}")
        return None
