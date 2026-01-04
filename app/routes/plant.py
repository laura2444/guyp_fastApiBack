from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from bson import ObjectId
from app.services.analysis_orchestrator import create_analysis_with_ai


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

@router.post("/analysis/")
async def upload_analysis(
    user_id: str = Form(...),
    prediction: str = Form(...),
    lat: float = Form(...),
    lng: float = Form(...),
    image: UploadFile = File(...)
):
    fs = get_gridfs()

    image_data = await image.read()
    filename = image.filename or "uploaded_file"
    image_id = await fs.upload_from_stream(filename, image_data)

    location = {"lat": lat, "lng": lng}

    # ✅ AQUÍ ESTÁ LA DIFERENCIA
    record_id = await save_analysis_record(
        user_id, prediction, location, str(image_id)
    )

    return {
        "message": "Análisis guardado",
        "id": record_id
    }

#Funciona
@router.get("/analysis/{analysis_id}")
async def get_analysis(analysis_id: str):
    if not ObjectId.is_valid(analysis_id):
        raise HTTPException(status_code=400, detail="ID inválido")

    analysis = await get_analysis_by_id(analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Análisis no encontrado")

    return analysis  

#Funciona
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

@router.post("/analysis/with-ai")
async def upload_analysis_with_ai(
    user_id: str = Form(...),
    prediction: str = Form(...),
    lat: float = Form(...),
    lng: float = Form(...),
    image: UploadFile = File(...)
):

    # 1. Guardar imagen en GridFS
    fs = get_gridfs()
    image_data = await image.read()
    filename = image.filename or "uploaded_file"
    image_id = await fs.upload_from_stream(filename, image_data)

    # 2. Construir ubicación
    location = {
        "lat": lat,
        "lng": lng
    }

    # 3. Llamar al orquestador
    result = await create_analysis_with_ai(
        user_id=user_id,
        prediction=prediction,
        location=location,
        image_id=str(image_id)
    )

    return {
        "message": "Análisis generado con IA",
        **result
    }

###Endpoint: obtener respuesta completa de la IA
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

###Endpoint: obtener solo el resumen (historial / listas)
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

###Endpoint opcional (muy útil): estado de IA
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

