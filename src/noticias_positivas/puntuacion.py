import re
import unicodedata

from .modelos import Noticia

POSITIVOS = {
    "avance": 3.0, "avances": 3.0, "breakthrough": 3.0, "buenas noticias": 4.0,
    "celebra": 2.5, "conquista": 2.5, "crecimiento": 1.8, "curacion": 4.0,
    "descubrimiento": 2.5, "exito": 3.0, "gratuito": 2.0,
    "innovacion": 2.2, "logro": 3.0, "milagro": 1.5,
    "protege": 2.0, "recupera": 2.2, "recuperacion": 2.2,
    "reduce": 1.5, "refugio": 1.5, "reforma": 1.2, "rescate": 3.0,
    "restauracion": 2.0, "salva": 3.0, "solucion": 2.5,
    "triunfo": 3.0, "victoria": 3.0, "wins": 2.5,
    "hope": 2.5, "hopeful": 2.5, "saves": 3.0, "success": 3.0,
    "promising": 2.5, "sustainable": 2.0, "peace": 3.0,
    "agreement": 2.5, "record low": 2.0, "beat": 1.5, "open": 0.8,
}

NEGATIVOS = {
    "ataque": -5.0, "crisis": -4.0, "dead": -5.0, "died": -5.0,
    "dies": -5.0, "desastre": -5.0, "guerra": -5.0, "muertos": -5.0,
    "muertes": -5.0, "asesinato": -5.0, "killed": -5.0, "muerte": -5.0,
    "terror": -5.0, "violencia": -5.0, "warning": -4.0, "alert": -4.0,
    "sunk": -4.0, "missing": -4.0, "catastrofe": -5.0, "genocide": -5.0,
    "flood": -4.0, "war": -5.0, "attack": -5.0, "strikes": -4.0,
    "bomb": -5.0, "shooting": -5.0, "victims": -4.0,
}


def normalizar(texto: str) -> str:
    texto = unicodedata.normalize("NFKD", texto.lower())
    return "".join(c for c in texto if not unicodedata.combining(c))


def clave_deduplicacion(noticia: Noticia) -> str:
    titulo = re.sub(r"[^a-z0-9]+", "", normalizar(noticia.titulo))
    return titulo[:90]


def puntuar(noticia: Noticia) -> float:
    texto = normalizar(noticia.titulo + " " + noticia.resumen)
    puntuacion = 0.0
    for termino, peso in POSITIVOS.items():
        if termino in texto:
            puntuacion += peso
    for termino, peso in NEGATIVOS.items():
        if termino in texto:
            puntuacion += peso
    return puntuacion


def seleccionar(noticias: list[Noticia], cantidad: int = 10) -> list[Noticia]:
    mejores: dict[str, Noticia] = {}
    for noticia in noticias:
        reemplazada = Noticia(
            noticia.titulo,
            noticia.enlace,
            noticia.fuente,
            noticia.resumen,
            noticia.publicada,
            puntuar(noticia),
            noticia.imagen,
        )
        clave = clave_deduplicacion(noticia)
        actual = mejores.get(clave)
        if actual is None or reemplazada.puntuacion > actual.puntuacion:
            mejores[clave] = reemplazada

    seleccionadas = sorted(mejores.values(), key=lambda n: (-n.puntuacion, -n.publicada.timestamp()))
    positivas = [n for n in seleccionadas if n.puntuacion > 0]
    return positivas[:cantidad]
