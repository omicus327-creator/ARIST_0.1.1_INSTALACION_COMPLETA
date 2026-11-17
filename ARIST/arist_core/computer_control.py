"""Acciones locales y visibles bajo demanda; sin captura de pantalla ni teclado."""

import csv
import ctypes
import os
import subprocess
from pathlib import Path


OPENABLE_EXTENSIONS = {
    ".txt", ".md", ".pdf", ".rtf", ".doc", ".docx", ".xls", ".xlsx",
    ".ppt", ".pptx", ".csv", ".png", ".jpg", ".jpeg", ".gif", ".bmp",
    ".mp3", ".wav", ".m4a", ".flac", ".ogg", ".wma", ".mp4", ".mkv",
    ".avi", ".mov", ".webm", ".wmv",
}
MEDIA_EXTENSIONS = {
    ".mp3", ".wav", ".m4a", ".flac", ".ogg", ".wma", ".mp4", ".mkv",
    ".avi", ".mov", ".webm", ".wmv",
}


def _existing_file(raw_path: str) -> Path:
    path = Path(raw_path.strip().strip('"')).expanduser().resolve()
    if not path.is_file():
        raise FileNotFoundError(f"No encontré el archivo: {path}")
    return path


def open_file(raw_path: str) -> Path:
    path = _existing_file(raw_path)
    if path.suffix.lower() not in OPENABLE_EXTENSIONS:
        raise ValueError("Por seguridad solo se abren documentos, imágenes y archivos multimedia compatibles.")
    os.startfile(str(path))
    return path


def play_media(raw_path: str) -> Path:
    path = _existing_file(raw_path)
    if path.suffix.lower() not in MEDIA_EXTENSIONS:
        raise ValueError("El archivo no tiene un formato de audio o video compatible.")
    os.startfile(str(path))
    return path


def move_pointer(x: int, y: int) -> tuple[int, int]:
    if os.name != "nt":
        raise OSError("El control del cursor está disponible en Windows.")
    user32 = ctypes.windll.user32
    width, height = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
    if not (0 <= x < width and 0 <= y < height):
        raise ValueError(f"Coordenadas fuera de pantalla; usa x=0–{width - 1}, y=0–{height - 1}.")
    if not user32.SetCursorPos(x, y):
        raise OSError("Windows no pudo mover el cursor.")
    return x, y


def click_pointer() -> None:
    if os.name != "nt":
        raise OSError("El control del cursor está disponible en Windows.")
    user32 = ctypes.windll.user32
    user32.mouse_event(0x0002, 0, 0, 0, 0)  # botón izquierdo abajo
    user32.mouse_event(0x0004, 0, 0, 0, 0)  # botón izquierdo arriba


def system_snapshot() -> str:
    if os.name != "nt":
        raise OSError("El monitoreo está disponible en Windows.")

    class MEMORYSTATUSEX(ctypes.Structure):
        _fields_ = [
            ("dwLength", ctypes.c_ulong),
            ("dwMemoryLoad", ctypes.c_ulong),
            ("ullTotalPhys", ctypes.c_ulonglong),
            ("ullAvailPhys", ctypes.c_ulonglong),
            ("ullTotalPageFile", ctypes.c_ulonglong),
            ("ullAvailPageFile", ctypes.c_ulonglong),
            ("ullTotalVirtual", ctypes.c_ulonglong),
            ("ullAvailVirtual", ctypes.c_ulonglong),
            ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
        ]

    status = MEMORYSTATUSEX()
    status.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
        raise OSError("Windows no pudo leer el estado de memoria.")

    result = subprocess.run(
        ["tasklist", "/FO", "CSV", "/NH"],
        capture_output=True,
        text=True,
        encoding="mbcs",
        errors="replace",
        check=True,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
    process_names = []
    for row in csv.reader(result.stdout.splitlines()):
        if row and row[0] not in process_names:
            process_names.append(row[0])
    total_gb = status.ullTotalPhys / (1024 ** 3)
    free_gb = status.ullAvailPhys / (1024 ** 3)
    visible_names = ", ".join(process_names[:30]) or "no disponible"
    extra = max(0, len(process_names) - 30)
    suffix = f" (y {extra} más)" if extra else ""
    return (
        f"RAM: {status.dwMemoryLoad}% usada; {free_gb:.1f} GB libres de {total_gb:.1f} GB.\n"
        f"Procesos activos ({len(process_names)} nombres): {visible_names}{suffix}.\n"
        "Consulta puntual: no monitorea en segundo plano."
    )
