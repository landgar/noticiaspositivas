from pathlib import Path
from datetime import datetime
import html

from jinja2 import Environment, FileSystemLoader, select_autoescape

from .modelos import Noticia


MESES = (
    "enero",
    "febrero",
    "marzo",
    "abril",
    "mayo",
    "junio",
    "julio",
    "agosto",
    "septiembre",
    "octubre",
    "noviembre",
    "diciembre",
)


def crear_noticias_html(
    titulo: str,
    noticias: list[Noticia],
    fecha: datetime,
    ruta_repositorio: str | Path = ".",
) -> Path:
    """Crea la página HTML diaria con el formato periodístico."""
    repositorio = Path(ruta_repositorio)
    directorio = repositorio / "salidas"
    directorio.mkdir(parents=True, exist_ok=True)

    ruta_plantilla = repositorio / "plantillas" / "entrada_hugo.html"
    if ruta_plantilla.exists():
        entorno = Environment(
            loader=FileSystemLoader(str(repositorio / "plantillas")),
            autoescape=select_autoescape(["html"]),
        )
        plantilla = entorno.get_template("entrada_hugo.html")
        fecha_texto = f"{fecha.day} de {MESES[fecha.month - 1]} de {fecha.year}"
        contenido = plantilla.render(
            titulo=titulo,
            fecha=fecha,
            fecha_texto=fecha_texto,
            noticias=noticias,
        )
    else:
        bloques: list[str] = [
            "<!doctype html>",
            '<html lang="es"><head><meta charset="utf-8">',
            f"<title>{html.escape(titulo)}</title></head><body>",
            f"<h1>{html.escape(titulo)}</h1>",
        ]
        for indice, noticia in enumerate(noticias, start=1):
            bloques.extend([
                f"<h2>{indice}. {html.escape(noticia.titulo)}</h2>",
                f'<p>{html.escape(noticia.resumen)}</p>' if noticia.resumen else "",
                f"<p><strong>Fuente: {html.escape(noticia.fuente)}</strong> · "
                f'<a href="{html.escape(noticia.enlace, quote=True)}">Leer fuente original</a></p>',
                f'<img src="{html.escape(noticia.imagen, quote=True)}" alt="">' if noticia.imagen else "",
            ])
        bloques.append("</body></html>")
        contenido = "".join(bloques)

    ruta = directorio / f"{fecha.strftime('%Y-%m-%d')}-noticias-positivas.html"
    ruta.write_text(contenido, encoding="utf-8")
    return ruta


def crear_noticias_txt(
    titulo: str,
    noticias: list[Noticia],
    fecha: datetime,
    ruta_repositorio: str | Path = ".",
) -> Path:
    """Crea un fichero de texto diario con las noticias seleccionadas."""
    repositorio = Path(ruta_repositorio)
    directorio = repositorio / "salidas"
    directorio.mkdir(parents=True, exist_ok=True)

    fecha_archivo = fecha.strftime("%Y-%m-%d")
    ruta = directorio / f"{fecha_archivo}-noticias-positivas.txt"

    contenido = [
        titulo,
        f"Fecha: {fecha.strftime('%d/%m/%Y %H:%M')}",
        f"Cantidad: {len(noticias)}",
        "",
    ]

    for indice, noticia in enumerate(noticias, start=1):
        contenido.append(f"{indice}. {noticia.titulo}")
        if noticia.resumen:
            contenido.append(noticia.resumen)
        contenido.append(f"Fuente: {noticia.fuente}")
        contenido.append(f"Enlace: {noticia.enlace}")
        contenido.append(f"Puntuación: {noticia.puntuacion:.1f}")
        contenido.append("")

    ruta.write_text("\n".join(contenido).rstrip() + "\n", encoding="utf-8")
    return ruta
