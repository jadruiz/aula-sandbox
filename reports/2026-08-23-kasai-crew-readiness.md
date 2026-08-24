# Readiness de Aula para Kasai Crew — 2026-08-23

## Resultado

**Runtime y topología real verificados; ejecución distribuible todavía bloqueada.** La imagen
construye e importa CrewAI como usuario no-root, con red desactivada y raíz read-only. Además,
construyó los cuatro agentes y cuatro tareas de Kasai Crew con su guardrail real, sin `kickoff` ni
credenciales. Todavía no consume una release de `kasai-crew` ni prueba el formato portable E2E.

La imagen `lab` sí se construyó y se arrancaron contenedores efímeros de smoke. **No** se levantó
la pila persistente completa con `docker compose up`; LangFlow, Redis, Letta y Flowise no forman
parte de esta verificación. Tampoco hubo llamada de modelo, proveedor simulado, API, clave o gasto.

## Registro exacto de ejecución

| Actividad | Ejecutada | Resultado |
|---|---:|---|
| Build de `kasailabs/aula-sandbox:dev` | sí | imagen creada e imports base verdes |
| Contenedor con red apagada/rootfs read-only | sí | UID 1000; workspace vacío; imports verdes |
| Topología Kasai Crew desde source read-only | sí | 4 agentes, 4 tareas y guardrail; sin `kickoff` |
| `docker compose config` | sí | configuración resolvió |
| `docker compose up` de lab/langflow/redis | no | no verificado en este corte |
| Perfiles Letta/Flowise | no | no verificados |
| Wheel/release de Kasai Crew | no existe | distribución bloqueada |
| Bundle portable E2E | no | pendiente |
| Fake provider/API real | no | cero red, credencial y gasto |

## Lo reutilizable

- Imagen Python 3.12 con CrewAI y herramientas del curso.
- Extra LiteLLM declarado para rutas OpenRouter/multiproveedor y smoke de la API base durante build.
- `/workspace` como único bind mount del host del servicio `lab`; `/tmp` es tmpfs efímero.
- `XDG_DATA_HOME`/cache de CrewAI en tmpfs `/tmp`, nunca en `$HOME` ni el bundle.
- Credenciales por `env_file`, fuera de las capas de imagen.
- Puertos publicados solo en `127.0.0.1`.

## Gaps

| Gap | Riesgo | Cierre |
|---|---|---|
| `kasai-crew` sin wheel publicada | copiar source crea acoplamiento y build no reproducible | release con hash y smoke |
| distribución de Kasai Crew no probada | el smoke monta source revisado, no una wheel con hash | fixture desde release en imagen congelada |
| bundle contiene texto | fuga si se versiona o retiene sin política | ignore, permisos, TTL/borrado |
| `.env` visible al proceso | una dependencia comprometida puede leer claves | clave revocable; luego broker/ASILO |
| sin hard cap local de USD | confirmación no evita sobreconsumo | límite en gateway/proveedor |
| compose normal no reproduce el smoke endurecido | rootfs/red/capabilities quedan más abiertos | perfil explícito read-only, cap-drop, no-new-privileges y límites |
| pip e imágenes auxiliares sin lock/digest | build/tag puede cambiar sin revisión | lock/hash, digest, SBOM, firma/provenance |
| un mismo `.env` puede llegar a varios servicios | aumenta el conjunto de procesos con credencial | secretos mínimos por servicio/perfil |
| Jupyter sin token | loopback evita exposición del salón, no procesos locales maliciosos | autenticación local o threat acceptance explícita |
| volúmenes nombrados auxiliares | flujos/memoria persisten fuera de `trabajo/` | inventario, retención y exclusión del perfil restringido |

## Qué falló y qué se cambió

Los primeros smokes read-only revelaron escrituras de importación:

1. componentes compatibles con XDG creaban data/cache;
2. CrewAI 1.15.x ignoraba XDG para su token manager/listener y escribía en
   `~/.local/share/crewai/credentials`.

Se configuraron `XDG_DATA_HOME` y `XDG_CACHE_HOME` bajo `/tmp`, se convirtió
`/home/aula/.local/share` en un symlink de imagen hacia `/tmp` y se agregó tmpfs de 256 MiB al
servicio `lab`. También se instaló el extra LiteLLM, se añadió import smoke en build y se guardó
`pip freeze`.

Estos cambios corrigen la persistencia observada en esa versión. No son una certificación general:
otra dependencia o actualización puede escribir en otra ruta, por lo que el smoke read-only debe
ser una regresión de release.

## Evidencia de imagen

- ID final: `sha256:cfe8c73e2f9ef551759775112edeb845c4c25bee52ca32f60e3ad5d1c7223ec4`.
- Usuario configurado: `aula`.
- Tamaño observado: 630,866,542 bytes.
- Versiones del build: CrewAI 1.15.17 y LiteLLM 1.98.0.
- Los dos primeros smokes read-only detectaron dos rutas implícitas: appdirs respetó XDG, pero el
  token manager de CrewAI 1.15.x no. La imagen redirige ambas a `/tmp`.
- Smoke final: red desactivada, root filesystem read-only, UID 1000, imports base aprobados; sólo
  permanecen los tres dotfiles creados por `useradd` en HOME y `/workspace` queda vacío.
- Smoke de topología: CrewAI 1.15.17 aceptó el guardrail y construyó cuatro agentes/cuatro tareas
  desde source read-only, sin `kickoff`, proveedor, credencial ni llamada de red.

## Recomendación

Usar Aula primero para validar el runner y un proveedor simulado. Mantener las corridas reales en
revisión humana hasta que el perfil endurecido de `asilo-sandbox` cierre launcher, dotenv, egress,
presupuesto y supply chain.

El siguiente gate no usa datos reales: wheel con hash + bundle sintético manipulado + contenedor
sin red/clave. Debe rechazar el tamper antes de construir rutas de modelo. Después se prueba un
proveedor simulado y sólo al final se evalúa una API con cuota y autorización separadas.

La documentación maestra de ubicación, seguridad, gobernanza y metodología vive en el repo hermano:

- `kasai-crew/docs/architecture/PLACEMENT-AND-INTEGRATION.md`
- `kasai-crew/docs/audits/2026-08-23-aula-asilo-integration.md`
- `kasai-crew/docs/security/SECURE-EXECUTION-BASELINE.md`
