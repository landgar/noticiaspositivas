from datetime import datetime, timezone

from noticias_positivas.modelos import Noticia
from noticias_positivas.puntuacion import seleccionar


def test_selecciona_noticias_positivas_y_deduplica():
    noticias = [
        Noticia("Gran avance científico", "https://a.example/articulo", "A", "Un éxito prometedor", datetime.now(timezone.utc)),
        Noticia("Gran avance científico", "https://b.example/articulo", "B", "Otro éxito", datetime.now(timezone.utc)),
        Noticia("Ataque e crisis", "https://a.example/negativa", "A", "Muertos", datetime.now(timezone.utc)),
    ]
    resultado = seleccionar(noticias, 10)
    assert len(resultado) == 1
    assert resultado[0].puntuacion > 0
