from app.services.plant_analysis_service import save_analysis_record
from app.services.prompt_service import build_plant_prompt
from app.services.gemini_client import GeminiClient
from app.database.mongodb import get_database

from app.database.mongodb import get_database
 
def get_gemini_client() -> GeminiClient:
    return GeminiClient()

from bson import ObjectId
from typing import Dict

async def create_analysis_with_ai(
    user_id: str,
    prediction: str,
    location: dict,
    image_id: str
) -> Dict:
    
    gemini = get_gemini_client()  # 👈 se crea cuando YA existe el env

    analysis_id_str: str = await save_analysis_record(
        user_id=user_id,
        prediction=prediction,
        location=location,
        image_id=image_id
    )
    analysis_id: ObjectId = ObjectId(analysis_id_str)

    prompt = build_plant_prompt(prediction, location)
    ai_response = gemini.generate(prompt)
    ai_summary = gemini.generate_summary(ai_response)

    db = get_database()
    await db["plant_analysis"].update_one(
        {"_id": analysis_id},
        {
            "$set": {
                "ai_response": ai_response,
                "ai_summary": ai_summary
            }
        }
    )

    return {
        "analysis_id": str(analysis_id),
        "ai_response": ai_response
    }

    """
    Debido a la naturaleza dinámica de MongoDB, el identificador _id se gestionó de forma explícita como ObjectId, evitando su acoplamiento directo con los modelos de dominio y garantizando compatibilidad con herramientas de análisis estático como Pylance.
    """