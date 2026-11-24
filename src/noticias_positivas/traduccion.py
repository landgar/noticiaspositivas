from pathlib import Path
import json
import re
from urllib.parse import quote

import requests

_CACHE_TRADUCCION: dict[tuple[str, str], str] = {}


def traducir_texto(texto: str, url_servicio: str = "") -> str:
    """Devuelve exactamente el texto recibido, sin consultar servicios externos."""
    return texto
