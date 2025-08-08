from app.models.plant import PlantAnalysis
from app.database.mongodb import get_database, get_gridfs
from bson import ObjectId


async def save_analysis_record(user_id: str, prediction: str, location: dict, image_id: str):
    db = get_database()

    record = PlantAnalysis(
        user_id=ObjectId(user_id),
        prediction=prediction,
        location=location,
        image_url=ObjectId(image_id)  # aseguramos que se guarde como ObjectId real
    )

    result = await db["plant_analysis"].insert_one(
        record.model_dump(by_alias=True, exclude_none=True)
    )

    return str(result.inserted_id)

async def get_analysis_by_id(analysis_id: str):
    db = get_database()
    doc = await db["plant_analysis"].find_one({"_id": ObjectId(analysis_id)})

    if doc:
        doc["_id"] = str(doc["_id"])
        doc["user_id"] = str(doc["user_id"])
        doc["image_url"] = str(doc["image_url"])
        doc["created_at"] = str(doc["created_at"])
        return doc

    return None


async def get_analyses_by_user(user_id: str):
    db = get_database()
    cursor = db["plant_analysis"].find({"user_id": ObjectId(user_id)})
    results = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        doc["user_id"] = str(doc["user_id"])
        doc["image_url"] = str(doc["image_url"])
        doc["created_at"] = str(doc["created_at"])
        results.append(doc)
    return results


async def get_all_analyses():
    db = get_database()
    cursor = db["plant_analysis"].find({})
    results = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        doc["user_id"] = str(doc["user_id"])
        doc["image_url"] = str(doc["image_url"])
        doc["created_at"] = str(doc["created_at"])
        results.append(doc)
    return results

async def delete_analysis(analysis_id: str):
    db = get_database()
    fs = get_gridfs()

    
    doc = await db["plant_analysis"].find_one({"_id": ObjectId(analysis_id)})

    if not doc:
        return False  

    # Eliminar la imagen de GridFS (fs.files + fs.chunks)
    image_id = doc.get("image_url")
    if image_id:
        try:
            await fs.delete(ObjectId(image_id))
        except Exception as e:
            print(f"No se pudo eliminar imagen: {e}")  

   
    result = await db["plant_analysis"].delete_one({"_id": ObjectId(analysis_id)})
    return result.deleted_count > 0