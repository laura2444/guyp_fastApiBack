from bson import ObjectId
from typing import Dict, TypedDict,Dict, Optional, Any

from app.services.plant_analysis_service import save_analysis_record
from app.services.prompt_service import build_plant_prompt
from app.services.gemini_client import GeminiClient
from app.database.mongodb import get_database


class AIAnalysisResult(TypedDict):
    analysis_id: str
    ai_response: Optional[Dict[str, Any]]


def get_gemini_client() -> GeminiClient:
    return GeminiClient()


async def create_analysis_with_ai(
    user_id: str,
    prediction: str,
    location: dict,
    image_id: str
) -> AIAnalysisResult:
    """
    Orquesta la creación de un análisis de planta y la generación
    de contenido explicativo usando IA generativa.
    """

    gemini = get_gemini_client()

    analysis_id_str = await save_analysis_record(
        user_id=user_id,
        prediction=prediction,
        location=location,
        image_id=image_id
    )

    analysis_id = ObjectId(analysis_id_str)

    prompt = build_plant_prompt(prediction, location)

    try:
        ai_response = gemini.generate(prompt)
        ai_summary = gemini.generate_summary(ai_response)
        ai_generated = True
    except Exception:
        ai_response = None
        ai_summary = None
        ai_generated = False

    db = get_database()
    await db["plant_analysis"].update_one(
        {"_id": analysis_id},
        {
            "$set": {
                "ai_response": ai_response,
                "ai_summary": ai_summary,
                "ai_generated": ai_generated
            }
        }
    )

    return {
        "analysis_id": str(analysis_id),
        "ai_response": ai_response
    }
