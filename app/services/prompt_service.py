def build_plant_prompt(prediction: str, location: dict) -> str:
    """
    Construye el prompt inscructivo apartir de la respuesta de los modelos deep leearning
    e ubicación.

    Esta función entrega la información generada por el modelo de
    gemini junto con los metadatos asociados(prediction, location).

    Args:
        prediction (str): Identificador del estado de salud de la planta(Sephtoria_plant).
        location (dict): Información de geolocalización enviada
            desde la aplicación móvil (latitud y longitud).

    Returns:
        PlantAnalysis: Objeto del análisis de la plata.
    """
    disease = prediction
 
    lat = location.get("latitude")
    lon = location.get("longitude")

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