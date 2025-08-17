from contextlib import asynccontextmanager
from fastapi import FastAPI
import os
from app.routes.auth import auth_router
from app.database.mongodb import connect_to_mongodb, close_mongodb
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from app.routes.plant import router as plant_router 
from app.routes.image_router import router as image

load_dotenv()

#evento, permite que se inicie la conexión a la base de datos al iniciar la aplicación
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Esto corre al iniciar
    await connect_to_mongodb()
    yield
    #Esto corre al cerrar
    await close_mongodb()

app = FastAPI(lifespan=lifespan)


app.add_middleware(CORSMiddleware, 
    allow_origins=["*"],  #permite que cualquier origen acceda a la API
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"]
)

#routes
app.include_router(auth_router, prefix="/auth", tags=["auth"]) 
app.include_router(plant_router, tags=["plant"])  
app.include_router(image, tags=["image"])           


@app.get("/")
async def root():
    return {"message": "Store API is running"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)