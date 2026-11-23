import subprocess
import sys
from pathlib import Path

BASE_PROYECTO = Path(__file__).resolve().parent
PYTHON = BASE_PROYECTO / ".venv" / "Scripts" / "python.exe"
if not PYTHON.exists():
    PYTHON = Path(sys.executable)

resultado = subprocess.run(
    [str(PYTHON), str(BASE_PROYECTO / "main.py")],
    cwd=BASE_PROYECTO,
    check=False,
)
if resultado.returncode != 0:
    raise SystemExit(resultado.returncode)

sys.path.insert(0, str(BASE_PROYECTO / "src"))
from noticias_positivas.publicacion import publicar_cambios_diarios

publicar_cambios_diarios(BASE_PROYECTO)
