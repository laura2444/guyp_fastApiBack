from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional


class UserRegisterSchema(BaseModel):
    name: str = Field(..., min_length=2, max_length=40)
    email: EmailStr
    password: str= Field(..., min_length=8)

    @field_validator('name')
    def validate_name(cls, v):
        if not v.strip(): # strip elimina espacios al inicio y al final, si no hay nada se devuelve false, y not false = true, se cumple if
            raise ValueError('Ingrese un nombre por favor')
        return v.strip().title()  # Devuelve el nombre con la primera letra en mayúscula y el resto en minúscula
    
    @field_validator('password')
    def validate_password(cls, v):
        if len(v)< 8:
            raise ValueError('La contraseña debe tener al menos 8 caracteres')
        return v


class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)


# Es para las respuestas que se envían al cliente, no enviar contraseña no es seguro
class UserResponseSchema(BaseModel):
    id: str
    name: str
    email: EmailStr
    token: Optional[str] = None