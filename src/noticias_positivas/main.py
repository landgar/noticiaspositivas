import argparse
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv() -> bool:
        """Permite ejecutar sin python-dotenv; las variables del sistema siguen disponibles."""
        return False

from .configuracion import cargar
from .recopilacion import recopilar
from .puntuacion import seleccionar
from .redaccion import generar_titulo, redactar
from .publicacion import crear_noticias_txt
from .traduccion import traducir_texto
from .modelos import Noticia


def ejecutar(configuracion: dict) -> None:
    noticias = recopilar(
        configuracion["fuentes"],
        configuracion.get("ventana_horas", 24),
    )
    seleccionadas = seleccionar(noticias, configuracion.get("cantidad_noticias", 10))
    if not seleccionadas:
        raise RuntimeError("No se encontraron noticias dentro de la ventana configurada.")

    url_traduccion = configuracion.get("url_traduccion", "")
    seleccionadas = [
        Noticia(
            titulo=traducir_texto(noticia.titulo, url_traduccion),
            enlace=noticia.enlace,
            fuente=noticia.fuente,
            resumen=traducir_texto(noticia.resumen, url_traduccion),
            publicada=noticia.publicada,
            puntuacion=noticia.puntuacion,
            imagen=noticia.imagen,
        )
        for noticia in seleccionadas
    ]

    zona_horaria = configuracion.get("zona_horaria", "Europe/Madrid")
    fecha = datetime.now(ZoneInfo(zona_horaria))
    titulo = generar_titulo(fecha, len(seleccionadas))

    ruta_repositorio = Path(configuracion.get("ruta_repositorio", ".")).resolve()
    ruta_txt = crear_noticias_txt(titulo, seleccionadas, fecha, ruta_repositorio)
    titulo_html, ruta_html = redactar(
        seleccionadas,
        zona_horaria,
        ruta_repositorio,
    )

    print(f"Generadas {len(seleccionadas)} noticias")
    print(f"Texto: {ruta_txt}")
    print(f"Página: {ruta_html}")


def main() -> None:
    load_dotenv()
    parser = argparse.ArgumentParser(description="Genera un fichero TXT diario con las noticias positivas")
    parser.add_argument("--config", default="config/configuracion.yml")
    argumentos = parser.parse_args()
    ejecutar(cargar(argumentos.config))


if __name__ == "__main__":
    main()
