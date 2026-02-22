"""
Pruebas de concurrencia del flujo de análisis SIN IA.

Objetivo: validar que múltiples solicitudes simultáneas a
POST /analysis/{plant_type} (imagen + modelo + guardado en BD/GridFS)
se ejecutan sin fallos, con respuestas correctas y sin cruce de datos
(aislamiento por request: cada uno su analysis_id, user_id, imagen).
"""
import asyncio
from typing import Set

import pytest
import pytest_asyncio
from bson import ObjectId
from httpx import AsyncClient

from tests.conftest import build_analysis_form, _make_test_image_bytes


# Número de requests en paralelo para pruebas de concurrencia
CONCURRENT_REQUESTS = 10
# Tipo de planta usado en los tests (debe existir en el modelo)
PLANT_TYPE = "tomato"


async def _post_one_analysis(
    client: AsyncClient,
    request_id: int,
    user_id: str,
    plant_type: str = PLANT_TYPE,
) -> tuple[int, dict]:
    """
    Envía una única solicitud POST /analysis/{plant_type}.
    Retorna (request_id, response_json) para poder asociar respuesta a cada tarea.
    """
    form = build_analysis_form(user_id=user_id, image_bytes=_make_test_image_bytes())
    url = f"/analysis/{plant_type}"
    response = await client.post(url, files=form)
    body = response.json() if response.content else {}
    return (request_id, body)


@pytest.mark.asyncio
async def test_concurrent_analysis_same_user(client: AsyncClient, valid_user_id: str):
    """
    Varias solicitudes en paralelo con el mismo user_id.
    Verifica: todas 200, analysis_id únicos, estructura correcta.
    """
    tasks = [
        _post_one_analysis(client, i, valid_user_id)
        for i in range(CONCURRENT_REQUESTS)
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    analysis_ids: Set[str] = set()
    for item in results:
        if isinstance(item, Exception):
            raise item
        req_id, data = item
        assert data.get("analysis_id") is not None, f"Request {req_id}: falta analysis_id"
        assert data.get("prediction") is not None, f"Request {req_id}: falta prediction"
        assert "confidence" in data, f"Request {req_id}: falta confidence"
        analysis_ids.add(data["analysis_id"])

    # Cada respuesta debe tener un analysis_id distinto
    assert len(analysis_ids) == CONCURRENT_REQUESTS, (
        f"Se esperaban {CONCURRENT_REQUESTS} analysis_id únicos, se obtuvieron {len(analysis_ids)}"
    )


@pytest.mark.asyncio
async def test_concurrent_analysis_different_users(client: AsyncClient):
    """
    Varias solicitudes en paralelo con user_id distinto cada una.
    Verifica: todas 200, analysis_id únicos y que en BD cada análisis
    quede asociado a su user_id (sin cruce).
    """
    # Un user_id por request
    user_ids = [str(ObjectId()) for _ in range(CONCURRENT_REQUESTS)]
    tasks = [
        _post_one_analysis(client, i, user_ids[i])
        for i in range(CONCURRENT_REQUESTS)
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    analysis_ids: Set[str] = set()
    for item in results:
        if isinstance(item, Exception):
            raise item
        req_id, data = item
        assert data.get("analysis_id"), f"Request {req_id}: sin analysis_id"
        analysis_ids.add(data["analysis_id"])

    assert len(analysis_ids) == CONCURRENT_REQUESTS

    # Comprobar en BD: cada analysis_id tiene el user_id correcto
    from app.database.mongodb import get_database
    db = get_database()
    for i, item in enumerate(results):
        _, data = item
        aid = data["analysis_id"]
        doc = await db["plant_analysis"].find_one({"_id": ObjectId(aid)})
        assert doc is not None, f"Análisis {aid} no encontrado en BD"
        assert str(doc["user_id"]) == user_ids[i], (
            f"Análisis {aid}: user_id en BD no coincide con el de la request {i}"
        )


@pytest.mark.asyncio
async def test_concurrent_analysis_all_plant_types(client: AsyncClient, valid_user_id: str):
    """
    Concurrencia repartida entre los tres tipos de planta (tomato, potato, pepper).
    Verifica que todos respondan 200 y con prediction/confidence.
    """
    plant_types = ["tomato", "potato", "pepper"]
    tasks = []
    for i in range(CONCURRENT_REQUESTS):
        plant = plant_types[i % len(plant_types)]
        form = build_analysis_form(valid_user_id, image_bytes=_make_test_image_bytes())
        tasks.append(client.post(f"/analysis/{plant}", files=form))

    responses = await asyncio.gather(*tasks, return_exceptions=True)
    for i, r in enumerate(responses):
        if isinstance(r, Exception):
            raise r
        assert r.status_code == 200, f"Request {i}: status {r.status_code}"
        data = r.json()
        assert "analysis_id" in data and "prediction" in data and "confidence" in data
