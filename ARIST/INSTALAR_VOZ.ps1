$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
$venvPython = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $venvPython)) { throw "Primero ejecuta INSTALAR_ARIST.ps1" }
& $venvPython -m pip install -r requirements-voice.txt
Write-Host "Prueba: .\.venv\Scripts\python.exe arist.py --voz-manual"
Write-Host "Si PyAudio falla en Python 3.13, revisa el README y prueba Python 3.11/3.12."
