$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
if (-not (Get-Command ollama -ErrorAction SilentlyContinue)) {
    Write-Host "Ollama no está disponible en PATH."
    if (Get-Command winget -ErrorAction SilentlyContinue) {
        $answer = Read-Host "¿Instalar Ollama con winget ahora? (S/N)"
        if ($answer -match '^[sS]') {
            winget install --id Ollama.Ollama -e
            Write-Host "Si el comando ollama no aparece, cierra y vuelve a abrir PowerShell."
        } else {
            Start-Process "https://ollama.com/download/windows"
            exit 0
        }
    } else {
        Start-Process "https://ollama.com/download/windows"
        Write-Host "Instala Ollama, reinicia PowerShell y vuelve a ejecutar este script."
        exit 0
    }
}
if (-not (Get-Command ollama -ErrorAction SilentlyContinue)) {
    Write-Warning "Ollama aún no está disponible en esta terminal. Reinicia PowerShell."
    exit 1
}
Write-Host "`nModelos instalados:"
ollama list
$models = ollama list 2>$null | Out-String
if ($models -notmatch 'llama3\.2') {
    Write-Host "`nDescargando llama3.2..."
    ollama pull llama3.2
} else {
    Write-Host "`nllama3.2 ya está instalado; se omite la descarga."
}
try {
    $null = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -TimeoutSec 5
    Write-Host "API local de Ollama responde." -ForegroundColor Green
} catch {
    Write-Warning "No responde localhost:11434. Comprueba que Ollama esté abierto."
}
Write-Host "ARIST usa ARIST_MODEL=llama3.2 en .env."
