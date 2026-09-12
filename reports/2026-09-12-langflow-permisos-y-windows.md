# LangFlow: permisos del volumen, login y scripts de Windows — 2026-09-12

## Qué se observó

- LangFlow caía al arrancar: su volumen `langflow-datos` se montaba en `/datos`, ruta que no
  existe en la imagen. Docker crea ese punto de montaje como `root:root`; la imagen corre como
  `user` (UID 1000, GID 0) y no puede escribir ahí ni la base ni la llave secreta.
- La imagen trae `LANGFLOW_AUTO_LOGIN=false`: el primer arranque pedía un superusuario que
  nadie en el aula conoce.
- No existían lanzadores para Windows; sólo `.command` y `.sh`.

## Fuente de la verificación

Dockerfile oficial `docker/build_and_push.Dockerfile` del repositorio de LangFlow: `useradd
user -u 1000 -g 0`, `chown -R 1000:0 /app/data /app/langflow`, `HOME=/app/data`,
`LANGFLOW_AUTO_LOGIN=false`. La documentación de despliegue usa `LANGFLOW_CONFIG_DIR=/app/langflow`
con el volumen montado en esa ruta.

## Qué cambió

| Archivo | Cambio |
|---|---|
| `infrastructure/docker-compose.yml` | servicio `langflow-init` que corrige propiedad del volumen a `1000:0`; `LANGFLOW_CONFIG_DIR=/app/langflow`; volumen en `/app/langflow`; `LANGFLOW_AUTO_LOGIN=true`; `depends_on` con `service_completed_successfully` |
| `scripts/validar_carpeta.ps1`, `arrancar.ps1`, `detener.ps1`, `montar_carpeta.ps1` | equivalentes en PowerShell con las mismas reglas de frontera |
| `scripts/arrancar.bat`, `detener.bat`, `montar_carpeta.bat` | lanzadores de doble clic; `ExecutionPolicy Bypass` sólo para esa ventana |
| `.gitattributes` | `.bat` y `.ps1` con CRLF; `.sh` y `.command` con LF |
| `tests/test_workspace_mount.py` | contrato del compose y existencia de los scripts de Windows |
| `README.md`, `docs/QUICKSTART.md` | arranque en Windows y recuperación de LangFlow |

`LANGFLOW_AUTO_LOGIN=true` sigue el mismo criterio que Jupyter sin token en ADR-001: el
puerto sólo se publica en `127.0.0.1`. No protege de otros procesos locales.

## Qué no se verificó en esta sesión

- No había daemon de Docker disponible: no se construyó ni levantó la pila, ni se probó el
  paso `langflow-init` contra un volumen real.
- Los scripts de PowerShell no se ejecutaron en Windows; se revisaron a mano.
- `docker compose config` y `pytest` se corrieron en local; su salida está en el estado del
  cambio.

## Pendiente

- Probar en un equipo Windows limpio con Docker Desktop y WSL 2: arranque, montaje de una
  carpeta y apagado.
- Probar en macOS que un volumen `langflow-datos` previo, creado como root, queda utilizable
  tras `langflow-init` sin borrarlo.
- Decidir si `levantar_sandboxes_guiado.sh` del curso necesita versión para Windows.
