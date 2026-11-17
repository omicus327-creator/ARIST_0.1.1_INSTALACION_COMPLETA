"""Operaciones de archivos confinadas a la carpeta de instalación de ARIST."""

import ctypes
import os
import stat
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]


def get_devices():
    if os.name != "nt":
        return []
    drive_mask = ctypes.windll.kernel32.GetLogicalDrives()
    return [
        f"{chr(ord('A') + index)}:\\"
        for index in range(26)
        if drive_mask & (1 << index)
    ]


def get_safe_path(raw_path: str) -> Path:
    path = (BASE_DIR / raw_path.strip().strip('"')).resolve()
    try:
        path.relative_to(BASE_DIR)
    except ValueError as exc:
        raise ValueError(f"La ruta debe estar dentro de {BASE_DIR}") from exc
    if path == BASE_DIR:
        raise ValueError("No se permiten operaciones sobre la carpeta base.")
    return path


def get_directories(limit: int = 200) -> list[Path]:
    directories = []
    for root, dirs, _files in os.walk(BASE_DIR):
        dirs[:] = [name for name in dirs if name not in {".venv", "models", "__pycache__"}]
        directories.extend(Path(root) / name for name in dirs)
        if len(directories) >= limit:
            return directories[:limit]
    return directories


def create_directory(raw_path: str) -> Path:
    path = get_safe_path(raw_path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def delete_directory(raw_path: str) -> Path:
    path = get_safe_path(raw_path)
    if not path.is_dir():
        raise ValueError("La ruta indicada no es un directorio.")
    path.rmdir()  # Solo elimina directorios vacíos.
    return path


def set_permissions(raw_path: str, mode: str) -> Path:
    path = get_safe_path(raw_path)
    if not path.exists():
        raise FileNotFoundError(f"No existe: {path}")

    mode = mode.strip().lower()
    if os.name == "nt":
        if mode == "r":
            path.chmod(stat.S_IREAD)
        elif mode == "w":
            path.chmod(stat.S_IREAD | stat.S_IWRITE)
        else:
            raise ValueError("En Windows usa 'r' (solo lectura) o 'w' (escritura). 'x' no es compatible con chmod.")
    else:
        if not mode.isdigit() or any(digit not in "01234567" for digit in mode):
            raise ValueError("Usa permisos octales, por ejemplo 644 o 755.")
        path.chmod(int(mode, 8))
    return path
