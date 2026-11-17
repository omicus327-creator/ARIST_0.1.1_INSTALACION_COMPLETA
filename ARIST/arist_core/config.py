from __future__ import annotations
import os
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / '.env')

def env_path(name: str, default: Path) -> Path:
    value = os.getenv(name, '').strip()
    return Path(value if value else default).expanduser().resolve()

APP_NAME = 'ARIST'
DATA_DIR = env_path('ARIST_DATA_DIR', ROOT / 'data')
WORKSPACE = env_path('ARIST_WORKSPACE', ROOT / 'workspace')
BACKUP_DIR = env_path('ARIST_BACKUP_DIR', ROOT / 'backups')
DB_PATH = DATA_DIR / 'arist.sqlite3'
OLLAMA_URL = os.getenv('ARIST_OLLAMA_URL', 'http://localhost:11434').rstrip('/')
OLLAMA_MODEL = os.getenv('ARIST_MODEL', 'llama3.2')
OLLAMA_TIMEOUT = int(os.getenv('ARIST_OLLAMA_TIMEOUT', '180'))
AI_PROVIDER = os.getenv('ARIST_AI_PROVIDER', 'ollama').lower()
CLOUD_BASE_URL = os.getenv('ARIST_CLOUD_BASE_URL', '').rstrip('/')
CLOUD_MODEL = os.getenv('ARIST_CLOUD_MODEL', '')
CLOUD_API_KEY = os.getenv('ARIST_CLOUD_API_KEY', '')
VOICE_LANGUAGE = os.getenv('ARIST_VOICE_LANGUAGE', 'es-MX')
WAKE_WORD = os.getenv('ARIST_WAKE_WORD', 'arist')
VOSK_MODEL_PATH = os.getenv('ARIST_VOSK_MODEL_PATH', '')
PRINTER_BACKEND = os.getenv('ARIST_PRINTER_BACKEND', 'none').lower()
OCTOPRINT_URL = os.getenv('ARIST_OCTOPRINT_URL', '').rstrip('/')
OCTOPRINT_API_KEY = os.getenv('ARIST_OCTOPRINT_API_KEY', '')
MOONRAKER_URL = os.getenv('ARIST_MOONRAKER_URL', '').rstrip('/')
MOONRAKER_API_KEY = os.getenv('ARIST_MOONRAKER_API_KEY', '')
PRINT_FILES_DIR = env_path('ARIST_PRINT_FILES_DIR', ROOT / 'print_files')
SLICER = os.getenv('ARIST_SLICER', 'none').lower()
SLICER_PATH = os.getenv('ARIST_SLICER_PATH', '')

for folder in (DATA_DIR, WORKSPACE, BACKUP_DIR, PRINT_FILES_DIR):
    folder.mkdir(parents=True, exist_ok=True)
