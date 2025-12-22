import json
from typing import Dict, Iterator, Optional
import google.genai as genai
from google.genai import types

import os

# Esquema para el frontend
_response_schema_frontend = {
    "type": "object",
    "properties": {
        "mensaje": {"type": "string"},
        "autocuidado": {"type": "array", "items": {"type": "string"}},
        "banderas_rojas": {"type": "array", "items": {"type": "string"}},
        "cuando_buscar_atencion": {"type": "string"},
        "descargo": {"type": "string"}
    },
    "required": ["mensaje", "descargo"]
}

# Esquema para la BD
_response_schema_db = {
    "type": "object",
    "properties": {
        "tema": {"type": "string"},
        "resumen": {"type": "string"},
        "descargo": {"type": "string"}
    },
    "required": ["tema", "resumen", "descargo"]
}

# Instrucciones para PLANTAS (frontend)
_SYSTEM_INSTRUCTIONS_FRONTEND = (
    "Eres un asistente especializado en salud de plantas. "
    "No realizas diagnóstico profesional, pero explicas de forma sencilla "
    "posibles causas, recomendaciones de cuidado y señales de alerta. "
    "Responde SIEMPRE en español claro y estructurado. "
    "Devuelve un JSON con: mensaje, autocuidado, banderas_rojas, "
    "cuando_buscar_atencion y descargo. "
    "Siempre agrega: 'Información educativa. No reemplaza asesoría agrícola profesional.'"
)

# Instrucciones para PLANTAS (resumen)
_SYSTEM_INSTRUCTIONS_DB = (
    "Eres un asistente que genera resúmenes sobre salud de plantas. "
    "Genera un JSON con: "
    "'tema' (máximo 3 palabras), "
    "'resumen' (1-2 párrafos), "
    "'descargo'. "
    "Siempre incluye: 'Información educativa. No reemplaza asesoría agrícola profesional.'"
)


class GeminiClient:
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.client = genai.Client(api_key=api_key or os.getenv("GEMINI_API_KEY"))
        self.model = model or "gemini-2.5-flash"

        # Config frontend
        self.config_frontend = types.GenerateContentConfig(
            system_instruction=_SYSTEM_INSTRUCTIONS_FRONTEND,
            temperature=0.3,
            response_mime_type="application/json",
            response_schema=_response_schema_frontend,
            safety_settings=[
                types.SafetySetting(
                    category=types.HarmCategory.DANGEROUS_CONTENT,
                    threshold=types.HarmBlockThreshold.MEDIUM_AND_ABOVE
                ),
                types.SafetySetting(
                    category=types.HarmCategory.HATE_SPEECH,
                    threshold=types.HarmBlockThreshold.ONLY_HIGH
                ),
                types.SafetySetting(
                    category=types.HarmCategory.HARASSMENT,
                    threshold=types.HarmBlockThreshold.ONLY_HIGH
                ),
                types.SafetySetting(
                    category=types.HarmCategory.SEXUALLY_EXPLICIT,
                    threshold=types.HarmBlockThreshold.ONLY_HIGH
                ),
            ],
        )

        # Config BD
        self.config_db = types.GenerateContentConfig(
            system_instruction=_SYSTEM_INSTRUCTIONS_DB,
            temperature=0.2,
            response_mime_type="application/json",
            response_schema=_response_schema_db,
            safety_settings=self.config_frontend.safety_settings,
        )


    def generate(self, prompt: str) -> Dict:
        """
        Genera la respuesta completa para mostrar al usuario.
        """
        try:
            res = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=self.config_frontend
            )

            if not res.text:
                raise ValueError("Respuesta vacía desde Gemini")

            return json.loads(res.text)

        except Exception as e:
            print(f"Error generando respuesta: {e}")
            return {
                "mensaje": "No pude generar una respuesta en este momento. Por favor intenta nuevamente.",
                "descargo": "Información educativa. No reemplaza asesoría agrícola profesional."
            }


    def generate_summary(self, full_response: Dict) -> Dict:
        """
        Genera una versión resumida para guardar en la base de datos.
        """
        summary_prompt = f"""
        Resume esta información sobre la salud de una planta:

        MENSAJE: {full_response.get('mensaje', '')}
        AUTOCUIDADO: {', '.join(full_response.get('autocuidado', []))}
        BANDERAS ROJAS: {', '.join(full_response.get('banderas_rojas', []))}
        CUANDO BUSCAR ATENCIÓN: {full_response.get('cuando_buscar_atencion', '')}

        Genera un JSON con: tema, resumen, descargo.
        """

        try:
            res = self.client.models.generate_content(
                model=self.model,
                contents=summary_prompt,
                config=self.config_db
            )

            if res.text is not None:
                return json.loads(res.text)
            else:
                raise ValueError("Respuesta vacía desde Gemini")

        except Exception as e:
            print(f"Error generando resumen: {e}")
            return {
                "tema": "Salud vegetal",
                "resumen": full_response.get("mensaje", ""),
                "descargo": "Información educativa. No reemplaza asesoría agrícola profesional."
            }
