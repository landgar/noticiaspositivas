from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

from jinja2 import Environment, FileSystemLoader, select_autoescape

from .modelos import Noticia

MESES = (
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
)


def generar_titulo(fecha: datetime, cantidad: int) -> str:
    fecha_es = f"{fecha.day} de {MESES[fecha.month - 1]} de {fecha.year}"
    return f"Las {cantidad} noticias más positivas del {fecha_es}"


def redactar(
    noticias: list[Noticia],
    zona: str = "Europe/Madrid",
    ruta_repositorio: str | Path = ".",
) -> tuple[str, str]:
    zona_horaria = ZoneInfo(zona)
    fecha = datetime.now(zona_horaria)
    titulo = generar_titulo(fecha, len(noticias))

    repositorio = Path(ruta_repositorio).resolve()
    entorno = Environment(
        loader=FileSystemLoader(str(repositorio / "plantillas")),
        autoescape=select_autoescape(["html"]),
    )
    plantilla = entorno.get_template("entrada_hugo.html")
    fecha_texto = f"{fecha.day} de {MESES[fecha.month - 1]} de {fecha.year}"
    html = plantilla.render(
        titulo=titulo,
        fecha=fecha,
        fecha_texto=fecha_texto,
        noticias=noticias,
    )

    salida = repositorio / "salidas"
    salida.mkdir(parents=True, exist_ok=True)
    fecha_archivo = fecha.strftime("%Y-%m-%d")
    ruta_html = salida / f"{fecha_archivo}-noticias-positivas.html"
    ruta_html.write_text(html, encoding="utf-8")
    return titulo, str(ruta_html)
