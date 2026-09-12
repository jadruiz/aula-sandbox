@echo off
rem Arranca el aula en Windows. Doble clic. Llama a arrancar.ps1 sin cambiar la politica
rem de ejecucion del sistema: el Bypass aplica solo a esta ventana.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0arrancar.ps1" %*
