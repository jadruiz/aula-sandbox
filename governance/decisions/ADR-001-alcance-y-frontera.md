---
status: accepted
date: 2026-08-19
deciders: José Ruiz (anchor); pendiente visto bueno de seguridad para el piloto
---

# ADR-001: alcance del aula-sandbox y frontera con asilo-sandbox

## Contexto

El curso arranca el 2026-08-20 con perfiles que no programan (Ruta B) y equipos
heterogéneos. `asilo-sandbox` —el entorno contenido del workspace— está bloqueado por
diseño hasta cerrar SB-01/SB-02 (launcher dentro del montaje RW, `source .env`), y su
modelo de amenazas es el de un **agente autónomo con acceso a archivos del host**. Esperar
ese hardening dejaría al curso sin entorno; desbloquearlo a la carrera traicionaría su
propio plan.

## Decisión

Crear un repo hermano con un alcance deliberadamente menor: **empaquetar herramientas,
no aislar agentes**.

1. Lo que corre dentro es JupyterLab, LangFlow, Redis y Letta; el código lo escribe y
   dispara el estudiante. No hay Agente Cero ni launcher auto-modificable: los scripts de
   arranque viven en `scripts/`, fuera del montaje `trabajo/`.
2. Único montaje: `trabajo/`. Puertos solo en `127.0.0.1`. Proceso no-root. Sin secretos
   en la imagen.
3. Jupyter corre **sin token**: la superficie de acceso es el loopback de la máquina del
   estudiante; un token compartido en pizarra daría seguridad teatral, no real.
4. Credenciales: clave **desechable con tope de gasto** en `.env` no versionado. Se acepta
   `env_file` (compose lo parsea como datos, no lo ejecuta como shell — a diferencia del
   `source .env` que bloqueó a asilo-sandbox).
5. Versiones: sin pins en el Dockerfile; el artefacto congelado es la **imagen** que el
   instructor construye y reparte antes de la sesión 1 (`pip freeze` queda dentro como
   evidencia). Pinnear números no verificables rompería builds; repartir la imagen da
   bits idénticos, que es lo que el axioma persigue.

## Qué NO promete

Aislamiento fuerte, protección contra código malicioso ejecutado por el propio estudiante,
ni contención de un agente con permisos amplios. Cuando `asilo-sandbox` cierre sus puertas
de seguridad, su perfil `course-restricted` (ADR-002 de aquel repo) podrá absorber este
caso de uso; hasta entonces las dos piezas no se mezclan.

## Consecuencias

Dos imágenes que mantener en el workspace, pero ninguna promesa de seguridad falsa. El
curso obtiene un entorno reproducible mañana; asilo-sandbox conserva su bloqueo íntegro.
