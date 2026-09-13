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

## Verificación en macOS, misma fecha

Con OrbStack activo, `docker compose up -d --build` sobre `trabajo/`:

| Comprobación | Resultado |
|---|---|
| `langflow-init` | termina con código 0; el volumen queda `1000:0 775` |
| LangFlow `/health_check` | 200 a los 3 s de arrancar |
| `/api/v1/auto_login` | 200 con token: sin pantalla de login |
| `secret_key` y `alembic/` en el volumen | escritos por UID 1000 |
| errores de permiso en los logs de LangFlow | ninguno |
| JupyterLab `/lab` | 200 |
| ruta de reparación | volumen forzado a `0:0 755` con `secret_key` `0:0 600`; tras `compose up` el init lo devolvió a `1000:0` y LangFlow volvió a 200 en 15 s conservando la misma llave |

Scripts de Windows, en un contenedor oficial de PowerShell (`lts-debian-12`, amd64): los
cuatro `.ps1` parsean sin errores y `validar_carpeta.ps1` acepta una subcarpeta limpia y
rechaza el perfil de usuario, un padre del perfil, una carpeta con `.env` y una ruta
inexistente.

## Qué sigue sin verificar

- Los `.bat` y el selector de carpeta en un Windows real con Docker Desktop y WSL 2; el
  contenedor de PowerShell prueba sintaxis y lógica, no el doble clic ni el diálogo.

## Pin de imágenes, 2026-09-13

Causa raíz de ambas fallas: `langflowai/langflow:latest` movió a 1.12.1. Se fijan por tag y
digest multi-arquitectura, verificados contra Docker Hub:

| Servicio | Imagen fijada |
|---|---|
| langflow | `1.12.1@sha256:3e3cac65…` (la que ya corría y pasó la verificación de arriba) |
| letta | `0.32.3@sha256:d27a77f3…` (mismo digest que `latest` ese día) |
| flowise | `3.1.4@sha256:3922767a…` (última release; `latest` apuntaba a un build sin tag) |

Un test impide reintroducir `:latest`. Subir de versión es una decisión de curso.

## Pendiente

- Prueba en un equipo Windows limpio con la guía `docs/PRUEBA-WINDOWS.md`.
- Decidir si `levantar_sandboxes_guiado.sh` del curso necesita versión para Windows.
