from typing import Optional, Dict, List
from datetime import datetime
from bson import ObjectId

from app.models.plant import PlantAnalysis, PyObjectId
from app.database.mongodb import get_database, get_gridfs


# =========================
# CREATE
# =========================

async def save_analysis_record(
    user_id: str,
    plant_type: str,
    prediction: str,
    confidence: float,
    location: Dict[str, float],
    image_id: str
) -> str:
    db = get_database()

    record = PlantAnalysis(
        user_id=PyObjectId(user_id),
        plant_type=plant_type,
        prediction=prediction,
        confidence=confidence,
        location=location,
        image_url=PyObjectId(image_id)
    )

    result = await db["plant_analysis"].insert_one(
        record.model_dump(by_alias=True, exclude_none=True)
    )

    return str(result.inserted_id)


# =========================
# READ
# =========================

async def get_analysis_by_id(analysis_id: str) -> Optional[Dict]:
    db = get_database()
    doc = await db["plant_analysis"].find_one({"_id": ObjectId(analysis_id)})
    return _serialize(doc) if doc else None


async def get_analyses_by_user(user_id: str) -> List[Dict]:
    db = get_database()
    cursor = db["plant_analysis"].find({"user_id": ObjectId(user_id)})
    return [_serialize(doc) async for doc in cursor]


async def get_all_analyses() -> List[Dict]:
    db = get_database()
    cursor = db["plant_analysis"].find({})
    return [_serialize(doc) async for doc in cursor]


async def get_analyses_by_plant_type(plant_type: str) -> List[Dict]:
    db = get_database()
    cursor = db["plant_analysis"].find({"plant_type": plant_type})
    return [_serialize(doc) async for doc in cursor]


async def get_analyses_by_prediction(prediction: str) -> List[Dict]:
    db = get_database()
    cursor = db["plant_analysis"].find({"prediction": prediction})
    return [_serialize(doc) async for doc in cursor]


async def get_analyses_by_date_range(
    start: datetime,
    end: datetime
) -> List[Dict]:
    db = get_database()
    cursor = db["plant_analysis"].find({
        "created_at": {"$gte": start, "$lte": end}
    })
    return [_serialize(doc) async for doc in cursor]


# =========================
# UPDATE
# =========================

async def update_prediction(
    analysis_id: str,
    prediction: str,
    confidence: float
) -> bool:
    db = get_database()
    result = await db["plant_analysis"].update_one(
        {"_id": ObjectId(analysis_id)},
        {"$set": {
            "prediction": prediction,
            "confidence": confidence
        }}
    )
    return result.modified_count > 0


async def add_ai_response(analysis_id: str, ai_response: Dict) -> bool:
    db = get_database()
    result = await db["plant_analysis"].update_one(
        {"_id": ObjectId(analysis_id)},
        {"$set": {"ai_response": ai_response}}
    )
    return result.modified_count > 0


async def add_ai_summary(analysis_id: str, ai_summary: Dict) -> bool:
    db = get_database()
    result = await db["plant_analysis"].update_one(
        {"_id": ObjectId(analysis_id)},
        {"$set": {"ai_summary": ai_summary}}
    )
    return result.modified_count > 0


# =========================
# DELETE
# =========================

async def delete_analysis(analysis_id: str) -> bool:
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


# =========================
# AI DATA (OPTIONAL)
# =========================

async def get_ai_response_by_analysis_id(
    analysis_id: str
) -> Optional[Dict]:
    db = get_database()
    return await db["plant_analysis"].find_one(
        {"_id": ObjectId(analysis_id)},
        {"_id": 0, "ai_response": 1}
    )


async def get_ai_summary_by_analysis_id(
    analysis_id: str
) -> Optional[Dict]:
    db = get_database()
    return await db["plant_analysis"].find_one(
        {"_id": ObjectId(analysis_id)},
        {"_id": 0, "ai_summary": 1}
    )


# =========================
# SERIALIZER
# =========================

def _serialize(doc: Dict) -> Dict:
    doc["_id"] = str(doc["_id"])
    doc["user_id"] = str(doc["user_id"])
    doc["image_url"] = str(doc["image_url"])
    doc["created_at"] = doc["created_at"].isoformat()
    return doc
