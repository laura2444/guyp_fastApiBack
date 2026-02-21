"""
Construcción de prompts para el modelo generativo (Gemini).
Incorpora predicción del modelo, ubicación y condiciones climáticas actuales.
"""
from typing import Any, Dict, Optional


def _format_weather_block(weather: Dict[str, Any]) -> str:
    """
    Formatea los datos de clima en un texto legible para el LLM.

    Args:
        weather: Diccionario con keys de WeatherData (temperature, humidity, etc.).

    Returns:
        Párrafo con condiciones actuales y ubicación si está disponible.
    """
    parts = [
        "Condiciones climáticas actuales en el lugar del análisis:",
        f"- Temperatura: {weather.get('temperature', 'N/A')} °C (sensación térmica: {weather.get('feelslike', 'N/A')} °C)",
        f"- Humedad: {weather.get('humidity', 'N/A')}%",
        f"- Condición: {weather.get('condition', 'N/A')}",
        f"- Viento: {weather.get('windspeed', 'N/A')} km/h, dirección {weather.get('winddirection', 'N/A')}°",
        f"- Es de día: {'Sí' if weather.get('is_day') else 'No'}",
        f"- Hora local (ubicación): {weather.get('time', 'N/A')}",
    ]
    location_name = weather.get("location_name", "").strip()
    region = weather.get("region", "").strip()
    country = weather.get("country", "").strip()
    if location_name or region or country:
        place_parts = [p for p in [location_name, region, country] if p]
        parts.append(f"- Lugar: {', '.join(place_parts)}")
    return "\n".join(parts)


def build_plant_prompt(
    prediction: Dict[str, Any],
    location: Dict[str, Any],
    weather: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Construye un prompt instructivo para el modelo generativo a partir de la
    predicción del modelo de visión, ubicación y opcionalmente clima actual.

    Args:
        prediction: Resultado del modelo de clasificación.
            Debe incluir "plant_type", "disease" y opcionalmente "confidence".
        location: Geolocalización. Se aceptan claves "lat"/"lng" o "latitude"/"longitude".
        weather: Opcional. Datos de clima actual (temperature, humidity, condition, etc.)
            y de ubicación (location_name, region, country). Si está presente se incluye
            en el prompt para contextualizar recomendaciones.

    Returns:
        Prompt en texto plano para enviar a Gemini.
    """
    plant_type = prediction.get("plant_type", "planta")
    disease = prediction.get("disease", "condición desconocida")
    confidence = prediction.get("confidence")

    # Unificar claves: el backend usa "lat"/"lng" (routes/orchestrator)
    lat = location.get("lat") or location.get("latitude")
    lon = location.get("lng") or location.get("longitude")

    # Bloque de ubicación (solo coordenadas si no hay weather con nombre de lugar)
    location_text = ""
    if lat is not None and lon is not None:
        location_text = (
            f"La planta se encuentra aproximadamente en las coordenadas "
            f"({lat}, {lon})."
        )
        if not weather:
            location_text += (
                " Ten en cuenta las condiciones climáticas y ambientales "
                "comunes de esta región."
            )
        location_text += "\n\n"

    # Bloque de clima actual (mejora mucho las recomendaciones del modelo)
    weather_block = ""
    if weather:
        weather_block = _format_weather_block(weather) + "\n\n"

    confidence_text = ""
    if confidence is not None:
        try:
            pct = float(confidence) * 100
            confidence_text = (
                f"El modelo tiene un nivel de confianza aproximado del {pct:.1f}% "
                "en esta predicción.\n\n"
            )
        except (TypeError, ValueError):
            pass

    prompt = f"""
Se ha analizado una imagen de una planta de tipo **{plant_type}**
utilizando un modelo de visión por computadora.

Resultado del análisis:
- Posible condición detectada: **{disease}**
{confidence_text}{location_text}{weather_block}
Explica de forma educativa y clara:
- Qué significa esta condición para la planta
- Posibles causas comunes (considerando el clima actual si es relevante)
- Recomendaciones generales de cuidado y prevención adaptadas al contexto
- Señales de alerta importantes (banderas rojas)
- En qué casos se recomienda buscar ayuda agrícola especializada

Usa un lenguaje sencillo y comprensible para usuarios no expertos.
"""
    return prompt.strip()
