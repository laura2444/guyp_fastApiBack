from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorGridFSBucket
from pymongo.errors import ConnectionFailure
from typing import Optional, Any
import os

class Database:
    client: Optional[AsyncIOMotorClient] = None
    database: Optional[Any] = None
    fs: Optional[AsyncIOMotorGridFSBucket] = None

db = Database()

async def connect_to_mongodb():
    try:
        uri = os.getenv("URI")
        if not uri:
            raise RuntimeError("La variable de entorno URI no está definida.")

        db.client = AsyncIOMotorClient(uri)

        # Test de conexión
        await db.client.admin.command("ping")

        db.database = db.client["guyp"]
        db.fs = AsyncIOMotorGridFSBucket(db.database)

        print("Conexión realizada a MongoDB")

    except ConnectionFailure as e:
        print("Error de conexión a MongoDB:", e)
        raise
    except Exception as e:
        print("Error al inicializar MongoDB:", e)
        raise
    
async def close_mongodb():
    if db.client:
        db.client.close()
        print("Conexión a MongoDB cerrada")

def get_database():
    if db.database is None:
        raise RuntimeError("La base de datos no está inicializada. Debes ejecutar connect_to_mongodb() primero.")
    return db.database


def get_gridfs() -> AsyncIOMotorGridFSBucket:
    if db.fs is None:
        raise RuntimeError("GridFS no está inicializado. connect_to_mongodb() no fue ejecutado.")
    return db.fs
