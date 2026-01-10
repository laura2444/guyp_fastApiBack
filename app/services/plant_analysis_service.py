from typing import Optional, Dict, List
from app.models.plant import PlantAnalysis, PyObjectId
from app.database.mongodb import get_database, get_gridfs
from bson import ObjectId
from datetime import datetime


async def save_analysis_record(user_id: str, prediction: str, location: dict, image_id: str):
    db = get_database()

    record = PlantAnalysis(
        user_id=PyObjectId(user_id),
        prediction=prediction,
        location=location,
        image_url=PyObjectId(image_id)
    )

    result = await db["plant_analysis"].insert_one(
        record.model_dump(by_alias=True, exclude_none=True)
    )
    return str(result.inserted_id)


async def get_analysis_by_id(analysis_id: str):
    db = get_database()
    doc = await db["plant_analysis"].find_one({"_id": ObjectId(analysis_id)})

    if doc:
        return _serialize(doc)
    return None


async def get_analyses_by_user(user_id: str):
    db = get_database()
    cursor = db["plant_analysis"].find({"user_id": ObjectId(user_id)})
    return [ _serialize(doc) async for doc in cursor ]


async def get_all_analyses():
    db = get_database()
    cursor = db["plant_analysis"].find({})
    return [ _serialize(doc) async for doc in cursor ]


async def get_analyses_by_prediction(prediction: str):
    db = get_database()
    cursor = db["plant_analysis"].find({"prediction": prediction})
    return [ _serialize(doc) async for doc in cursor ]


async def get_analyses_by_date_range(start: datetime, end: datetime):
    db = get_database()
    cursor = db["plant_analysis"].find({
        "created_at": {"$gte": start, "$lte": end}
    })
    return [ _serialize(doc) async for doc in cursor ]


async def update_prediction(analysis_id: str, new_prediction: str):
    db = get_database()
    result = await db["plant_analysis"].update_one(
        {"_id": ObjectId(analysis_id)},
        {"$set": {"prediction": new_prediction}}
    )
    return result.modified_count > 0


async def add_ai_response(analysis_id: str, ai_response: Dict):
    db = get_database()
    result = await db["plant_analysis"].update_one(
        {"_id": ObjectId(analysis_id)},
        {"$set": {"ai_response": ai_response}}
    )
    return result.modified_count > 0


async def add_ai_summary(analysis_id: str, ai_summary: Dict):
    db = get_database()
    result = await db["plant_analysis"].update_one(
        {"_id": ObjectId(analysis_id)},
        {"$set": {"ai_summary": ai_summary}}
    )
    return result.modified_count > 0


async def delete_analysis(analysis_id: str):
    db = get_database()
    fs = get_gridfs()

    doc = await db["plant_analysis"].find_one({"_id": ObjectId(analysis_id)})
    if not doc:
        return False

    image_id = doc.get("image_url")
    if image_id:
        try:
            await fs.delete(ObjectId(image_id))
        except Exception as e:
            print(f"No se pudo eliminar imagen: {e}")

    result = await db["plant_analysis"].delete_one({"_id": ObjectId(analysis_id)})
    return result.deleted_count > 0


async def get_ai_response_by_analysis_id(analysis_id: str) -> Optional[Dict]:
    db = get_database()
    return await db["plant_analysis"].find_one(
        {"_id": ObjectId(analysis_id)},
        {"_id": 0, "ai_response": 1}
    )


async def get_ai_summary_by_analysis_id(analysis_id: str) -> Optional[Dict]:
    db = get_database()
    return await db["plant_analysis"].find_one(
        {"_id": ObjectId(analysis_id)},
        {"_id": 0, "ai_summary": 1}
    )


def _serialize(doc: dict) -> dict:
    doc["_id"] = str(doc["_id"])
    doc["user_id"] = str(doc["user_id"])
    doc["image_url"] = str(doc["image_url"])
    if "created_at" in doc:
        doc["created_at"] = str(doc["created_at"])
    return doc
