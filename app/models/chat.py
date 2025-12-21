from pydantic import BaseModel, Field
from typing import List, Optional
from models.plant import PyObjectId

# la estructura a la respuesta de la API, de Gemini
class ChatOut(BaseModel):
    plant_id: PyObjectId
    mensaje: str
    autocuidado: Optional[List[str]] = None
    banderas_rojas: Optional[List[str]] = None
    cuando_buscar_atencion: Optional[str] = None
    descargo: str = Field(default="Información educativa. No reemplaza una consulta profesional.")

    
    
