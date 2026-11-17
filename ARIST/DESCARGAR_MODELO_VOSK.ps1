$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
$venvPython = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $venvPython)) { throw "Primero ejecuta INSTALAR_ARIST.ps1" }
& $venvPython -m pip install vosk
$modelsDir = Join-Path $PSScriptRoot "models"
New-Item -ItemType Directory -Force -Path $modelsDir | Out-Null
$zipPath = Join-Path $modelsDir "vosk-model-small-es-0.42.zip"
$modelDir = Join-Path $modelsDir "vosk-model-small-es-0.42"
if (-not (Test-Path $modelDir)) {
    Invoke-WebRequest -Uri "https://alphacephei.com/vosk/models/vosk-model-small-es-0.42.zip" -OutFile $zipPath
    Expand-Archive -Path $zipPath -DestinationPath $modelsDir -Force
    Remove-Item $zipPath -Force
}
if (-not (Test-Path ".env")) { Copy-Item ".env.example" ".env" }
$setting = "ARIST_VOSK_MODEL_PATH=$modelDir"
$content = Get-Content ".env" -Raw
if ($content -match '(?m)^ARIST_VOSK_MODEL_PATH=.*$') {
    $content = [regex]::Replace($content, '(?m)^ARIST_VOSK_MODEL_PATH=.*$', [System.Text.RegularExpressions.MatchEvaluator]{ param($m) $setting })
} else { $content += "`r`n$setting`r`n" }
Set-Content -Path ".env" -Value $content -Encoding utf8
Write-Host "Modelo Vosk instalado: $modelDir" -ForegroundColor Green
Write-Host "Ejecuta: .\.venv\Scripts\python.exe arist.py --activar-voz"
