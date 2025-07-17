from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure
import os

class database:
    client = None
    database = None

db= database() #instancia global para acceder a la bd desde cualquier lugar del proyecto

async def connect_to_mongodb():
    try:
        uri = os.getenv("URI")
        db.client = AsyncIOMotorClient(uri)
        await db.client.admin.command("ping") # verifica si la conexión es se ha realizado , puede que se cree el client pero no se conecte a mongo
        db.database = db.client["guyp"]
        print("Conexión realizada a la base de datos MongoDB")

    except ConnectionFailure as e:
        print(f"Error de conexión a MongoDB: No se pudo conectar al servidor: {e}")
        raise
    except Exception as e:
        print(f"Error de conexión a MongoDB: {e}")
        raise

async def close_mongodb():
    db.client.close()
    print("Conexión a MongoDB cerrada")

def get_database():
    return db.database


