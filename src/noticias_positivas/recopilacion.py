import html
import re
from datetime import datetime, timedelta, timezone

import feedparser

from .modelos import Noticia


PaisesEuropeos = {
    "alemania", "austria", "belgica", "bélgica", "bulgaria", "chipre",
    "croacia", "dinamarca", "eslovaquia", "eslovenia", "espana", "españa",
    "estonia", "finlandia", "francia", "grecia", "hungria", "hungría",
    "irlanda", "italia", "letonia", "lituania", "luxemburgo", "malta",
    "noruega", "paises bajos", "países bajos", "polonia", "portugal",
    "reino unido", "republica checa", "república checa", "rumania", "romania",
    "suecia", "suiza", "ucrania", "union europea", "unión europea",
}

PALABRAS_ESPANOLAS = {
    "el", "la", "los", "las", "de", "del", "en", "por", "para",
    "con", "sin", "una", "un", "que", "se", "es", "está", "como",
    "más", "sobre", "tras", "desde", "tras", "su", "sus", "contra",
}


def limpiar_texto(texto: str) -> str:
    texto = re.sub(r"<[^>]+>", " ", texto or "")
    texto = html.unescape(texto)
    return re.sub(r"\s+", " ", texto).strip()


def fecha_entrada(entrada) -> datetime:
    for campo in ("published_parsed", "updated_parsed", "created_parsed"):
        valor = getattr(entrada, campo, None)
        if valor:
            return datetime(*valor[:6], tzinfo=timezone.utc)
    return datetime.now(timezone.utc)


def fuente_espanola(fuente: dict) -> bool:
    """Acepta únicamente medios declarados españoles."""
    pais = str(fuente.get("pais", "")).strip().lower()
    region = str(fuente.get("region", "")).strip().lower()

    return (
        pais in {"espana", "españa"}
        and region in {"espana", "españa"}
    )


def extraer_imagen(entrada) -> str:
    for atributo in ("media_content", "media_thumbnail"):
        elementos = getattr(entrada, atributo, []) or []
        for elemento in elementos:
            url = elemento.get("url", "") if isinstance(elemento, dict) else ""
            if url:
                return url

    for adjunto in getattr(entrada, "enclosures", []) or []:
        tipo = adjunto.get("type", "")
        url = adjunto.get("href", adjunto.get("url", ""))
        if url and (tipo.startswith("image/") or re.search(r"\.(jpg|jpeg|png|webp)(?:$|[?])", url, re.I)):
            return url

    contenido = " ".join(
        str(entrada.get(campo, ""))
        for campo in ("summary", "description", "content")
        if entrada.get(campo)
    )
    coincidencia = re.search(r'<img[^>]+(?:src|data-src)=["\']([^"\']+)', contenido, re.I)
    return coincidencia.group(1) if coincidencia else ""


def recopilar(
    fuentes: list[dict],
    ventana_horas: int = 24,
) -> list[Noticia]:
    limite = datetime.now(timezone.utc) - timedelta(hours=ventana_horas)
    noticias: list[Noticia] = []

    for fuente in fuentes:
        if not fuente_espanola(fuente):
            continue

        canal = feedparser.parse(fuente["rss"])
        for entrada in canal.entries:
            publicada = fecha_entrada(entrada)
            if publicada < limite:
                continue

            titulo = limpiar_texto(entrada.get("title", ""))
            resumen = limpiar_texto(entrada.get("summary", entrada.get("description", "")))
            enlace = entrada.get("link", "")
            noticias.append(Noticia(
                titulo,
                enlace,
                fuente["nombre"],
                resumen,
                publicada,
                imagen=extraer_imagen(entrada),
            ))

    return noticias
