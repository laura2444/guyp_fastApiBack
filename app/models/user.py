from pydantic import BaseModel, Field
from typing import Optional

class User(BaseModel):
    id: Optional[str] = Field(None, alias="_id") # field (puede recibir un none, y su alias o nombre en la bd es _id)
    name: str
    email:str
    password: str

