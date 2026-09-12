# Arranca el aula en Windows. Misma lógica que arrancar.command: valida la carpeta,
# comprueba Docker, crea .env sin credenciales y levanta los contenedores.
#
#   powershell -NoProfile -ExecutionPolicy Bypass -File scripts\arrancar.ps1
#   powershell -NoProfile -ExecutionPolicy Bypass -File scripts\arrancar.ps1 C:\ruta\a\mi-proyecto
#
# Para doble clic usa scripts\arrancar.bat, que llama a este archivo.
param(
    [Parameter(Position = 0)]
    [string]$Carpeta = "trabajo"
)

$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..")

function Cerrar([int]$Codigo) {
    if ($Host.Name -eq "ConsoleHost") { Read-Host "Pulsa Enter para cerrar" | Out-Null }
    exit $Codigo
}

Write-Host "════════════════════════════════════════════════════"
Write-Host "  Aula · Ecosistemas Inteligentes"
Write-Host "════════════════════════════════════════════════════"

# 1. Carpeta única que verá el aula.
try {
    $workspace = & powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $PSScriptRoot "validar_carpeta.ps1") $Carpeta 2>&1
    if ($LASTEXITCODE -ne 0) { throw ($workspace | Out-String) }
    $workspace = ($workspace | Select-Object -Last 1).ToString().Trim()
} catch {
    Write-Host ""
    Write-Host "  $($_.Exception.Message)"
    Cerrar 1
}
$env:AULA_WORKSPACE = $workspace

# 2. ¿Está Docker Desktop corriendo?
docker info *> $null
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "  Falta Docker Desktop (o no está abierto)."
    Write-Host ""
    Write-Host "  1. Descárgalo de https://www.docker.com/products/docker-desktop/ (te lo abro ahora)"
    Write-Host "  2. Instálalo con el backend WSL 2 y ábrelo una vez"
    Write-Host "  3. Vuelve a hacer doble clic en arrancar.bat"
    Start-Process "https://www.docker.com/products/docker-desktop/"
    Cerrar 1
}

# 3. .env sin credenciales: el primer arranque es offline.
if (-not (Test-Path ".env")) {
    Copy-Item ".env.ejemplo" ".env"
    Write-Host ""
    Write-Host "  Te acabo de crear .env sin credenciales. Aula continuará en modo offline."
} elseif (Select-String -Path ".env" -Pattern "PEGA-AQUI-TU-CLAVE" -Quiet) {
    # Compatibilidad con clones anteriores; el marcador no es una credencial real.
    (Get-Content ".env") -replace "sk-proj-PEGA-AQUI-TU-CLAVE", "" | Set-Content ".env"
    Write-Host ""
    Write-Host "  Se quitó el marcador de ejemplo. Aula continuará en modo offline."
}

# 4. Levantar. La primera vez construye la imagen: 10-15 minutos es normal.
Write-Host ""
Write-Host "  Levantando contenedores (la primera vez tarda 10-15 min)..."
docker compose -f infrastructure/docker-compose.yml up -d --build
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "  Algo falló al levantar. Haz una captura de lo de arriba y"
    Write-Host "  mándasela al instructor."
    Cerrar 1
}

Write-Host ""
Write-Host "  Listo. Tus herramientas:"
Write-Host ""
Write-Host "    JupyterLab (labs de código) →  http://localhost:8888"
Write-Host "    LangFlow  (agentes visuales) →  http://localhost:7860"
Write-Host ""
Write-Host "  Tu carpeta de trabajo es:  $workspace"
Write-Host "  Para apagar todo: doble clic en scripts\detener.bat"
Start-Process "http://localhost:8888"
Start-Sleep -Seconds 3
Start-Process "http://localhost:7860"
Cerrar 0
