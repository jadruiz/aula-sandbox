# Prueba de arranque en Windows

## TL;DR

Diez minutos en un equipo Windows con Docker Desktop. Los scripts de Windows se probaron en un
contenedor de PowerShell, no con doble clic real; esta guía cierra ese hueco. Quien la ejecute
manda las capturas al instructor y el resultado se anota en `reports/`.

## Requisitos

- Windows 10 u 11 con Docker Desktop instalado y abierto, backend WSL 2.
- Este repo descargado como ZIP o clonado, en una carpeta propia, por ejemplo `Documentos\aula-sandbox`.
- Sin `.env` previo, o con uno sin claves.

## Pasos y evidencia

| # | Acción | Resultado esperado | Captura |
|---|---|---|---|
| 1 | Doble clic en `scripts\arrancar.bat` | ventana con "Aula · Ecosistemas Inteligentes"; crea `.env`; construye la imagen la primera vez | la ventana al terminar |
| 2 | Abrir <http://localhost:8888> | JupyterLab con la carpeta `trabajo` | pestaña del navegador |
| 3 | Abrir <http://localhost:7860> | LangFlow sin pantalla de login | pestaña del navegador |
| 4 | Crear un archivo en Jupyter | aparece en `trabajo\` en el explorador | explorador |
| 5 | Doble clic en `scripts\detener.bat` | contenedores detenidos; `trabajo\` intacta | la ventana |
| 6 | Doble clic en `scripts\montar_carpeta.bat` y elegir una carpeta vacía de `Documentos` | Aula arranca y Jupyter muestra esa carpeta | Jupyter |
| 7 | Repetir 6 eligiendo tu carpeta de usuario completa | mensaje "No se permite montar tu carpeta personal completa" y no arranca | la ventana |
| 8 | `scripts\detener.bat` | apagado limpio | ninguna |

## Si algo falla

- "Docker no responde": abre Docker Desktop y espera a que el icono deje de animarse.
- Ventana que se cierra sola: abre PowerShell en la carpeta del repo y corre
  `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\arrancar.ps1` para ver el error.
- Puerto ocupado: cierra otra instancia de Jupyter o LangFlow.
- Conserva el texto del error completo; no bajes ningún gate para que arranque.

## Dónde se registra

`reports/YYYY-MM-DD-prueba-windows.md` con versión de Windows, versión de Docker Desktop, el
resultado de cada paso y las capturas relevantes.
