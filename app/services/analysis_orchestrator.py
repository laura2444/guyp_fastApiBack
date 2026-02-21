from bson import ObjectId
from typing import Dict, Optional, Any, TypedDict
from app.services.plant_analysis_service import save_analysis_record
from app.services.prompt_service import build_plant_prompt
from app.services.gemini_client import GeminiClient
from app.database.mongodb import get_database
from app.services.weather_service import get_weather
from app.services.plant_model_service import predict

from PIL import Image
from io import BytesIO


class AIAnalysisResult(TypedDict):
    analysis_id: str
    plant_type: str
    prediction: str
    confidence: float
    ai_generated: bool
    ai_response: Optional[Dict[str, Any]]
    weather: Optional[Dict[str, Any]]


def get_gemini_client() -> GeminiClient:
    return GeminiClient()


async def create_analysis_with_ai(
    user_id: str,
    plant_type: str,
    location: dict,
    image_id: str,
    image_bytes: bytes
) -> AIAnalysisResult:

    # =============================
    # 1️⃣ Predicción del modelo
    # =============================
    image_pil = Image.open(BytesIO(image_bytes)).convert("RGB")

    prediction_result = predict(image_pil, plant_type)

    disease_name = prediction_result["prediction"]
    confidence = float(prediction_result["confidence"])

    # =============================
    # 2️⃣ Guardar análisis base
    # =============================
    analysis_id_str = await save_analysis_record(
        user_id=user_id,
        plant_type=plant_type,
        prediction=disease_name,
        confidence=confidence,
        location=location,
        image_id=image_id
    )

    analysis_id = ObjectId(analysis_id_str)

    # =============================
    # 3️⃣ Obtener clima (si hay GPS válido)
    # =============================
    weather = None
    try:
        lat = float(location.get("lat") or location.get("latitude", 0))
        lon = float(location.get("lng") or location.get("longitude", 0))
        weather = await get_weather(lat, lon)
    except (TypeError, ValueError):
        weather = None

    # =============================
    # 4️⃣ Construir prompt IA (con clima y ubicación para mejor respuesta)
    # =============================
    prompt = build_plant_prompt(
        prediction={
            "plant_type": plant_type,
            "disease": disease_name,
            "confidence": confidence
        },
        location=location,
        weather=weather
    )

    gemini = get_gemini_client()

    # =============================
    # 5️⃣ Generar contenido IA
    # =============================
    try:
        ai_response = gemini.generate(prompt)
        ai_summary = gemini.generate_summary(ai_response)
        ai_generated = True

    except Exception as e:
        print(f"[AI ERROR] {e}")
        ai_response = None
        ai_summary = None
        ai_generated = False

    # =============================
    # 6️⃣ Persistir IA + clima
    # =============================
    db = get_database()

    await db["plant_analysis"].update_one(
        {"_id": analysis_id},
        {
            "$set": {
                "ai_response": ai_response,
                "ai_summary": ai_summary,
                "ai_generated": ai_generated,
                "weather": weather
            }
        }
    )

    # =============================
    # 7️⃣ Respuesta final
    # =============================
    return {
        "analysis_id": analysis_id_str,
        "plant_type": plant_type,
        "prediction": disease_name,
        "confidence": confidence,
        "ai_generated": ai_generated,
        "ai_response": ai_response,
        "weather": weather
    }
