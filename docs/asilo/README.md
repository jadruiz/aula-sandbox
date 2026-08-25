# Adopción ASILO en Aula

## TL;DR

Aula aplica un perfil educativo de contención parcial: usuario no-root, un workspace explícito,
puertos loopback y estado efímero. No se presenta como aislamiento fuerte ni hereda el estado de
`asilo-sandbox`.

| Control | Estado | Evidencia |
|---|---|---|
| único bind mount del host | implementado en Compose; validación en launcher | `tests/test_workspace_mount.py` |
| rechazo de raíz, home y symlink | implementado | `scripts/validar_carpeta.sh` |
| secretos fuera del workspace | parcial; validador rechaza `.env` en carpeta elegida | prueba negativa |
| proceso no-root | configurado en imagen | Dockerfile; falta E2E multiplataforma |
| puertos sólo loopback | configurado | Compose |
| aislamiento fuerte | no implementado | fuera del alcance de Aula |

Las excepciones, amenazas y riesgo residual viven en ADR-001 y en la documentación de
arquitectura; esta página no redefine la metodología.
