from pathlib import Path
import json
import re
from urllib.parse import quote

import requests

_CACHE_TRADUCCION: dict[tuple[str, str], str] = {}


def ya_esta_en_espanol(texto: str) -> bool:
    palabras_espanolas = {
        "el", "la", "los", "las", "de", "del", "en", "por", "para",
        "con", "sin", "una", "un", "unos", "unas", "que", "se",
        "más", "como", "sobre", "tras", "desde", "es", "está", "son",
    }
    palabras = set(re.findall(r"[^\W\d_]+", texto.lower(), flags=re.UNICODE))
    coincidencias = palabras & palabras_espanolas
    return bool(re.search(r"[áéíóúüñ¿¡]", texto, flags=re.UNICODE)) or len(coincidencias) >= 3


def traducir_texto(texto: str, url_servicio: str = "") -> str:
    """Traduce texto a español. Devuelve el original si el servicio falla."""
    texto = texto.strip()
    if not texto:
        return ""
    if ya_esta_en_espanol(texto):
        return texto

    if not url_servicio:
        url_servicio = "https://api.mymemory.translated.net/get"

    clave = (texto, url_servicio)
    if clave in _CACHE_TRADUCCION:
        return _CACHE_TRADUCCION[clave]

    try:
        if "mymemory.translated.net" in url_servicio:
            separador = "&" if "?" in url_servicio else "?"
            texto_consulta = texto[:480]
            url = f"{url_servicio}{separador}q={quote(texto_consulta, safe='')}&langpair=en|es"
        else:
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

        if traducido.lower().startswith(("query length limit", "quota finished", "maximum query", "please specify")):
            return texto

        resultado = traducido.strip() or texto
        _CACHE_TRADUCCION[clave] = resultado
        return resultado
    except (requests.RequestException, json.JSONDecodeError, TypeError, KeyError, IndexError):
        return texto
