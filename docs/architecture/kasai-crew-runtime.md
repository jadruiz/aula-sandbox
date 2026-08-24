# Frontera de ejecución para Kasai Crew

## Decisión

`aula-sandbox` puede aportar el runtime reproducible de CrewAI, pero no se convierte en el
plano de control ni recibe un montaje del árbol completo de Kasai. Existe una sola crew de
ecosistema en `ia-core/kasai-crew`; cada repo conserva Git, instrucciones y validación propios.

## Flujo permitido

```text
host / Agente 0
  repo allowlisted -> plan offline -> bundle portable con hashes
                                      |
                                      v
aula-sandbox/trabajo -> /workspace -> validar bundle -> CrewAI -> propuesta en /workspace
                                                               -> revisión humana
```

1. En el host, `kasai-crew export` abre únicamente los archivos declarados en `inputs`.
2. El export bloquea clasificaciones `restricted`/`secret`, ausencia de opt-in y patrones de
   secreto conocidos. Elimina rutas absolutas, pero conserva texto, hash y snapshot Git relativo.
3. La persona copia el bundle a `trabajo/`; ese sigue siendo el único bind mount del host.
4. El runner recalcula tamaño y SHA-256 antes de llamar un modelo.
5. La salida es una propuesta para revisión. Aula no escribe, hace commit ni publica en el repo
   de origen.

## Prohibiciones

- No montar `Code/`, `$HOME`, `.ssh`, sockets de Docker ni carpetas padre.
- No copiar cookies o sesiones de ChatGPT, Claude, Gemini, Copilot o Codex al contenedor.
- No hornear claves, bundles ni source privado dentro de la imagen.
- No instalar una copia de la crew dentro de cada repo.
- No presentar Docker/Aula como aislamiento fuerte.

CrewAI crea un directorio de datos durante el import aun con memoria desactivada. La imagen fija
`XDG_DATA_HOME` y `XDG_CACHE_HOME` bajo el tmpfs `/tmp`; ese estado es efímero y no contamina
`trabajo/` ni el expediente. En 1.15.x, el listener también crea una clave bajo
`~/.local/share/crewai/credentials` sin respetar XDG; la imagen hace esa subruta un symlink
inmutable a `/tmp`. `trabajo/` sigue siendo el único bind mount del host.

## Estado real al 2026-08-23

- Aula instala e importa CrewAI 1.15.17/LiteLLM 1.98.0 como UID 1000 en smoke sin red/read-only.
  La topología real de Kasai Crew (cuatro agentes, cuatro tareas y guardrail) también construye sin
  `kickoff`; `kasai-crew` todavía no tiene release/wheel distribuida.
- El bundle y su validación están implementados y probados offline en el repo hermano.
- La imagen tiene smoke de compatibilidad desde source read-only, pero no desde una wheel firmada.
- Una corrida externa exige API/gateway independiente; una suscripción de chat no se trata como
  credencial programática.
- Se construyó y arrancó la imagen `lab` en contenedores efímeros; no se ejecutó
  `docker compose up` de la pila completa ni se probaron LangFlow/Redis/Letta/Flowise.
- “Único montaje” significa único **bind mount del host para `lab`**. Los servicios auxiliares
  declaran volúmenes nombrados y no pertenecen automáticamente al perfil restringido.

## Gates para habilitar el perfil

- [ ] Release revisada y wheel con hash de `kasai-crew`.
- [x] Imagen reconstruida y `versiones-instaladas.txt` incluido; falta archivar el freeze junto a
  una release distribuida.
- [ ] Smoke offline: importar, validar bundle alterado y comprobar fail-closed.
- [ ] Proveedor simulado: cero llamadas y cero coste real.
- [ ] Prueba E2E: ningún path del repo origen visible en el contenedor.
- [ ] Política de retención/borrado para bundles y logs.
- [ ] Tope de gasto efectivo en gateway/proveedor; `max_cost_usd` local no basta.

Hasta cerrar estos gates, Aula es un destino de arquitectura y desarrollo, no una ruta de
producción del ecosistema.
