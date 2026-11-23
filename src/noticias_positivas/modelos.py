from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Noticia:
    titulo: str
    enlace: str
    fuente: str
    resumen: str
    publicada: datetime
    puntuacion: float = 0.0
    imagen: str = ""


if __name__ == "__main__":
    pass
