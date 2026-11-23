from datetime import datetime
from zoneinfo import ZoneInfo

from noticias_positivas.modelos import Noticia
from noticias_positivas.publicacion import crear_noticias_html, crear_noticias_txt
from noticias_positivas.recopilacion import fuente_europea


def test_crea_fichero_txt_diario(tmp_path):
    noticia = Noticia(
        titulo="Avance positivo",
        enlace="https://example.com/noticia",
        fuente="Ejemplo",
        resumen="Una mejora concreta.",
        publicada=datetime.now(ZoneInfo("Europe/Madrid")),
        puntuacion=10,
    )

    ruta = crear_noticias_txt(
        "Las 1 noticias más positivas",
        [noticia],
        datetime(2026, 11, 23, tzinfo=ZoneInfo("Europe/Madrid")),
        tmp_path,
    )

    contenido = ruta.read_text(encoding="utf-8")
    assert ruta.name == "2026-11-23-noticias-positivas.txt"
    assert "Las 1 noticias más positivas" in contenido
    assert "1. Avance positivo" in contenido
    assert "Fuente: Ejemplo" in contenido
    assert "Enlace: https://example.com/noticia" in contenido


def test_crea_fichero_html_diario(tmp_path):
    noticia = Noticia(
        titulo="Avance positivo",
        enlace="https://example.com/noticia",
        fuente="Ejemplo",
        resumen="Una mejora concreta.",
        publicada=datetime.now(ZoneInfo("Europe/Madrid")),
        puntuacion=10,
    )

    ruta = crear_noticias_html(
        "Las 1 noticias más positivas",
        [noticia],
        datetime(2026, 11, 23, tzinfo=ZoneInfo("Europe/Madrid")),
        tmp_path,
    )

    contenido = ruta.read_text(encoding="utf-8")
    assert ruta.name == "2026-11-23-noticias-positivas.html"
    assert "<title>Las 1 noticias más positivas</title>" in contenido
    assert "<h1>Las 1 noticias más positivas</h1>" in contenido
    assert "<h2>1. Avance positivo</h2>" in contenido
    assert "Fuente: Ejemplo" in contenido
    assert 'href="https://example.com/noticia"' in contenido
    assert "Una mejora concreta." in contenido


def test_crea_pagina_html_periodistica(tmp_path):
    repositorio = tmp_path
    (repositorio / "plantillas").mkdir()
    (repositorio / "plantillas" / "entrada_hugo.html").write_text(
        '<h1>{{ titulo }}</h1>{% for noticia in noticias %}'
        '<h2>{{ noticia.titulo }}</h2><a href="{{ noticia.enlace }}">Fuente</a>'
        '{% if noticia.imagen %}<img src="{{ noticia.imagen }}">{% endif %}{% endfor %}',
        encoding="utf-8",
    )
    noticia = Noticia(
        titulo="Avance europeo",
        enlace="https://example.com/noticia",
        fuente="Ejemplo Europeo",
        resumen="Una mejora concreta.",
        publicada=datetime.now(ZoneInfo("Europe/Madrid")),
        puntuacion=10,
        imagen="https://example.com/foto.jpg",
    )

    ruta = crear_noticias_html(
        "Las 1 noticias más positivas",
        [noticia],
        datetime(2026, 11, 23, tzinfo=ZoneInfo("Europe/Madrid")),
        repositorio,
    )

    contenido = ruta.read_text(encoding="utf-8")
    assert ruta.name == "2026-11-23-noticias-positivas.html"
    assert "Avance europeo" in contenido
    assert 'href="https://example.com/noticia"' in contenido
    assert 'src="https://example.com/foto.jpg"' in contenido


def test_solo_admite_fuentes_europeas():
    assert fuente_europea({"pais": "España", "region": "Europa"})
    assert fuente_europea({"pais": "Francia", "region": "Europa"})
    assert not fuente_europea({"pais": "Canadá", "region": "América"})
    assert not fuente_europea({"pais": "Estados Unidos", "region": "América"})
