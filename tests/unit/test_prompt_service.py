"""
Tests unitarios para app.services.prompt_service.
Pruebas de build_plant_prompt con/sin ubicación, con/sin clima, y claves lat/lng vs latitude/longitude.
"""
import sys
from pathlib import Path

# Asegurar que el proyecto esté en el path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.services.prompt_service import build_plant_prompt


def test_build_plant_prompt_sin_ubicacion_ni_clima():
    """Prompt solo con predicción: debe incluir enfermedad y confianza."""
    out = build_plant_prompt(
        prediction={
            "plant_type": "tomato",
            "disease": "Septoria leaf spot",
            "confidence": 0.92,
        },
        location={},
    )
    assert "tomato" in out
    assert "Septoria leaf spot" in out
    assert "92.0%" in out
    assert "coordenadas" not in out or "None" not in out
    assert "Condiciones climáticas" not in out


def test_build_plant_prompt_con_lat_lng():
    """Ubicación con claves lat/lng (estándar del backend)."""
    out = build_plant_prompt(
        prediction={"plant_type": "potato", "disease": "Late blight", "confidence": 0.88},
        location={"lat": -12.0, "lng": -77.0},
    )
    assert "potato" in out
    assert "Late blight" in out
    assert "-12.0" in out and "-77.0" in out
    assert "88.0%" in out


def test_build_plant_prompt_con_latitude_longitude():
    """Ubicación con claves latitude/longitude (fallback)."""
    out = build_plant_prompt(
        prediction={"plant_type": "pepper", "disease": "Bacterial spot"},
        location={"latitude": 40.4, "longitude": -3.7},
    )
    assert "40.4" in out and "-3.7" in out
    assert "pepper" in out and "Bacterial spot" in out


def test_build_plant_prompt_con_clima():
    """Con weather se incluye bloque de condiciones climáticas y lugar."""
    out = build_plant_prompt(
        prediction={"plant_type": "tomato", "disease": "Healthy", "confidence": 1.0},
        location={"lat": -12.0, "lng": -77.0},
        weather={
            "temperature": 22.0,
            "feelslike": 23.0,
            "humidity": 65,
            "condition": "Partly cloudy",
            "windspeed": 15.0,
            "winddirection": 180,
            "is_day": 1,
            "time": "2025-02-21 14:30",
            "location_name": "Lima",
            "region": "Lima",
            "country": "Peru",
        },
    )
    assert "Condiciones climáticas actuales" in out
    assert "22.0" in out and "23.0" in out
    assert "65%" in out
    assert "Partly cloudy" in out
    assert "Lima" in out and "Peru" in out
    assert "banderas rojas" in out.lower() or "Recomendaciones" in out


def test_build_plant_prompt_clima_sin_lugar():
    """Weather sin location_name/region/country no debe romper; no aparece línea 'Lugar:' vacía rara."""
    out = build_plant_prompt(
        prediction={"plant_type": "tomato", "disease": "X"},
        location={"lat": 0.0, "lng": 0.0},
        weather={
            "temperature": 10.0,
            "feelslike": 9.0,
            "humidity": 80,
            "condition": "Rain",
            "windspeed": 20.0,
            "winddirection": 270,
            "is_day": 0,
            "time": "",
            "location_name": "",
            "region": "",
            "country": "",
        },
    )
    assert "Condiciones climáticas actuales" in out
    assert "10.0" in out and "Rain" in out
    assert "Lugar:" not in out or "N/A" in out
