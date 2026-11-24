from pathlib import Path
import json
import re
from urllib.parse import quote

import requests

_CACHE_TRADUCCION: dict[tuple[str, str], str] = {}


def traducir_texto(texto: str, url_servicio: str = "") -> str:
    """Traduce texto a español. Devuelve el original si el servicio falla."""
    texto = texto.strip()
    if not texto:
        return ""

    if not url_servicio:
        url_servicio: str = "https://translate.googleapis.com/translate_a/single"

    clave = (texto, url_servicio)
    if clave in _CACHE_TRADUCCION:
        return _CACHE_TRADUCCION[clave]

    try:
        separador = "&" if "?" in url_servicio else "?"
        url = (
            f"{url_servicio}{separador}client=gtx&sl=auto&tl=es&dt=t"
            f"&q={quote(texto, safe='')}"
        )

        respuesta = requests.get(url, timeout=12)
        respuesta.raise_for_status()
        datos = respuesta.json()

        if "responseData" in datos:
            traducido = datos["responseData"].get("translatedText", "")
        else:
            segmentos = datos[0] if datos and isinstance(datos, list) else []
            traducido = "".join(segmento[0] for segmento in segmentos if segmento and segmento[0])

        if traducido.lower().startswith((
            "query length limit", "quota finished", "maximum query", "please specify",
            "please select two distinct languages",
        )):
            return texto

        resultado = traducido.strip() or texto
        _CACHE_TRADUCCION[clave] = resultado
        return resultado
    except (requests.RequestException, json.JSONDecodeError, TypeError, KeyError, IndexError):
        return texto
