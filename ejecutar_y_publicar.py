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
raise SystemExit(resultado.returncode)
