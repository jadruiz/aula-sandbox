# Apaga el aula en Windows. Los flujos de LangFlow y tu carpeta de trabajo se conservan.
$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..")

docker compose -f infrastructure/docker-compose.yml down
Write-Host ""
Write-Host "  Aula apagada. Tu trabajo sigue en tu carpeta y tus flujos"
Write-Host "  de LangFlow reaparecerán en el próximo arranque."
if ($Host.Name -eq "ConsoleHost") { Read-Host "Pulsa Enter para cerrar" | Out-Null }
