---
status: accepted
date: 2026-08-23
deciders: José Ruiz (anchor); implementación de imagen pendiente de gate
---

# ADR-002: Aula ejecuta bundles; no hospeda una crew por repo

## Contexto

El ecosistema tiene repos Git independientes y necesita investigación, ataque adversarial,
auditoría y síntesis con varios modelos. Montar todo el workspace en Aula ampliaría el alcance de
cualquier prompt injection, clave filtrada o código ejecutado. Duplicar una crew por repo también
fragmentaría prompts, dependencias, presupuesto y observabilidad.

## Decisión

Adoptar un solo plano `kasai-crew`. Agente 0 compila en el host un paquete portátil con evidencia
allowlisted. Aula recibe únicamente ese paquete en `trabajo/`, lo valida y produce una propuesta
sin acceso al repo origen. La crew se instalará desde una wheel revisada cuando exista; no se copia
source de un repo hermano al contexto Docker.

## Consecuencias

- Se conserva AX-02: un único montaje de escritura.
- El control plane y el runtime pueden versionarse y probarse por separado.
- El bundle contiene evidencia y requiere la misma clasificación/retención que su contenido.
- La implementación E2E queda bloqueada hasta una release instalable y un proveedor simulado.
- Los casos con datos regulados, otra autoridad o credenciales aisladas pueden exigir otra crew o
  `asilo-sandbox`, pero eso requiere un ADR propio.
