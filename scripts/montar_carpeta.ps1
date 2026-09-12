# Windows: elegir una carpeta en el explorador y arrancar Aula con un único bind mount.
$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.Windows.Forms

$dialogo = New-Object System.Windows.Forms.FolderBrowserDialog
$dialogo.Description = "Elige la carpeta que verá Aula"
$dialogo.ShowNewFolderButton = $true

if ($dialogo.ShowDialog() -ne [System.Windows.Forms.DialogResult]::OK) { exit 0 }

& (Join-Path $PSScriptRoot "arrancar.ps1") $dialogo.SelectedPath
exit $LASTEXITCODE
