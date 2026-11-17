$ErrorActionPreference = "Continue"
Set-Location $PSScriptRoot
$venvPython = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
Write-Host "`n=== PYTHON Y BIBLIOTECAS ===" -ForegroundColor Cyan
if (Test-Path $venvPython) {
    & $venvPython --version
    & $venvPython -c "import requests, dotenv, pytest; print('Dependencias base: OK')"
    & $venvPython -c "import speech_recognition, pyttsx3, pyaudio; print('Dependencias de voz: OK')"
    & $venvPython -c "import vosk; print('Vosk: OK')"
} else { Write-Warning "No existe .venv. Ejecuta INSTALAR_ARIST.ps1" }
Write-Host "`n=== OLLAMA ===" -ForegroundColor Cyan
if (Get-Command ollama -ErrorAction SilentlyContinue) {
    ollama --version
    ollama list
    try {
        $null = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -TimeoutSec 5
        Write-Host "API local de Ollama responde."
    } catch { Write-Warning "La API local no responde. Abre Ollama." }
} else { Write-Warning "Ollama no está instalado o no está en PATH." }
Write-Host "`n=== AYUDA ARIST ===" -ForegroundColor Cyan
if (Test-Path $venvPython) { & $venvPython arist.py --help }
