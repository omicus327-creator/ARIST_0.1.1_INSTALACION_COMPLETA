$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
Write-Host "`n=== INSTALADOR DE ARIST ===" -ForegroundColor Cyan
if (-not (Get-Command py -ErrorAction SilentlyContinue)) {
    throw "No se encontró 'py'. Instala Python desde https://www.python.org/downloads/windows/ y marca Add Python to PATH."
}
if (-not (Test-Path ".venv")) { py -3 -m venv .venv }
$venvPython = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $venvPython)) { throw "No se pudo crear el entorno virtual." }
& $venvPython -m pip install --upgrade pip
& $venvPython -m pip install -r requirements.txt
if (-not (Test-Path ".env")) { Copy-Item ".env.example" ".env" }
foreach ($folder in @("workspace", "print_files", "backups", "data")) {
    New-Item -ItemType Directory -Force -Path $folder | Out-Null
}
Write-Host "`nInstalación base terminada." -ForegroundColor Green
Write-Host "Siguiente: .\INSTALAR_OLLAMA.ps1"
Write-Host "Inicio: .\.venv\Scripts\python.exe arist.py"
