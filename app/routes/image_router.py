from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from bson import ObjectId
from io import BytesIO
from app.database.mongodb import get_gridfs

router = APIRouter()

@router.get("/images/{image_id}")
async def get_image(image_id: str):
    fs = get_gridfs()

    try:
        grid_out = await fs.open_download_stream(ObjectId(image_id))
        content = await grid_out.read()
        return StreamingResponse(BytesIO(content), media_type="image/jpeg")
    except Exception:
        raise HTTPException(status_code=404, detail="Imagen no encontrada")
