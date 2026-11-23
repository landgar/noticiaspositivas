import argparse
import time
from datetime import datetime, timedelta
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
from .publicacion import crear_noticias_txt, publicar_cambios_diarios
from .traduccion import traducir_texto
from .modelos import Noticia


def siguiente_fecha_ejecucion(fecha_actual: datetime, hora: str = "09:00") -> datetime:
    """Devuelve siempre el mismo horario del día siguiente."""
    horas, minutos = (int(parte) for parte in hora.split(":"))
    if horas < 0 or horas > 23 or minutos < 0 or minutos > 59:
        raise ValueError("La hora diaria debe tener formato HH:MM y estar entre 00:00 y 23:59.")

    siguiente = fecha_actual + timedelta(days=1)
    return siguiente.replace(hour=horas, minute=minutos, second=0, microsecond=0)


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


def ejecutar_y_publicar(configuracion: dict, sin_publicar: bool = False) -> None:
    ejecutar(configuracion)

    if not sin_publicar:
        ruta_repositorio = Path(configuracion.get("ruta_repositorio", ".")).resolve()
        try:
            publicar_cambios_diarios(ruta_repositorio)
        except Exception as error:
            raise RuntimeError(
                "La edición se generó, pero no pudo publicarse en GitHub. "
                "Comprueba Git, la autenticación y que 'origin' apunta al repositorio."
            ) from error


def main() -> None:
    load_dotenv()
    parser = argparse.ArgumentParser(description="Genera y publica diariamente las noticias positivas")
    parser.add_argument("--config", default="config/configuracion.yml")
    parser.add_argument(
        "--sin-publicar",
        action="store_true",
        help="Genera la edición sin hacer commit ni push",
    )
    parser.add_argument(
        "--una-vez",
        action="store_true",
        help="Genera una sola edición y termina",
    )
    argumentos = parser.parse_args()
    configuracion = cargar(argumentos.config)

    if argumentos.una_vez:
        ejecutar_y_publicar(configuracion, argumentos.sin_publicar)
        return

    zona_horaria = configuracion.get("zona_horaria", "Europe/Madrid")
    zona = ZoneInfo(zona_horaria)
    hora = configuracion.get("hora_generacion_diaria", "09:00")

    try:
        while True:
            try:
                ejecutar_y_publicar(configuracion, argumentos.sin_publicar)
            except RuntimeError as error:
                print(f"Aviso: {error}")
            siguiente = siguiente_fecha_ejecucion(datetime.now(zona), hora)
            segundos = max(1, (siguiente - datetime.now(zona)).total_seconds())
            print(f"Próxima ejecución: {siguiente.strftime('%d/%m/%Y %H:%M')} ({zona_horaria})")
            print("Esperando a la siguiente edición diaria...")
            time.sleep(segundos)
    except KeyboardInterrupt:
        print("Ejecución diaria detenida por el usuario.")
