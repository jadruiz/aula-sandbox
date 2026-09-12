@echo off
rem Elige una carpeta y arranca el aula con ese unico bind mount. Doble clic.
powershell -NoProfile -ExecutionPolicy Bypass -STA -File "%~dp0montar_carpeta.ps1"
