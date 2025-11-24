from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from bson import ObjectId

from app.services.plant_analysis_service import (
    save_analysis_record,
    get_analysis_by_id,
    get_analyses_by_user,
    get_all_analyses,
    delete_analysis
)
from app.database.mongodb import get_gridfs

router = APIRouter()

#Funciona
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


    # Guardar análisis
    location = {"lat": lat, "lng": lng}
    record_id = await save_analysis_record(user_id, prediction, location, str(image_id))

    return {"message": "Análisis guardado", "id": record_id}

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
