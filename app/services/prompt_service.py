def build_plant_prompt(prediction: str, location: dict) -> str:
    """
    Construye un prompt instructivo a partir de la predicción
    del modelo de deep learning y la información de ubicación.

    Esta función genera un contexto enriquecido para el modelo
    generativo (Gemini), combinando el resultado de clasificación
    con metadatos ambientales.

    Args:
        prediction (str): Estado de salud detectado en la planta
            (ej. "Septoria_leaf_spot").
        location (dict): Información de geolocalización enviada
            desde la aplicación móvil (lat, lng).

    Returns:
        str: Prompt instructivo para el modelo generativo.
    """

    disease = prediction

    lat = location.get("lat")
    lon = location.get("lng")

    location_text = ""
    if lat is not None and lon is not None:
        location_text = (
            f"La planta se encuentra ubicada aproximadamente en "
            f"las coordenadas ({lat}, {lon}). "
            f"Ten en cuenta condiciones climáticas y ambientales "
            f"comunes en esta región."
        )

    prompt = f"""
    Se ha analizado una imagen de una planta usando un modelo de visión por computadora.

    Resultado del modelo:
    - Posible condición detectada: {disease}

    {location_text}

    Explica de forma educativa:
    - Qué podría significar esta condición
    - Recomendaciones generales de cuidado
    - Señales de alerta (banderas rojas)
    - Cuándo buscar ayuda agrícola especializada

    Usa un lenguaje claro para usuarios no expertos.
    """

    return prompt.strip()
