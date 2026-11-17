# ARIST 0.1.1

Asistente modular para Windows enfocado en programación, revisión de proyectos, voz y gestión de impresión 3D.

> Base inicial: las comprobaciones de sintaxis no equivalen a pruebas con impresoras físicas, micrófonos ni modelos locales.

## 1. Requisitos

- Windows 10 u 11.
- Python 3.10 o superior. Para compatibilidad de bibliotecas de audio, se recomienda Python 3.11 o 3.12. El núcleo y modo texto pueden funcionar con Python 3.13.
- 8 GB de RAM. Comienza con `llama3.2`; si el equipo se queda corto de memoria, prueba `llama3.2:1b`.
- Internet para descargar Ollama/modelos, usar reconocimiento de voz Google y proveedores cloud.
- Micrófono para voz.
- OctoPrint o Moonraker configurado para controlar una impresora compatible.

## 2. Instalar el núcleo

1. Extrae el ZIP en una carpeta, por ejemplo `C:\ARIST`.
2. Abre PowerShell dentro de esa carpeta.
3. Ejecuta:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\INSTALAR_ARIST.ps1
```

El instalador crea el entorno virtual `.venv`, instala las dependencias base, crea `.env` y las carpetas necesarias. No modifica la instalación global de Python.

Instalación manual equivalente:

```powershell
cd C:\ARIST
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Bibliotecas base: `requests` (conexiones HTTP), `python-dotenv` (configuración) y `pytest` (soporte de pruebas).

## 3. Ollama y modelo de IA

Ejecuta:

```powershell
.\INSTALAR_OLLAMA.ps1
```

El script comprueba Ollama, ofrece instalarlo con `winget` si falta, descarga `llama3.2` solo si no está instalado y comprueba la API local.

Instalación manual:

1. Instala Ollama desde https://ollama.com/download/windows.
2. Abre Ollama.
3. Ejecuta:

```powershell
ollama pull llama3.2
ollama list
ollama run llama3.2
```

Escribe `/bye` para salir de la prueba. ARIST ya está configurado para `ARIST_MODEL=llama3.2` en `.env`. Si ese modelo ya está instalado, no lo descargues otra vez.

Alternativa más pequeña para equipos con memoria limitada:

```powershell
ollama pull llama3.2:1b
```

Después cambia en `.env`:

```ini
ARIST_MODEL=llama3.2:1b
```

No es necesario descargar ambos. El modelo se descarga por separado y no está incluido en el ZIP.

## 4. Iniciar ARIST

```powershell
.\.venv\Scripts\python.exe arist.py
```

También puedes usar `run_arist.bat` después de instalar dependencias.

## 5. Voz (opcional)

Ejecuta:

```powershell
.\INSTALAR_VOZ.ps1
```

Equivalente manual:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-voice.txt
```

Modos:

```powershell
.\.venv\Scripts\python.exe arist.py --voz
.\.venv\Scripts\python.exe arist.py --voz-manual
```

`--voz` escucha continuamente. `--voz-manual` espera Enter antes de cada instrucción.

**Limitación importante:** el reconocimiento de las instrucciones usa Google Speech Recognition y requiere Internet. La síntesis de voz con `pyttsx3` es local. PyAudio puede fallar si no hay wheel compatible con tu versión de Python. Si ocurre en Python 3.13, prueba Python 3.11 o 3.12 y crea el entorno con esa versión; no hace falta desinstalar Python 3.13.

Ejemplo con Python 3.12:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -r requirements-voice.txt
```

## 6. Palabra clave «ARIST»

Ejecuta:

```powershell
.\DESCARGAR_MODELO_VOSK.ps1
```

Instala Vosk, descarga el modelo pequeño de español y configura la ruta en `.env`. Después:

```powershell
.\.venv\Scripts\python.exe arist.py --activar-voz
```

Vosk detecta localmente la palabra clave. La transcripción de la orden posterior sigue usando Google Speech Recognition y requiere Internet. Por tanto, esta versión no tiene reconocimiento de órdenes completamente offline.

## 7. Comprobar instalación

```powershell
.\COMPROBAR_INSTALACION.ps1
```

Comprueba dependencias, Ollama, modelos y ayuda de ARIST. Las dependencias de voz pueden aparecer como ausentes si no se instalaron.

## 8. Configurar impresora 3D

Edita `.env` con el Bloc de notas. No compartas este archivo: puede contener claves API.

OctoPrint:

```ini
ARIST_PRINTER_BACKEND=octoprint
ARIST_OCTOPRINT_URL=http://IP_DE_TU_OCTOPRINT
ARIST_OCTOPRINT_API_KEY=TU_CLAVE_API
```

Moonraker / Klipper:

```ini
ARIST_PRINTER_BACKEND=moonraker
ARIST_MOONRAKER_URL=http://IP_DE_TU_MOONRAKER
ARIST_MOONRAKER_API_KEY=
```

En esta versión los backends implementados son OctoPrint y Moonraker. No existe un protocolo universal para todas las impresoras. Otras marcas requieren adaptadores específicos y pruebas con su modelo y firmware.

## 9. Carpetas y comandos

- `workspace/`: proyectos que ARIST puede leer y revisar.
- `backups/`: copias previas al reemplazo de archivos.
- `print_files/`: modelos 3D y G-code.
- `data/arist.sqlite3`: historial local de trabajos.

Comandos:
- `ayuda`
- `programa <descripción>`
- `corrige <problema>`
- `revisa archivo <ruta>`
- `revisa proyecto`
- `crea archivo <ruta> | <descripción>`
- `comprueba sintaxis <archivo.py>`
- `archivos proyecto`
- `unidades`
- `lista directorios`
- `crea directorio <ruta>`
- `elimina directorio <ruta>` (solo elimina directorios vacíos y pide confirmación)
- `cambia permisos <ruta> <r|w>` (Windows: solo lectura o escritura)
- `lista archivos 3d`
- `carga archivo <archivo.gcode>`
- `inicia impresion <archivo.gcode>`
- `estado impresora`
- `historial`
- `salir`

Las cargas e inicios requieren confirmación. El laminado automático de STL/3MF/OBJ aún no está implementado. Usa Cura o PrusaSlicer para generar G-code y coloca ese archivo en `print_files/`.

## 10. Limitaciones conocidas

- El ZIP no contiene Ollama, el modelo Llama ni el modelo Vosk: se instalan/descargan por separado.
- El reconocimiento de instrucciones por voz necesita Internet.
- No se ha validado la compatibilidad con todas las impresoras.
- Laminado automático todavía no está implementado.
- El seguimiento automático de trabajos es limitado.
- La revisión sintáctica no garantiza que un programa funcione.
- Las pruebas físicas deben realizarse en el equipo y con el hardware correspondiente.

## 11. Seguridad

- Revisa el código generado antes de ejecutarlo.
- No compartas `.env` ni claves API.
- Mantén OctoPrint/Moonraker en red privada; usa VPN o acceso seguro para conexiones remotas.
- Comprueba impresora, material, temperaturas, cama y G-code antes de iniciar una impresión.
