---
status: accepted
date: 2026-08-24
deciders: José Ruiz (anchor)
---

# ADR-003: un workspace explícito, no necesariamente `trabajo/`

## Contexto

La carpeta fija `trabajo/` era sencilla, pero obligaba a copiar proyectos y confundía la
frontera importante —un único bind mount acotado— con un nombre de carpeta. Montar cualquier ruta
sin validación abriría home, raíz, symlinks o secretos.

## Decisión

Mantener `trabajo/` como default y permitir una carpeta elegida explícitamente. Un validador
canónico resuelve la ruta y rechaza raíz, home, padres de home, symlinks y un `.env` dentro del
workspace. Compose recibe la ruta mediante `AULA_WORKSPACE`.

## Consecuencias

- una persona puede montar un proyecto sin moverlo;
- sigue existiendo un único bind mount para `lab`;
- invocar Compose directamente omite validación y queda como operación avanzada consciente;
- montar un repo completo expone su contenido al código del estudiante: no usar esta ruta para el
  perfil restringido de Kasai Crew, que continúa consumiendo sólo bundles.
