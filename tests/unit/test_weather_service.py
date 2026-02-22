"""
Tests unitarios para app.services.weather_service.
Pruebas de validación de coordenadas y de get_weather con respuesta mockeada.
"""
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.services.weather_service import (
    _are_valid_coordinates,
    get_weather,
)


# ---------------------------------------------------------------------------
# Validación de coordenadas (función interna; se prueba vía comportamiento)
# ---------------------------------------------------------------------------

def test_valid_coordinates_ok():
    """Coordenadas válidas dentro de rango."""
    assert _are_valid_coordinates(-12.0, -77.0) is True
    assert _are_valid_coordinates(40.4, -3.7) is True
    assert _are_valid_coordinates(0.0, 1.0) is True
    assert _are_valid_coordinates(1.0, 0.0) is True


def test_valid_coordinates_rechaza_cero_cero():
    """(0, 0) se considera inválido para evitar peticiones por defecto."""
    assert _are_valid_coordinates(0.0, 0.0) is False


def test_valid_coordinates_fuera_de_rango():
    """Latitud fuera de [-90, 90] o longitud fuera de [-180, 180]."""
    assert _are_valid_coordinates(91.0, 0.0) is False
    assert _are_valid_coordinates(-91.0, 0.0) is False
    assert _are_valid_coordinates(0.0, 181.0) is False
    assert _are_valid_coordinates(0.0, -181.0) is False


# ---------------------------------------------------------------------------
# get_weather con HTTP mockeado
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_get_weather_sin_api_key_retorna_none():
    """Si WEATHER_API_KEY no está definida, get_weather retorna None."""
    with patch.dict("os.environ", {}, clear=False):
        # Forzar reimport para que tome el env vacío (o mockear el módulo)
        with patch("app.services.weather_service.WEATHER_API_KEY", ""):
            result = await get_weather(-12.0, -77.0)
    assert result is None


@pytest.mark.asyncio
async def test_get_weather_coordenadas_invalidas_retorna_none():
    """Coordenadas (0,0) no llaman a la API y retornan None."""
    with patch("app.services.weather_service.WEATHER_API_KEY", "fake-key"):
        result = await get_weather(0.0, 0.0)
    assert result is None


@pytest.mark.asyncio
async def test_get_weather_respuesta_ok_parsea_correctamente():
    """Con respuesta JSON válida de WeatherAPI se parsea a WeatherData."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "location": {
            "name": "Lima",
            "region": "Lima",
            "country": "Peru",
            "localtime": "2025-02-21 14:30",
        },
        "current": {
            "temp_c": 22.0,
            "feelslike_c": 23.0,
            "humidity": 65,
            "wind_kph": 15.0,
            "wind_degree": 180,
            "is_day": 1,
            "condition": {"text": "Partly cloudy"},
        },
    }
    mock_response.raise_for_status = MagicMock()

    fake_client = AsyncMock()
    fake_client.get = AsyncMock(return_value=mock_response)
    fake_cm = AsyncMock()
    fake_cm.__aenter__.return_value = fake_client
    fake_cm.__aexit__.return_value = None

    with patch("app.services.weather_service.WEATHER_API_KEY", "fake-key"):
        with patch(
            "app.services.weather_service.httpx.AsyncClient",
            return_value=fake_cm,
        ):
            result = await get_weather(-12.0, -77.0)

    assert result is not None
    assert result["temperature"] == 22.0
    assert result["feelslike"] == 23.0
    assert result["humidity"] == 65
    assert result["condition"] == "Partly cloudy"
    assert result["location_name"] == "Lima"
    assert result["region"] == "Lima"
    assert result["country"] == "Peru"


@pytest.mark.asyncio
async def test_get_weather_http_error_retorna_none():
    """Si la API devuelve error HTTP, get_weather retorna None (no lanza)."""
    import httpx
    fake_client = AsyncMock()
    fake_client.get = AsyncMock(
        side_effect=httpx.HTTPStatusError(
            "404",
            request=httpx.Request("GET", "https://api.weatherapi.com/"),
            response=httpx.Response(404),
        )
    )
    fake_cm = AsyncMock()
    fake_cm.__aenter__.return_value = fake_client
    fake_cm.__aexit__.return_value = None

    with patch("app.services.weather_service.WEATHER_API_KEY", "fake-key"):
        with patch(
            "app.services.weather_service.httpx.AsyncClient",
            return_value=fake_cm,
        ):
            result = await get_weather(-12.0, -77.0)
    assert result is None
