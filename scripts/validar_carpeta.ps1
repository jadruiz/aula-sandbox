# Devuelve una única ruta canónica apta para montarse como /workspace.
# Equivalente en PowerShell de validar_carpeta.sh: mismas reglas, mismo resultado.
#
#   powershell -NoProfile -ExecutionPolicy Bypass -File scripts\validar_carpeta.ps1 C:\ruta\a\la\carpeta
param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string]$Carpeta
)

$ErrorActionPreference = "Stop"

function Fallar([string]$Mensaje) {
    [Console]::Error.WriteLine($Mensaje)
    exit 2
}

if ([string]::IsNullOrWhiteSpace($Carpeta)) {
    Fallar "Uso: validar_carpeta.ps1 C:\ruta\a\la\carpeta"
}

$item = Get-Item -LiteralPath $Carpeta -ErrorAction SilentlyContinue
if ($null -eq $item -or -not $item.PSIsContainer) {
    Fallar "La carpeta elegida no existe o no es un directorio: $Carpeta"
}
if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) {
    Fallar "La carpeta elegida no puede ser un enlace simbólico ni una unión (junction)."
}

$resuelta = $item.FullName.TrimEnd('\')
$raiz = [IO.Path]::GetPathRoot($resuelta).TrimEnd('\')
$perfil = $env:USERPROFILE
if ($perfil) { $perfil = $perfil.TrimEnd('\') }

if ($resuelta -ieq $raiz) {
    Fallar "No se permite montar la raíz de una unidad."
}
if ($perfil -and ($resuelta -ieq $perfil)) {
    Fallar "No se permite montar tu carpeta personal completa."
}
if ($perfil -and ($perfil.ToLowerInvariant() + '\').StartsWith($resuelta.ToLowerInvariant() + '\')) {
    Fallar "La carpeta es demasiado amplia: contiene tu carpeta personal."
}
if (Test-Path -LiteralPath (Join-Path $resuelta ".env")) {
    Fallar "La carpeta contiene .env. Mueve los secretos fuera antes de montarla."
}

Write-Output $resuelta
