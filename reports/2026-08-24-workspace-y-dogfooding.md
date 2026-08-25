# Aula — workspace explícito y dogfooding

## TL;DR

Aula ya permite elegir una carpeta sin copiarla ni editar Compose. El gate rechaza rutas amplias,
symlinks y `.env`. Cuatro tests y la configuración estática pasan; además, la imagen local ejecutó
un smoke efímero como UID 1000, sin red y escribiendo sólo en el bind temporal.

## Qué cambió

- `AULA_WORKSPACE` alimenta el único bind `/workspace`; `trabajo/` sigue como default.
- Un validador común sirve a terminal y doble clic; Finder tiene selector propio.
- Se documentó bundle de Kasai Crew frente a montaje del repo origen.
- `src/` y `docs/asilo/` tienen función real y el perfil MILPA dejó de tener gaps.
- README, Quickstart, índice y diagramas van de orientación a implementación.

## Evidencia 2026-08-24

```text
pytest: 4 passed
docker compose config: OK
bash -n: OK
milpa validate: ok=true, missing=[]
audit-docs: ok=true
imagen: sha256:cfe8c73e2f9ef551759775112edeb845c4c25bee52ca32f60e3ad5d1c7223ec4
smoke: UID 1000 · /workspace · mount-ok
```

El smoke usó flags más estrictos que el Compose normal: `network none`, rootfs read-only,
cap-drop ALL y no-new-privileges. Prueba el montaje y la imagen bajo ese comando, no aislamiento
absoluto ni el stack completo con Jupyter/LangFlow/Redis.

## Riesgo residual

- Jupyter sin token confía en loopback y puede ser alcanzado por procesos locales.
- Compose no aplica todo el hardening del smoke manual.
- La API key entra por entorno a servicios seleccionados; no existe broker.
- Imágenes auxiliares `latest` y build sin lock reproducible permanecen deuda del aula.

## Acción siguiente

Crear un perfil Compose `crew-offline` con un solo servicio, bundle read-only, red `none`, token
local y wheel de Kasai Crew fijada; probar proveedor falso antes de una API real.
