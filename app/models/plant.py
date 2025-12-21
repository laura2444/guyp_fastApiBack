from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from bson import ObjectId
from pydantic_core import core_schema
from pydantic import GetCoreSchemaHandler


class PyObjectId(ObjectId):
    """Tipo personalizado compatible con Pydantic v2"""

    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type, _handler: GetCoreSchemaHandler) -> core_schema.CoreSchema:
        return core_schema.no_info_plain_validator_function(cls.validate)

    @classmethod
    def validate(cls, v: Any) -> ObjectId:
        if isinstance(v, ObjectId):
            return v
        if isinstance(v, str) and ObjectId.is_valid(v):
            return ObjectId(v)
        raise ValueError("Invalid ObjectId")


class PlantAnalysis(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    user_id: PyObjectId
    prediction: str
    location: Dict[str, float]
    image_url: PyObjectId  
    created_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {
        "populate_by_name": True,   # 🔴 ESTA LÍNEA ES CLAVE
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str}
    }
