# Tests – guyp_fastApiBack

## Estructura

- **`conftest.py`**: Fixtures compartidas (cliente HTTP async con lifespan, imagen de prueba, `user_id` válido).
- **`test_analysis_concurrency.py`**: Pruebas de **concurrencia** del análisis **sin IA** (POST `/analysis/{plant_type}`: imagen + modelo + BD/GridFS).
- **`unit/test_prompt_service.py`**: Tests unitarios del servicio de prompts.
- **`unit/test_weather_service.py`**: Tests unitarios del servicio de clima (validación de coordenadas y `get_weather` mockeado).

## Requisitos

- Python con dependencias instaladas (`pip install -r requirements.txt`).
- **Tests unitarios**: no requieren servicios externos.
- **Tests de concurrencia**: requieren **MongoDB** en marcha y variable de entorno **`URI`** definida (misma que en desarrollo).

## Ejecución

Desde la raíz del proyecto:

```bash
# Todos los tests
pytest

# Solo tests unitarios (sin MongoDB)
pytest tests/unit/ -v

# Solo tests de concurrencia
pytest tests/test_analysis_concurrency.py -v

# Con cobertura (opcional)
pip install pytest-cov
pytest tests/ --cov=app --cov-report=term-missing
```

## Pruebas de concurrencia

Validan que múltiples solicitudes simultáneas al análisis **sin IA**:

- Terminan todas con éxito (200).
- Cada una recibe un `analysis_id` distinto.
- No hay cruce de datos: cada análisis queda asociado al `user_id` de su request.

Se lanzan **10** requests en paralelo por defecto; puedes cambiar `CONCURRENT_REQUESTS` en `test_analysis_concurrency.py`.
