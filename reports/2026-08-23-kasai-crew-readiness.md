# Readiness de Aula para Kasai Crew — 2026-08-23

## Resultado

**Runtime y topología real verificados; ejecución distribuible todavía bloqueada.** La imagen
construye e importa CrewAI como usuario no-root, con red desactivada y raíz read-only. Además,
construyó los cuatro agentes y cuatro tareas de Kasai Crew con su guardrail real, sin `kickoff` ni
credenciales. Todavía no consume una release de `kasai-crew` ni prueba el formato portable E2E.

## Lo reutilizable

- Imagen Python 3.12 con CrewAI y herramientas del curso.
- Extra LiteLLM declarado para rutas OpenRouter/multiproveedor y smoke de la API base durante build.
- `/workspace` como único montaje de escritura.
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
