from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from bson import ObjectId
from PIL import Image
from io import BytesIO
from app.services.analysis_orchestrator import create_analysis_with_ai
import app.ml.model_loader
from app.services.plant_model_service import predict

from app.services.plant_analysis_service import (
    save_analysis_record,
    get_analysis_by_id,
    get_analyses_by_user,
    get_all_analyses,
    delete_analysis,
    get_ai_response_by_analysis_id,
    get_ai_summary_by_analysis_id
)
from app.database.mongodb import get_gridfs, get_database

router = APIRouter()

@router.post("/analysis/{plant_type}")
async def upload_analysis(
    plant_type: str,
    user_id: str = Form(...),
    lat: float = Form(...),
    lng: float = Form(...),
    image: UploadFile = File(...)
):
    if plant_type not in {"tomato", "potato", "pepper"}:
        raise HTTPException(status_code=400, detail="Tipo de planta no soportado")

    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="ID de usuario inválido")

    # 1️⃣ Guardar imagen
    fs = get_gridfs()
    image_bytes = await image.read()
    image_id = await fs.upload_from_stream(
        image.filename or "uploaded_image",
        image_bytes
    )

    # 2️⃣ Inferencia - CORREGIDO: usar BytesIO para PIL
    image_pil = Image.open(BytesIO(image_bytes)).convert("RGB")
    result = predict(image_pil, plant_type)

    # 3️⃣ Guardar análisis - CORREGIDO: usar class_id
    analysis_id = await save_analysis_record(
        user_id=user_id,
        plant_type=plant_type,
        prediction=result["prediction"],  # ← Esto es STRING ("Bacterial_spot")
        confidence=result["confidence"],
        location={"lat": lat, "lng": lng},
        image_id=str(image_id)
    )

    return {
    "analysis_id": analysis_id,
    "class_id": result["class_id"],
    "prediction": result["prediction"],  # ← Agregar nombre
    "confidence": result["confidence"]
}

@router.post("/analysis/{plant_type}/with-ai")
async def upload_analysis_with_ai(
    plant_type: str,
    user_id: str = Form(...),
    lat: float = Form(...),
    lng: float = Form(...),
    image: UploadFile = File(...)
):
    if plant_type not in {"tomato", "potato", "pepper"}:
        raise HTTPException(status_code=400, detail="Tipo de planta no soportado")
    
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="ID de usuario inválido")

    fs = get_gridfs()
    image_bytes = await image.read()
    image_id = await fs.upload_from_stream(
        image.filename or "uploaded_image",
        image_bytes
    )

    location = {"lat": lat, "lng": lng}

    # Get prediction first
    image_pil = Image.open(BytesIO(image_bytes)).convert("RGB")
    prediction_result = predict(image_pil, plant_type)

    result = await create_analysis_with_ai(
        user_id=user_id,
        plant_type=plant_type,
        location=location,
        image_id=str(image_id),
        image_bytes=image_bytes
    )

    return {
        "message": "Análisis generado con IA",
        **result
    }

@router.get("/analysis/{analysis_id}")
async def get_analysis(analysis_id: str):
    if not ObjectId.is_valid(analysis_id):
        raise HTTPException(status_code=400, detail="ID inválido")

    analysis = await get_analysis_by_id(analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Análisis no encontrado")

    return analysis  

@router.get("/user/{user_id}/analysis")
async def get_user_analysis_history(user_id: str):
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="ID de usuario inválido")

    analyses = await get_analyses_by_user(user_id)

    if not analyses:
        return {"message": "El usuario no tiene análisis guardados."}

    return analyses

@router.get("/analysis/")
async def get_all_analysis():
    return await get_all_analyses()

@router.delete("/analysis/{analysis_id}")
async def remove_analysis(analysis_id: str):
    if not ObjectId.is_valid(analysis_id):
        raise HTTPException(status_code=400, detail="ID inválido")

    success = await delete_analysis(analysis_id)
    if not success:
        raise HTTPException(status_code=404, detail="Análisis no encontrado")

    return {"message": "Análisis e imagen eliminados correctamente"}

@router.get("/analysis/{analysis_id}/ai")
async def get_analysis_ai_response(analysis_id: str):
    if not ObjectId.is_valid(analysis_id):
        raise HTTPException(status_code=400, detail="ID inválido")

    result = await get_ai_response_by_analysis_id(analysis_id)

    if not result:
        raise HTTPException(status_code=404, detail="Análisis no encontrado")

    if not result.get("ai_generated"):
        return {
            "message": "Este análisis no tiene respuesta de IA generada",
            "ai_response": None
        }

    return result

@router.get("/analysis/{analysis_id}/ai/summary")
async def get_analysis_ai_summary(analysis_id: str):
    if not ObjectId.is_valid(analysis_id):
        raise HTTPException(status_code=400, detail="ID inválido")

    result = await get_ai_summary_by_analysis_id(analysis_id)

    if not result or not result.get("ai_summary"):
        raise HTTPException(
            status_code=404,
            detail="Resumen de IA no disponible"
        )

    return result["ai_summary"]

@router.get("/analysis/{analysis_id}/ai/status")
async def get_analysis_ai_status(analysis_id: str):
    if not ObjectId.is_valid(analysis_id):
        raise HTTPException(status_code=400, detail="ID inválido")

    db = get_database()
    analysis = await db["plant_analysis"].find_one(
        {"_id": ObjectId(analysis_id)},
        {"_id": 0, "ai_generated": 1}
    )

    if not analysis:
        raise HTTPException(status_code=404, detail="Análisis no encontrado")

    return {
        "ai_generated": analysis.get("ai_generated", False)
    }