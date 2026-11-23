import sys
from pathlib import Path

# Permite ejecutar main.py directamente desde el repositorio,
# sin necesidad de instalar previamente el paquete con pip.
BASE_PROYECTO = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_PROYECTO / "src"))

from noticias_positivas.main import main


if __name__ == "__main__":
    main()
