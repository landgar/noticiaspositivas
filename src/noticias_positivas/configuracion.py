import os
from pathlib import Path

import yaml


def cargar(ruta: str | Path = "config/configuracion.yml") -> dict:
    ruta = Path(ruta)
    with ruta.open("r", encoding="utf-8") as archivo:
        configuracion = yaml.safe_load(archivo)

    configuracion["ruta_repositorio"] = os.getenv(
        "RUTA_REPOSITORIO",
        configuracion.get("ruta_repositorio", "."),
    )
    configuracion["publicacion"] = {"subir_automaticamente": False}
    return configuracion
