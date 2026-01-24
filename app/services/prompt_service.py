from typing import Dict


def build_plant_prompt(prediction: Dict, location: dict) -> str:
    """
    Construye un prompt instructivo a partir de la predicción
    del modelo de deep learning y la información de ubicación.

    Args:
        prediction (dict): Resultado del modelo de clasificación.
            {
                "plant_type": "tomato",
                "disease": "Septoria leaf spot",
                "confidence": 0.92
            }
        location (dict): Información de geolocalización
            {
                "latitude": float,
                "longitude": float
            }

    Returns:
        str: Prompt instructivo para el modelo generativo.
    """

    plant_type = prediction.get("plant_type", "planta")
    disease = prediction.get("disease", "condición desconocida")
    confidence = prediction.get("confidence")

    lat = location.get("latitude")
    lon = location.get("longitude")

    # Texto de ubicación
    location_text = ""
    if lat is not None and lon is not None:
        location_text = (
            f"La planta se encuentra aproximadamente en las coordenadas "
            f"({lat}, {lon}). Ten en cuenta las condiciones climáticas y "
            f"ambientales comunes de esta región."
        )

    confidence_text = ""
    if confidence is not None:
        confidence_text = (
            f"El modelo tiene un nivel de confianza aproximado del "
            f"{confidence * 100:.1f}% en esta predicción."
        )

    prompt = f"""
    Se ha analizado una imagen de una planta de tipo **{plant_type}**
    utilizando un modelo de visión por computadora.

    Resultado del análisis:
    - Posible condición detectada: **{disease}**
    {confidence_text}

    {location_text}

    Explica de forma educativa y clara:
    - Qué significa esta condición para la planta
    - Posibles causas comunes
    - Recomendaciones generales de cuidado y prevención
    - Señales de alerta importantes (banderas rojas)
    - En qué casos se recomienda buscar ayuda agrícola especializada

    Usa un lenguaje sencillo y comprensible para usuarios no expertos.
    """

    return prompt.strip()
