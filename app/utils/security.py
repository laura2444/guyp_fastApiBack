import os
from jose import JWTError, jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext

# contexto de encriptación que usa el algoritmo bcrypt, hashea las contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Clave secreta para firmar los tokens JWT 
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "passwordKey")  # Usa la misma clave que en Node.js
ALGORITHM = "HS256" # Algoritmo de encriptación,es el más común en estos casos


def hash_password(password: str) -> str: #hashea la contraseña usando pwd_contexto que usa bycript
    return pwd_context.hash(password)

#verifica si la contraseña en texto plano coincide con la contraseña hasheada
def verify_password(escrita: str, guardada: str) -> bool:
    return pwd_context.verify(escrita, guardada) #toma la contraseña texto plano que escribe el usuario y la vuelve a hashear con el mismo algoritmo HS256 para compararla con la hasheada guardada en la base de datos, si conside es true el bool
 
#crea un token de acceso JWT con los datos proporcionados
def create_access_token(data: dict): #recine un diccionario de datos que se van a incluir en el token
    to_encode = data.copy() #copia los datos para no modificar el original
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM) # agrega la clave secreta y el algoritmo de encriptación al token
    return encoded_jwt
