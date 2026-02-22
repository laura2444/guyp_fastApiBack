"""
Fixtures compartidas para tests.
Incluye app FastAPI, cliente HTTP async con lifespan (MongoDB conectado)
e imagen de prueba para el análisis sin IA.
"""
import io
import uuid
from PIL import Image
import pytest
import pytest_asyncio
import httpx
from httpx import ASGITransport
from bson import ObjectId

from asgi_lifespan import LifespanManager

# Importar app después de posibles monkeypatch de env (si se usa)
from main import app


# ---------------------------------------------------------------------------
# Imagen de prueba (RGB 224x224, formato que acepta el modelo)
# ---------------------------------------------------------------------------

def _make_test_image_bytes(width: int = 224, height: int = 224) -> bytes:
    """Genera una imagen RGB en memoria para usar en multipart/form-data."""
    img = Image.new("RGB", (width, height), color=(120, 80, 200))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)
    return buf.read()


@pytest.fixture
def test_image_bytes() -> bytes:
    """Imagen JPEG válida para POST /analysis/{plant_type}."""
    return _make_test_image_bytes()


@pytest.fixture
def valid_user_id() -> str:
    """ObjectId válido para usar como user_id en requests."""
    return str(ObjectId())


# ---------------------------------------------------------------------------
# Cliente HTTP async con lifespan (conexión a MongoDB)
# ---------------------------------------------------------------------------

@pytest_asyncio.fixture
async def client():
    """
    Cliente HTTP asíncrono contra la app FastAPI con lifespan ejecutado.
    Necesario para que connect_to_mongodb() se ejecute y los tests de análisis funcionen.
    """
    async with LifespanManager(app):
        async with httpx.AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
            timeout=60.0,
        ) as ac:
            yield ac


# ---------------------------------------------------------------------------
# Helpers para tests de análisis (multipart)
# ---------------------------------------------------------------------------

def build_analysis_form(
    user_id: str,
    lat: float = -12.0,
    lng: float = -77.0,
    image_bytes: bytes | None = None,
    filename: str = "test_plant.jpg",
):
    """
    Construye el body multipart para POST /analysis/{plant_type}.
    Retorno: dict para files= y data= de httpx (equivalente a Form + File).
    """
    if image_bytes is None:
        image_bytes = _make_test_image_bytes()
    return {
        "user_id": (None, user_id),
        "lat": (None, str(lat)),
        "lng": (None, str(lng)),
        "image": (filename, image_bytes, "image/jpeg"),
    }
